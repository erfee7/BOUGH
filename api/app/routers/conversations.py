import logging
import uuid
from fastapi import APIRouter, HTTPException

from app.db.connection import get_pool
from app.db import conversations as db_conversations
from app.db import messages as db_messages

from app.schemas.chat import (
    ConversationCreate,
    ConversationCreateResponse,
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

@router.post("/conversations", response_model=ConversationCreateResponse)
async def create_conversation(payload: ConversationCreate):
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
                creation_data = {"source": "system_setup"},
                conn = conn
            )
            
            # 3. Set the active leaf to the root message
            await db_conversations.update_conversation(conversation_id, active_leaf_id = message_id, conn = conn)
            
            logger.info("Created conversation %s with root message %s", conversation_id, message_id)

            conv_record = await db_conversations.fetch_conversation(conversation_id, conn = conn)
            
            return ConversationCreateResponse(
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
        
    message_records = await db_messages.fetch_conversation_messages(conversation_id)
      
    return ConversationDetailResponse(
        conversation = ConversationResponse.model_validate(conv_record),
        messages = [MessageResponse.model_validate(msg) for msg in message_records]
    )