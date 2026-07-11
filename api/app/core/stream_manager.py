import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from typing import Any, AsyncGenerator

from app.db import messages as db_messages
from app.llm.provider import generate_stream

logger = logging.getLogger(__name__)

@dataclass
class StreamState:
    """Holds the in-memory state of an active LLM generation."""
    message_id: uuid.UUID
    accumulated_content: str = ""
    is_finished: bool = False
    clients: list[asyncio.Queue] = field(default_factory = list)

# Module-level registry for active streams
_active_streams: dict[uuid.UUID, StreamState] = {}

def start_stream(message_id: uuid.UUID, messages_history: list) -> None:
    """Spawns a background task to handle LLM generation and streaming."""
    if message_id in _active_streams:
        logger.warning("Stream for message %s is already active.", message_id)
        return
        
    state = StreamState(message_id = message_id)
    _active_streams[message_id] = state
    
    # Detach the generation from the HTTP request lifecycle
    asyncio.create_task(_run_generation(message_id, messages_history, state))
    logger.info("Started background stream generation for message %s", message_id)

async def get_stream(message_id: uuid.UUID) -> AsyncGenerator[dict[str, Any], None]:
    """
    listens to an active stream. 
    If the stream is active, yields catch-up content followed by live tokens.
    If the stream is not active, returns immediately (API should fallback to DB).
    """
    state = _active_streams.get(message_id)
    if state is None:
        logger.info("No active stream found for message %s. Fallback to DB expected.", message_id)
        return

    # --- ATOMIC BLOCK START ---
    # No 'await' exists here. The event loop cannot switch to the worker 
    # between reading accumulated content and registering the queue.
    catch_up_content = state.accumulated_content
    queue: asyncio.Queue = asyncio.Queue()
    state.clients.append(queue)
    # --- ATOMIC BLOCK END ---

    # 1. Yield accumulated content as a single chunk if any exists
    if catch_up_content:
        yield {"type": "token", "content": catch_up_content}

    # 2. listen for live tokens
    while True:
        item = await queue.get()
        if item is None:
            # End of stream signal from worker
            break
        yield item
        if item.get("type") in ["done", "error"]:
            # Signal the client to close the connection
            break

async def _run_generation(message_id: uuid.UUID, messages_history: list, state: StreamState) -> None:
    """The background worker. Consumes LLM provider events and updates DB/memory."""
    try:
        await db_messages.update_message(message_id, status = 'streaming')
        logger.info("Stream generation started for message %s", message_id)
        
        async for event in generate_stream(messages_history):
            event_type = event.get("type")
            
            if event_type == "token":
                content = event.get("content", "")
                
                # --- ATOMIC BLOCK START ---
                state.accumulated_content += content
                for q in state.clients:
                    q.put_nowait(event)
                # --- ATOMIC BLOCK END ---
                    
            elif event_type == "done":
                metadata = event.get("metadata", {})
                await db_messages.update_message(
                    message_id, 
                    status = 'complete', 
                    content = state.accumulated_content, 
                    metadata = metadata
                )
                state.is_finished = True
                # Broadcast the done event to all listeners
                for q in state.clients:
                    q.put_nowait(event)
                break
                
            elif event_type == "error":
                error_data = event.get("error_data", {})
                await db_messages.update_message(
                    message_id, 
                    status = 'error', 
                    content = state.accumulated_content, 
                    error_data = error_data
                )
                state.is_finished = True
                # Broadcast the error event to all listeners
                for q in state.clients:
                    q.put_nowait(event)
                break
                
    except Exception as e:
        logger.error("Unexpected error in stream generation for %s: %s", message_id, e)
        await db_messages.update_message(
            message_id, 
            status = 'error', 
            content = state.accumulated_content, 
            error_data = {"message": str(e), "type": type(e).__name__}
        )
        for q in state.clients:
            q.put_nowait({"type": "error", "error_data": {"message": str(e)}})
            
    finally:
        # Cleanup memory: remove the stream state
        if message_id in _active_streams:
            del _active_streams[message_id]
            
        # Signal all remaining listeners to close their HTTP connections
        for q in state.clients:
            q.put_nowait(None)
            
        logger.info("Stream generation cleaned up for message %s", message_id)