import pytest
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException

from app.security import hash_password, verify_password, get_current_user
from app.db.users import fetch_session, fetch_user_by_id, delete_session

def test_hash_and_verify_password():
    """Tests that hashing and verifying a password works correctly."""
    plain_password = "my_super_secret_password"
    hashed = hash_password(plain_password)
    
    assert hashed != plain_password
    assert verify_password(hashed, plain_password) is True

def test_verify_password_mismatch():
    """Tests that a wrong password fails verification."""
    hashed = hash_password("correct_password")
    assert verify_password(hashed, "wrong_password") is False

def test_verify_password_invalid_hash():
    """Tests that an invalid hash format doesn't crash, just returns False."""
    assert verify_password("not_a_real_hash", "any_password") is False

@pytest.mark.asyncio
async def test_get_current_user_no_cookie():
    """Tests that missing session_id cookie raises 401."""
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(session_id=None)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Not authenticated"

@pytest.mark.asyncio
async def test_get_current_user_invalid_uuid():
    """Tests that a non-UUID string raises 401."""
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(session_id="not-a-uuid")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid session token"

@pytest.mark.asyncio
async def test_get_current_user_session_not_found():
    """Tests that a valid UUID not in DB raises 401."""
    random_uuid = str(uuid.uuid4())
    
    with patch('app.security.db_users.fetch_session', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(session_id=random_uuid)
            
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Session not found"
        mock_fetch.assert_called_once_with(uuid.UUID(random_uuid))

@pytest.mark.asyncio
async def test_get_current_user_expired_session():
    """Tests that an expired session raises 401 and triggers cleanup deletion."""
    random_uuid = str(uuid.uuid4())
    user_id = uuid.uuid4()
    expired_time = datetime.now(timezone.utc) - timedelta(days=1)
    
    mock_session = {
        "id": uuid.UUID(random_uuid),
        "user_id": user_id,
        "expires_at": expired_time,
        "created_at": datetime.now(timezone.utc)
    }
    
    with patch('app.security.db_users.fetch_session', new_callable=AsyncMock) as mock_fetch_session, \
         patch('app.security.db_users.delete_session', new_callable=AsyncMock) as mock_delete_session:
        
        mock_fetch_session.return_value = mock_session
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(session_id=random_uuid)
            
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Session expired"
        # Ensure it cleaned up the expired session
        mock_delete_session.assert_called_once_with(uuid.UUID(random_uuid))

@pytest.mark.asyncio
async def test_get_current_user_inactive_user():
    """Tests that an inactive user raises 401."""
    random_uuid = str(uuid.uuid4())
    user_id = uuid.uuid4()
    future_time = datetime.now(timezone.utc) + timedelta(days=1)
    
    mock_session = {
        "id": uuid.UUID(random_uuid),
        "user_id": user_id,
        "expires_at": future_time,
        "created_at": datetime.now(timezone.utc)
    }
    mock_user = {
        "id": user_id,
        "username": "inactive_user",
        "password_hash": "hash",
        "is_active": False,
        "created_at": datetime.now(timezone.utc)
    }
    
    with patch('app.security.db_users.fetch_session', new_callable=AsyncMock) as mock_fetch_session, \
         patch('app.security.db_users.fetch_user_by_id', new_callable=AsyncMock) as mock_fetch_user:
        
        mock_fetch_session.return_value = mock_session
        mock_fetch_user.return_value = mock_user
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(session_id=random_uuid)
            
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "User inactive or not found"

@pytest.mark.asyncio
async def test_get_current_user_success():
    """Tests that a valid session and active user returns the user dict."""
    random_uuid = str(uuid.uuid4())
    user_id = uuid.uuid4()
    future_time = datetime.now(timezone.utc) + timedelta(days=1)
    
    mock_session = {
        "id": uuid.UUID(random_uuid),
        "user_id": user_id,
        "expires_at": future_time,
        "created_at": datetime.now(timezone.utc)
    }
    mock_user = {
        "id": user_id,
        "username": "active_user",
        "password_hash": "hash",
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    }
    
    with patch('app.security.db_users.fetch_session', new_callable=AsyncMock) as mock_fetch_session, \
         patch('app.security.db_users.fetch_user_by_id', new_callable=AsyncMock) as mock_fetch_user:
        
        mock_fetch_session.return_value = mock_session
        mock_fetch_user.return_value = mock_user
        
        result = await get_current_user(session_id=random_uuid)
        
        assert result == mock_user
        mock_fetch_session.assert_called_once_with(uuid.UUID(random_uuid))
        mock_fetch_user.assert_called_once_with(user_id)