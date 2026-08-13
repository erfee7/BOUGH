import logging
import os
import uuid
from fastapi import APIRouter, HTTPException, Response, Depends, Cookie

from app.security import verify_password, hash_password, get_current_user, create_user_session
from app.db import users as db_users
from app.schemas.auth import LoginRequest, ChangePasswordRequest, UserResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/login", response_model=UserResponse)
async def login(payload: LoginRequest, response: Response):
    """Logs in a user and sets a session cookie."""
    # Lazy cleanup of expired sessions
    await db_users.delete_expired_sessions()
    
    user = await db_users.fetch_user_by_username(payload.username)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    if not user['is_active']:
        raise HTTPException(status_code=401, detail="Account is disabled")
        
    if not verify_password(user['password_hash'], payload.password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    session_id_str, expires_at = await create_user_session(user['id'])
    
    # Determine if cookie should be Secure (HTTPS only)
    secure_cookie = os.getenv("SESSION_COOKIE_SECURE", "False").lower() == "true"
    
    response.set_cookie(
        key="session_id",
        value=session_id_str,
        httponly=True,
        secure=secure_cookie,
        samesite="lax",
        expires=expires_at
    )
    
    logger.info("User %s logged in successfully", user['username'])
    return UserResponse.model_validate(user)

@router.post("/logout")
async def logout(response: Response, session_id: str | None = Cookie(None, alias="session_id")):
    """Logs out the current user by deleting the session and clearing the cookie."""
    if session_id:
        try:
            session_uuid = uuid.UUID(session_id)
            await db_users.delete_session(session_uuid)
        except ValueError:
            pass # Ignore invalid UUID formats on logout
            
    response.delete_cookie(key="session_id")
    return {"status": "ok"}

@router.get("/me", response_model=UserResponse)
async def get_me(user: dict = Depends(get_current_user)):
    """Returns the currently logged-in user's information."""
    return UserResponse.model_validate(user)

@router.post("/change-password", response_model=UserResponse)
async def change_password(
    payload: ChangePasswordRequest, 
    user: dict = Depends(get_current_user),
    session_id: str | None = Cookie(None, alias="session_id")
):
    """Changes the user's password and invalidates other sessions."""
    if not verify_password(user['password_hash'], payload.old_password):
        raise HTTPException(status_code=400, detail="Incorrect current password")
        
    new_hash = hash_password(payload.new_password)
    await db_users.update_password(user['id'], new_hash)
    
    # Delete all other sessions, keeping the current one alive
    current_session_uuid = uuid.UUID(session_id) if session_id else None
    await db_users.delete_all_sessions_for_user(user['id'], exclude_session_id=current_session_uuid)
    
    # Fetch fresh user data to return
    updated_user = await db_users.fetch_user_by_id(user['id'])
    logger.info("User %s changed password", updated_user['username'])
    return UserResponse.model_validate(updated_user)