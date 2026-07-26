from pydantic import BaseModel, field_validator
from datetime import datetime
import uuid

# --- Request Models ---

class ConversationCreateRequest(BaseModel):
    title: str | None = None
    system_prompt: str | None = None

class ConversationPatchRequest(BaseModel):
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
    
class TitleGenerateRequest(BaseModel):
    force: bool = False

class MessageAppendRequest(BaseModel):
    content: str
    role: str | None = None
    creation_data: dict | None = None

class MessageGenerateRequest(BaseModel):
    model: str | None = None
    parameters: dict | None = None

class PromptCreateRequest(BaseModel):
    name: str
    content: str
    role: str
    description: str | None = None

class PromptUpdateRequest(BaseModel):
    name: str | None = None
    content: str | None = None
    role: str | None = None
    description: str | None = None

# --- Response Models ---

class MessageResponse(BaseModel):
    id: uuid.UUID
    parent_id: uuid.UUID | None = None
    role: str
    content: str | None = None
    status: str
    creation_data: dict | None = None
    metadata: dict | None = None
    created_at: datetime

class ConversationResponse(BaseModel):
    id: uuid.UUID
    title: str | None = None
    active_leaf_id: uuid.UUID | None = None
    created_at: datetime

class PromptResponse(BaseModel):
    id: uuid.UUID
    name: str
    content: str
    role: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime

class ConversationCreateRequestResponse(BaseModel):
    conversation: ConversationResponse
    root_message_id: uuid.UUID

class ConversationDetailResponse(BaseModel):
    conversation: ConversationResponse
    messages: list[MessageResponse]

class MessageIdResponse(BaseModel):
    message_id: uuid.UUID