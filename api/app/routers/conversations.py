import logging
import uuid
from fastapi import APIRouter, HTTPException

from app.db.connection import get_pool
from app.db import conversations as db_conversations
from app.db import messages as db_messages

from app.core import titler
from app.core import stream_manager

from app.schemas.chat import (
    ConversationCreateRequest,
    ConversationPatchRequest,
    TitleGenerateRequest,
    ConversationCreateRequestResponse,
    ConversationDetailResponse,
    ConversationResponse,
    MessageResponse
)


logger = logging.getLogger(__name__)

router = APIRouter(prefix = "/api/chat", tags=["chat"])

@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations():
    """Fetches a list of all conversations for the sidebar."""
    records = await db_conversations.fetch_all_conversations()
    return [ConversationResponse.model_validate(rec) for rec in records]

@router.post("/conversations", response_model=ConversationCreateRequestResponse)
async def create_conversation(payload: ConversationCreateRequest):
    """Creates a new conversation and its root system message."""
    # We explicitly acquire a connection here because we need a transaction
    # to ensure the conversation, message, and active_leaf are all created atomically.
    pool = get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            # 1. Create the conversation
            conversation_id = await db_conversations.create_conversation(title = payload.title, conn = conn)
            
            # 2. Create the root system message
            root_prompt = payload.system_prompt
            message_id = await db_messages.create_message(
                conversation_id = conversation_id,
                role = "system",
                content = root_prompt,
                status = "complete",
                creation_data = {"source": "user"},
                conn = conn
            )
            
            # 3. Set the active leaf to the root message
            await db_conversations.update_conversation(conversation_id, active_leaf_id = message_id, conn = conn)
            
            logger.info("Created conversation %s with root message %s", conversation_id, message_id)

            conv_record = await db_conversations.fetch_conversation(conversation_id, conn = conn)
            
            return ConversationCreateRequestResponse(
                conversation = ConversationResponse.model_validate(conv_record),
                root_message_id = message_id
            )


@router.get("/conversations/{conversation_id}", response_model = ConversationDetailResponse)
async def get_conversation(conversation_id: uuid.UUID):
    """Fetches a conversation and all its messages as a flat list."""
    # No explicit connection acquisition needed. Let the db layer handle it.
    conv_record = await db_conversations.fetch_conversation(conversation_id)
    if not conv_record:
        raise HTTPException(status_code = 404, detail = "Conversation not found")
        
    msg_records = await db_messages.fetch_conversation_messages(conversation_id)
      
    return ConversationDetailResponse(
        conversation = ConversationResponse.model_validate(conv_record),
        messages = [MessageResponse.model_validate(msg) for msg in msg_records]
    )

@router.patch("/conversations/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(conversation_id: uuid.UUID, payload: ConversationPatchRequest):
    """Updates the information of a conversation."""
    record = await db_conversations.fetch_conversation(conversation_id)
    if not record:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Extract only the fields that were actually provided in the request
    update_data = payload.model_dump(exclude_unset=True)
    
    # Validate active_leaf_id if provided in the payload
    if "active_leaf_id" in update_data:
        leaf_id = update_data["active_leaf_id"]
        if leaf_id is None:
            raise HTTPException(status_code=400, detail="active_leaf_id cannot be null")
        
        messages = await db_messages.fetch_conversation_messages(conversation_id)
        msg_ids = {m['id'] for m in messages}
        parent_ids = {m['parent_id'] for m in messages if m['parent_id'] is not None}
        
        if leaf_id not in msg_ids:
            raise HTTPException(status_code=400, detail="active_leaf_id does not belong to this conversation")
        if leaf_id in parent_ids:
            raise HTTPException(status_code=400, detail="active_leaf_id must be a leaf node (cannot have children)")
    
    # If there are fields to update, call the DB layer
    if update_data:
        await db_conversations.update_conversation(conversation_id, **update_data)
    
    # Fetch the updated record and return it
    updated_conv = await db_conversations.fetch_conversation(conversation_id)
    return ConversationResponse.model_validate(updated_conv)

@router.post("/conversations/{conversation_id}/generate-title", response_model=ConversationResponse)
async def generate_conversation_title(conversation_id: uuid.UUID, payload: TitleGenerateRequest):
    """Triggers LLM title generation for a conversation."""
    record = await db_conversations.fetch_conversation(conversation_id)
    if not record:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    new_title = await titler.generate_title(conversation_id, force=payload.force)
    
    # Fetch the updated record to return canonical truth
    updated_conv = await db_conversations.fetch_conversation(conversation_id)
    return ConversationResponse.model_validate(updated_conv)

@router.delete("/conversations/{conversation_id}", status_code=204)
async def delete_conversation(conversation_id: uuid.UUID):
    """Deletes a conversation, cancels any active streams, and cascades messages."""
    record = await db_conversations.fetch_conversation(conversation_id)
    if not record:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    # Find and cancel any active streams before deleting
    messages = await db_messages.fetch_conversation_messages(conversation_id)
    for msg in messages:
        if msg['status'] in ['streaming', 'pending']:
            stream_manager.cancel_stream(msg['id'])
            
    await db_conversations.delete_conversation(conversation_id)
    logger.info("Deleted conversation %s", conversation_id)

@router.post("/conversations/{conversation_id}/touch")
async def touch_conversation(conversation_id: uuid.UUID):
    """Manually bumps the conversation's updated_at timestamp."""
    record = await db_conversations.fetch_conversation(conversation_id)
    if not record:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    await db_conversations.touch_conversation(conversation_id)
    logger.info("Touched conversation %s", conversation_id)
    
    return {"status": "ok"}