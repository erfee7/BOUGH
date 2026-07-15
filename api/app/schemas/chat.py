from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

# --- Request Models ---

class ConversationCreate(BaseModel):
    title: Optional[str] = None
    system_prompt: Optional[str] = None

class MessageAppend(BaseModel):
    content: str
    role: Optional[str] = None
    creation_data: Optional[dict] = None

class MessageGenerate(BaseModel):
    model: Optional[str] = None
    parameters: Optional[dict] = None

# --- Response Models ---

class MessageResponse(BaseModel):
    id: uuid.UUID
    parent_id: Optional[uuid.UUID] = None
    role: str
    content: Optional[str] = None
    status: str
    creation_data: Optional[dict] = None
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

class MessageIdResponse(BaseModel):
    message_id: uuid.UUID