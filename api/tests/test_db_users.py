import uuid
import pytest
import asyncpg
from datetime import datetime, timedelta, timezone

from app.db.users import (
    fetch_user_by_username,
    fetch_user_by_id,
    create_user,
    update_password,
    set_user_active_status,
    create_session,
    fetch_session,
    delete_session,
    delete_all_sessions_for_user,
    delete_expired_sessions
)

@pytest.mark.asyncio
async def test_create_and_fetch_user_by_id(db_transaction: asyncpg.Connection):
    """Tests creating a user and fetching it by ID."""
    test_username = "testuser1"
    test_hash = "dummy_hash_123"
    
    user_id = await create_user(
        username=test_username,
        password_hash=test_hash,
        conn=db_transaction
    )
    
    result = await fetch_user_by_id(user_id=user_id, conn=db_transaction)
    
    assert result is not None
    assert isinstance(result, dict)
    assert result['id'] == user_id
    assert result['username'] == test_username
    assert result['password_hash'] == test_hash
    assert result['is_active'] is True

@pytest.mark.asyncio
async def test_fetch_user_by_username(db_transaction: asyncpg.Connection):
    """Tests fetching a user by username."""
    test_username = "testuser2"
    user_id = await create_user(username=test_username, password_hash="hash", conn=db_transaction)
    
    result = await fetch_user_by_username(username=test_username, conn=db_transaction)
    
    assert result is not None
    assert result['id'] == user_id

@pytest.mark.asyncio
async def test_fetch_missing_user(db_transaction: asyncpg.Connection):
    """Tests that fetching a non-existent user returns None."""
    random_uuid = uuid.uuid4()
    result = await fetch_user_by_id(user_id=random_uuid, conn=db_transaction)
    assert result is None
    
    result = await fetch_user_by_username(username="ghost_user", conn=db_transaction)
    assert result is None

@pytest.mark.asyncio
async def test_update_password(db_transaction: asyncpg.Connection):
    """Tests updating a user's password hash."""
    user_id = await create_user(username="pwd_user", password_hash="old_hash", conn=db_transaction)
    
    await update_password(user_id=user_id, new_password_hash="new_hash", conn=db_transaction)
    
    result = await fetch_user_by_id(user_id=user_id, conn=db_transaction)
    assert result['password_hash'] == "new_hash"

@pytest.mark.asyncio
async def test_set_user_active_status(db_transaction: asyncpg.Connection):
    """Tests disabling and enabling a user."""
    user_id = await create_user(username="active_user", password_hash="hash", conn=db_transaction)
    
    # Disable
    await set_user_active_status(user_id=user_id, is_active=False, conn=db_transaction)
    result = await fetch_user_by_id(user_id=user_id, conn=db_transaction)
    assert result['is_active'] is False
    
    # Enable
    await set_user_active_status(user_id=user_id, is_active=True, conn=db_transaction)
    result = await fetch_user_by_id(user_id=user_id, conn=db_transaction)
    assert result['is_active'] is True

@pytest.mark.asyncio
async def test_create_and_fetch_session(db_transaction: asyncpg.Connection):
    """Tests creating and fetching a session."""
    user_id = await create_user(username="session_user", password_hash="hash", conn=db_transaction)
    expires_at = datetime.now(timezone.utc) + timedelta(days=30)
    
    session_id = await create_session(user_id=user_id, expires_at=expires_at, conn=db_transaction)
    
    result = await fetch_session(session_id=session_id, conn=db_transaction)
    
    assert result is not None
    assert isinstance(result, dict)
    assert result['id'] == session_id
    assert result['user_id'] == user_id
    assert result['expires_at'] == expires_at

@pytest.mark.asyncio
async def test_delete_session(db_transaction: asyncpg.Connection):
    """Tests deleting a specific session."""
    user_id = await create_user(username="del_session_user", password_hash="hash", conn=db_transaction)
    session_id = await create_session(user_id=user_id, expires_at=datetime.now(timezone.utc), conn=db_transaction)
    
    await delete_session(session_id=session_id, conn=db_transaction)
    
    result = await fetch_session(session_id=session_id, conn=db_transaction)
    assert result is None

@pytest.mark.asyncio
async def test_delete_all_sessions_for_user(db_transaction: asyncpg.Connection):
    """Tests deleting all sessions for a user, with optional exclusion."""
    user_id = await create_user(username="multi_session_user", password_hash="hash", conn=db_transaction)
    
    session_id_1 = await create_session(user_id=user_id, expires_at=datetime.now(timezone.utc), conn=db_transaction)
    session_id_2 = await create_session(user_id=user_id, expires_at=datetime.now(timezone.utc), conn=db_transaction)
    session_id_3 = await create_session(user_id=user_id, expires_at=datetime.now(timezone.utc), conn=db_transaction)
    
    # Delete all EXCEPT session_id_2
    await delete_all_sessions_for_user(user_id=user_id, exclude_session_id=session_id_2, conn=db_transaction)
    
    assert await fetch_session(session_id=session_id_1, conn=db_transaction) is None
    assert await fetch_session(session_id=session_id_2, conn=db_transaction) is not None # Kept alive
    assert await fetch_session(session_id=session_id_3, conn=db_transaction) is None
    
    # Now delete the rest with no exclusion
    await delete_all_sessions_for_user(user_id=user_id, conn=db_transaction)
    assert await fetch_session(session_id=session_id_2, conn=db_transaction) is None

@pytest.mark.asyncio
async def test_delete_expired_sessions(db_transaction: asyncpg.Connection):
    """Tests that only expired sessions are deleted."""
    user_id = await create_user(username="expiry_user", password_hash="hash", conn=db_transaction)
    
    # Create an expired session
    expired_time = datetime.now(timezone.utc) - timedelta(days=1)
    expired_session_id = await create_session(user_id=user_id, expires_at=expired_time, conn=db_transaction)
    
    # Create an active session
    active_time = datetime.now(timezone.utc) + timedelta(days=1)
    active_session_id = await create_session(user_id=user_id, expires_at=active_time, conn=db_transaction)
    
    # Run the cleanup
    await delete_expired_sessions(conn=db_transaction)
    
    # Check results
    expired_result = await fetch_session(session_id=expired_session_id, conn=db_transaction)
    active_result = await fetch_session(session_id=active_session_id, conn=db_transaction)
    
    assert expired_result is None
    assert active_result is not None