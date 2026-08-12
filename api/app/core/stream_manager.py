import asyncio
import logging
import uuid
import time
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
    accumulated_reasoning: str = ""
    is_finished: bool = False
    cancel_requested: bool = False
    clients: list[asyncio.Queue] = field(default_factory = list)

# Module-level registry for active streams
_active_streams: dict[uuid.UUID, StreamState] = {}

def start_stream(message_id: uuid.UUID, messages_history: list, model: str | None = None, parameters: dict[str, Any] | None = None) -> None:
    """Spawns a background task to handle LLM generation and streaming."""
    if message_id in _active_streams:
        logger.warning("Stream for message %s is already active.", message_id)
        return
        
    state = StreamState(message_id=message_id)
    _active_streams[message_id] = state
    
    # Detach the generation from the HTTP request lifecycle
    asyncio.create_task(_run_generation(message_id, messages_history, state, model, parameters))
    logger.info("Started background stream generation for message %s", message_id)

def cancel_stream(message_id: uuid.UUID) -> bool:
    """Requests cancellation for a specific message stream."""
    state = _active_streams.get(message_id)
    if state and not state.is_finished and not state.cancel_requested:
        state.cancel_requested = True
        return True
    return False

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
    catch_up_reasoning = state.accumulated_reasoning
    queue: asyncio.Queue = asyncio.Queue()
    state.clients.append(queue)
    # --- ATOMIC BLOCK END ---

    # 1. Yield accumulated content and reasoning as a single chunk if any exists
    if catch_up_content or catch_up_reasoning:
        yield {
            "type": "catch_up", 
            "content": catch_up_content,
            "reasoning": catch_up_reasoning
        }

    # 2. listen for live tokens
    while True:
        item = await queue.get()
        if item is None:
            # End of stream signal from worker
            break
        yield item
        if item.get("type") in ["done", "error", "canceled"]:
            # Signal the client to close the connection
            break

async def _run_generation(message_id: uuid.UUID, messages_history: list, state: StreamState, model: str | None = None, parameters: dict[str, Any] | None = None) -> None:
    """The background worker. Consumes LLM provider events and updates DB/memory."""
    start_time = time.time() # Record start time
    
    try:
        await db_messages.update_message(message_id, status='streaming')
        logger.info("Stream generation started for message %s", message_id)
        
        async for event in generate_stream(messages_history, model = model, parameters = parameters):
            # Check for cancellation before processing the chunk
            if state.cancel_requested:
                await db_messages.update_message(
                    message_id, 
                    status='canceled', 
                    content=state.accumulated_content, 
                    reasoning=state.accumulated_reasoning
                )
                state.is_finished = True
                # Broadcast the cancel event to all listeners
                for q in state.clients:
                    q.put_nowait({"type": "canceled"})
                break

            event_type = event.get("type")
            
            if event_type == "token":
                content = event.get("content", "")
                
                # --- ATOMIC BLOCK START ---
                state.accumulated_content += content
                for q in state.clients:
                    q.put_nowait(event)
                # --- ATOMIC BLOCK END ---

            elif event_type == "reasoning":
                content = event.get("content", "")
                
                # --- ATOMIC BLOCK START ---
                state.accumulated_reasoning += content
                for q in state.clients:
                    q.put_nowait(event)
                # --- ATOMIC BLOCK END ---
                    
            elif event_type == "done":
                metadata = event.get("metadata", {})
                
                # Inject our server-side generation time
                generation_time = time.time() - start_time
                metadata["server_metrics"] = {"generation_time": generation_time}
                
                await db_messages.update_message(
                    message_id, 
                    status='complete', 
                    content=state.accumulated_content, 
                    reasoning=state.accumulated_reasoning,
                    metadata=metadata
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
                    status='error', 
                    content=state.accumulated_content, 
                    reasoning=state.accumulated_reasoning,
                    error_data=error_data
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
            status='error', 
            content=state.accumulated_content, 
            reasoning=state.accumulated_reasoning,
            error_data={"message": str(e), "type": type(e).__name__}
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