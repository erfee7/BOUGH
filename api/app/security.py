import logging
import uuid
from datetime import datetime, timedelta, timezone
from fastapi import Cookie, HTTPException, status
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.db import users as db_users

logger = logging.getLogger(__name__)

# Initialize the Argon2 hasher
ph = PasswordHasher()

def hash_password(password: str) -> str:
    """Hashes a plaintext password using Argon2."""
    return ph.hash(password)

def verify_password(password_hash: str, plain_password: str) -> bool:
    """Verifies a plaintext password against an Argon2 hash."""
    try:
        ph.verify(password_hash, plain_password)
        return True
    except VerifyMismatchError:
        return False
    except Exception as e:
        # Catches invalid hash format, etc.
        logger.warning("Password verification error: %s", e)
        return False

async def get_current_user(session_id: str | None = Cookie(None, alias="session_id")) -> dict:
    """
    FastAPI dependency to protect routes. 
    Reads the session_id cookie, validates it against the DB, and returns the user dict.
    """
    if not session_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    try:
        session_uuid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session token")
    
    session = await db_users.fetch_session(session_uuid)
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session not found")
    
    # Check if session is expired
    if session['expires_at'] < datetime.now(timezone.utc):
        await db_users.delete_session(session_uuid) # Clean up expired session
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")
        
    user = await db_users.fetch_user_by_id(session['user_id'])
    if not user or not user['is_active']:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User inactive or not found")
        
    return user

# Helper to create session and return expiry time
async def create_user_session(user_id: uuid.UUID) -> tuple[str, datetime]:
    """Creates a session in the DB and returns the session_id string and expiry datetime."""
    expires_at = datetime.now(timezone.utc) + timedelta(days=30)
    session_id = await db_users.create_session(user_id, expires_at)
    return str(session_id), expires_at