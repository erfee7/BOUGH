from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

# --- Request Models ---

class ConversationCreate(BaseModel):
    title: Optional[str] = None
    system_prompt: Optional[str] = None

# --- Response Models ---

class MessageResponse(BaseModel):
    id: uuid.UUID
    parent_id: Optional[uuid.UUID] = None
    role: str
    content: Optional[str] = None
    status: str
    generation_config: Optional[dict] = None
    metadata: Optional[dict]= None
    created_at: datetime

class ConversationResponse(BaseModel):
    id: uuid.UUID
    title: Optional[str] = None
    active_leaf_id: Optional[uuid.UUID] = None
    created_at: datetime

class ConversationCreateResponse(BaseModel):
    conversation: ConversationResponse
    root_message_id: uuid.UUID

class ConversationDetailResponse(BaseModel):
    conversation: ConversationResponse
    messages: list[MessageResponse]

