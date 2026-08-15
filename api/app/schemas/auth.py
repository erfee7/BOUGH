from pydantic import BaseModel
from datetime import datetime
import uuid

# --- Request Models ---

class LoginRequest(BaseModel):
    username: str
    password: str

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

# --- Response Models ---

class UserResponse(BaseModel):
    id: uuid.UUID
    username: str
    is_active: bool
    created_at: datetime