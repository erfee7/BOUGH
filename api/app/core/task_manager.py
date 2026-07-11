import asyncio
import logging
import uuid
from typing import AsyncGenerator, List, Dict, Any

from app.db.messages import update_message
from app.llm.provider import generate_stream

logger = logging.getLogger(__name__)

# Module-level registry for active background task queues
_task_queues: dict[uuid.UUID, asyncio.Queue] = {}

def start_task(message_id: uuid.UUID, messages_history: List[Dict[str, Any]]) -> None:
    """
    Spawns a background asyncio task to handle LLM generation.
    Returns immediately without blocking.
    """
    queue = asyncio.Queue(maxsize=100)
    _task_queues[message_id] = queue
    
    # Detach the task from the current HTTP request lifecycle
    asyncio.create_task(_run_generation(message_id, messages_history, queue))
    logger.info("Started background LLM generation task for message ID: %s", message_id)

async def get_stream(message_id: uuid.UUID) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Yields events from the task queue as they arrive.
    If the task is not found, raises KeyError.
    """
    if message_id not in _task_queues:
        logger.warning("No active stream found for message ID: %s", message_id)
        raise KeyError(f"No active stream for message {message_id}")
    
    queue = _task_queues[message_id]
    
    while True:
        item = await queue.get()
        if item is None:
            # Sentinel value to signal end of stream
            break
        yield item

async def _run_generation(message_id: uuid.UUID, messages_history: List[Dict[str, Any]], queue: asyncio.Queue) -> None:
    """
    Private background worker. Consumes LLM provider stream, writes to DB, and pushes to queue.
    """
    full_content = ""
    
    try:
        # Mark as streaming in the DB
        await update_message(message_id, status='streaming')
        
        async for event in generate_stream(messages_history):
            event_type = event.get("type")
            
            if event_type == "token":
                content = event["content"]
                full_content += content
                await queue.put(event)
                
            elif event_type == "done":
                metadata = event.get("metadata", {})
                await update_message(message_id, status='complete', content=full_content, metadata=metadata)
                await queue.put(event)
                
            elif event_type == "error":
                error_data = event.get("error_data", {})
                await update_message(message_id, status='error', content=full_content, error_data=error_data)
                await queue.put(event)
                break  # Stop processing on error
                
    except Exception as e:
        # Catch unexpected errors during orchestration (e.g., DB failure)
        logger.error("Unexpected error in _run_generation for message %s: %s", message_id, e)
        error_event = {"type": "error", "error_data": {"message": f"Internal server error: {str(e)}", "type": "InternalError"}}
        await update_message(message_id, status='error', content=full_content, error_data=error_event["error_data"])
        await queue.put(error_event)
        
    finally:
        # Signal the listener to close, and clean up the registry
        await queue.put(None)
        if message_id in _task_queues:
            del _task_queues[message_id]
        logger.info("Background LLM generation task finished for message ID: %s", message_id)