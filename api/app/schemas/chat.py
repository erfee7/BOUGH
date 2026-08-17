from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Literal
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
    content: str | None = None  # Optional: image-only messages. Router normalizes None -> "" before storage.
    role: Literal['user', 'developer', 'assistant'] = "user"
    attachment_ids: list[uuid.UUID] = []  # User-chosen order is the display/sending order

class MessageGenerateRequest(BaseModel):
    model: str | None = None
    parameters: dict | None = None

class PromptCreateRequest(BaseModel):
    name: str
    content: str
    role: Literal['system', 'developer']
    description: str | None = None

class PromptUpdateRequest(BaseModel):
    name: str | None = None
    content: str | None = None
    role: Literal['system', 'developer'] | None = None
    description: str | None = None

class PresetCreateRequest(BaseModel):
    name: str
    model: str | None = None
    parameters: dict | None = None

class PresetUpdateRequest(BaseModel):
    name: str | None = None
    model: str | None = None
    parameters: dict | None = None

# --- Response Models ---

class MessageResponse(BaseModel):
    id: uuid.UUID
    parent_id: uuid.UUID | None = None
    role: str
    content: str | None = None
    reasoning: str | None = None
    attachments: list[dict] = []
    status: str
    error_data: dict | None = None
    creation_data: dict | None = None
    metadata: dict | None = None
    created_at: datetime

class ConversationResponse(BaseModel):
    id: uuid.UUID
    title: str | None = None
    active_leaf_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime

class PromptResponse(BaseModel):
    id: uuid.UUID
    name: str
    content: str
    role: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime

class PresetResponse(BaseModel):
    id: uuid.UUID
    name: str
    model: str | None = None
    parameters: dict
    created_at: datetime
    updated_at: datetime

class ModelResponse(BaseModel):
    id: str
    name: str

class ConversationCreateRequestResponse(BaseModel):
    conversation: ConversationResponse
    root_message_id: uuid.UUID

class ConversationDetailResponse(BaseModel):
    conversation: ConversationResponse
    messages: list[MessageResponse]

class AttachmentResponse(BaseModel):
    id: uuid.UUID
    mime_type: str
    filename: str
    size: int