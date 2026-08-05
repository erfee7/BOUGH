import json
import logging
import os
import uuid
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.db.connection import get_pool
from app.db import conversations as db_conversations
from app.db import messages as db_messages
from app.core import stream_manager
from app.schemas.chat import (
    MessageAppendRequest,
    MessageGenerateRequest,
    MessageIdResponse
)


logger = logging.getLogger(__name__)

router = APIRouter(prefix = "/api/chat", tags = ["messages"])

def _format_sse(data: dict) -> str:
    """Formats a dictionary into a standard Server-Sent Event string."""
    return f"data: {json.dumps(data)}\n\n"

@router.post("/messages/{parent_id}/append", response_model = MessageIdResponse)
async def append_message(parent_id: uuid.UUID, payload: MessageAppendRequest):
    """Appends a new message (e.g., user message) to a parent node."""
    pool = get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            p_msg_record = await db_messages.fetch_message(parent_id, conn = conn)
            if not p_msg_record:
                raise HTTPException(status_code = 404, detail = "Parent message not found")
                
            conversation_id = p_msg_record['conversation_id']

            role = payload.role
            creation_data = {"source": "user"}
            
            new_msg_id = await db_messages.create_message(
                conversation_id = conversation_id,
                role = role,
                parent_id = parent_id,
                content = payload.content,
                status = "complete",
                creation_data = creation_data,
                conn = conn
            )
            
            await db_conversations.update_conversation(conversation_id, active_leaf_id = new_msg_id, conn = conn)
            await db_conversations.touch_conversation(conversation_id, conn = conn)
            
            return MessageIdResponse(message_id = new_msg_id)

@router.post("/messages/{parent_id}/generate", response_model = MessageIdResponse)
async def generate_message(parent_id: uuid.UUID, payload: MessageGenerateRequest):
    """Triggers LLM generation for an assistant message based on the parent's history."""
    pool = get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            p_msg_record = await db_messages.fetch_message(parent_id, conn = conn)
            if not p_msg_record:
                raise HTTPException(status_code = 404, detail = "Parent message not found")

            if p_msg_record['status'] not in ['complete', 'canceled']:
                raise HTTPException(status_code = 400, detail = "Parent message must be 'complete' or 'canceled' to generate a response.")
                
            conversation_id = p_msg_record['conversation_id']
            target_model = payload.model or os.getenv("DEFAULT_MODEL", "openrouter/free")
            
            creation_data = {
                "source": "model",
                "model": target_model,
                "parameters": payload.parameters or {}
            }
            
            # Create the empty assistant message
            assistant_msg_id = await db_messages.create_message(
                conversation_id = conversation_id,
                role = "assistant",
                parent_id = parent_id,
                content = None,
                status = "pending",
                creation_data = creation_data,
                conn = conn
            )
            
            await db_conversations.update_conversation(conversation_id, active_leaf_id = assistant_msg_id, conn = conn)
            await db_conversations.touch_conversation(conversation_id, conn = conn)
            
            # Fetch history from the new assistant message (walks up to root)
            history = await db_messages.fetch_message_history(parent_id, conn = conn)
            
            # Trigger background stream
            stream_manager.start_stream(assistant_msg_id, history)
            
            return MessageIdResponse(message_id = assistant_msg_id)

@router.get("/messages/{message_id}/stream")
async def stream_message(message_id: uuid.UUID):
    """SSE endpoint for streaming message generation. Handles reconnections."""
    
    # Check DB first for current status - do this BEFORE creating StreamingResponse
    msg = await db_messages.fetch_message(message_id)
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    
    async def event_generator():
        if msg['status'] == 'complete':
            yield _format_sse({"type": "done", "content": msg['content'], "reasoning": msg['reasoning'], "metadata": msg['metadata']})
            yield "data: [DONE]\n\n"
            return
            
        if msg['status'] == 'error':
            yield _format_sse({"type": "error", "content": msg['content'], "reasoning": msg['reasoning'], "error_data": msg['error_data']})
            yield "data: [DONE]\n\n"
            return

        if msg['status'] == 'canceled':
            yield _format_sse({"type": "canceled", "content": msg['content'], "reasoning": msg['reasoning']})
            yield "data: [DONE]\n\n"
            return
        
        # If pending or streaming, hook into the stream manager
        async for event in stream_manager.get_stream(message_id):
            if event is None:
                break
            yield _format_sse(event)
            if event.get("type") in ["done", "error"]:
                break
                
        # Stream manager finished, send final terminator
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.post("/messages/{message_id}/cancel")
async def cancel_message(message_id: uuid.UUID):
    """Requests cancellation for an active stream. Idempotent."""
    msg = await db_messages.fetch_message(message_id)
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    
    stream_manager.cancel_stream(message_id)
    
    return {"status": "ok"}