from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
import uuid

# --- Request Models ---

class ConversationCreate(BaseModel):
    title: Optional[str] = None
    system_prompt: Optional[str] = None

class ConversationTitling(BaseModel):
    title: str | None = None
    active_leaf_id: uuid.UUID | None = None

    @field_validator('title')
    @classmethod
    def normalize_title(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if v == "":
                return None
            max_length = 137
            if len(v) > max_length:
                raise ValueError(f"Title must be {max_length} characters or less")
        return v

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