import uuid
import pytest
import httpx
from httpx import ASGITransport
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from app.main import app
from app.security import get_current_user_id
from app.db import users as db_users
from app.db.connection import get_pool

_TEST_USERNAME = "testuser"
_TEST_PASSWORD = "testpassword123"
_TEST_HASH = "dummy_hash"

@pytest.mark.asyncio
async def test_login_success(mock_pool):
    """Tests successful login, cookie setting, and user return."""
    # Create a user in the transactional DB
    user_id = await db_users.create_user(
        username=_TEST_USERNAME, 
        password_hash=_TEST_HASH, 
        conn=mock_pool.conn
    )
    
    with patch('app.db.connection.get_pool', return_value=mock_pool), \
         patch('app.routers.auth.verify_password', return_value=True):
        
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            payload = {"username": _TEST_USERNAME, "password": _TEST_PASSWORD}
            response = await client.post("/api/auth/login", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["id"] == str(user_id)
            assert data["username"] == _TEST_USERNAME
            assert data["is_active"] is True
            
            # Verify the cookie is set
            cookies = response.headers.get("set-cookie")
            assert cookies is not None
            assert "session_id=" in cookies
            assert "HttpOnly" in cookies

@pytest.mark.asyncio
async def test_login_wrong_password(mock_pool):
    """Tests that login fails with wrong password."""
    await db_users.create_user(username=_TEST_USERNAME, password_hash=_TEST_HASH, conn=mock_pool.conn)
    
    with patch('app.db.connection.get_pool', return_value=mock_pool), \
         patch('app.routers.auth.verify_password', return_value=False): # Simulate wrong password
        
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            payload = {"username": _TEST_USERNAME, "password": "wrongpassword"}
            response = await client.post("/api/auth/login", json=payload)
            
            assert response.status_code == 401
            assert response.json()["detail"] == "Incorrect username or password"

@pytest.mark.asyncio
async def test_login_inactive_user(mock_pool):
    """Tests that an inactive user cannot log in."""
    user_id = await db_users.create_user(username="inactive", password_hash=_TEST_HASH, conn=mock_pool.conn)
    await db_users.set_user_active_status(user_id, is_active=False, conn=mock_pool.conn)
    
    with patch('app.db.connection.get_pool', return_value=mock_pool), \
         patch('app.routers.auth.verify_password', return_value=True):
        
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            payload = {"username": "inactive", "password": "any"}
            response = await client.post("/api/auth/login", json=payload)
            
            assert response.status_code == 401
            assert response.json()["detail"] == "Account is disabled"

@pytest.mark.asyncio
async def test_logout_clears_cookie(mock_pool):
    """Tests that logout deletes the session and clears the cookie."""
    user_id = await db_users.create_user(username="logout_user", password_hash=_TEST_HASH, conn=mock_pool.conn)
    session_id = await db_users.create_session(user_id, expires_at=datetime.now(timezone.utc) + timedelta(days=1), conn=mock_pool.conn)
    
    with patch('app.db.connection.get_pool', return_value=mock_pool):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/auth/logout", cookies={"session_id": str(session_id)})
            
            assert response.status_code == 200
            
            # Verify cookie is cleared in response
            cookies = response.headers.get("set-cookie")
            assert "session_id=" in cookies
            assert "Max-Age=0" in cookies or "expires=Thu, 01 Jan 1970" in cookies.lower()
            
            # Verify session is deleted from DB
            db_session = await db_users.fetch_session(session_id, conn=mock_pool.conn)
            assert db_session is None

@pytest.mark.asyncio
async def test_me_endpoint_unauthenticated():
    """Tests that /me fails without a cookie."""
    # Temporarily remove the autouse auth bypass to test the real 401 behavior
    app.dependency_overrides.pop(get_current_user_id, None)
    
    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/auth/me")
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_me_endpoint_authenticated(mock_pool):
    """Tests /me with a mocked authenticated user ID that exists in DB."""
    user_id = await db_users.create_user(username="me_user", password_hash=_TEST_HASH, conn=mock_pool.conn)
    app.dependency_overrides[get_current_user_id] = lambda: user_id
    
    try:
        with patch('app.db.connection.get_pool', return_value=mock_pool):
            async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get("/api/auth/me")
                
                assert response.status_code == 200
                data = response.json()
                assert data["username"] == "me_user"
    finally:
        # Clean up override
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_change_password(mock_pool):
    """Tests changing password keeps current session and kills others."""
    user_id = await db_users.create_user(username="pwd_changer", password_hash="old_hash", conn=mock_pool.conn)
    
    # Create current session (the one making the request)
    current_session_id = await db_users.create_session(user_id, expires_at=datetime.now(timezone.utc) + timedelta(days=1), conn=mock_pool.conn)
    # Create another session that should be killed
    other_session_id = await db_users.create_session(user_id, expires_at=datetime.now(timezone.utc) + timedelta(days=1), conn=mock_pool.conn)
    
    app.dependency_overrides[get_current_user_id] = lambda: user_id
    
    try:
        with patch('app.db.connection.get_pool', return_value=mock_pool), \
             patch('app.routers.auth.verify_password', return_value=True), \
             patch('app.routers.auth.hash_password', return_value="new_hash"):
            
            async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                payload = {"old_password": "old", "new_password": "new"}
                response = await client.post(
                    "/api/auth/change-password", 
                    json=payload,
                    cookies={"session_id": str(current_session_id)}
                )
                
                assert response.status_code == 200
                
                # Verify password was updated in DB
                db_user = await db_users.fetch_user_by_id(user_id, conn=mock_pool.conn)
                assert db_user['password_hash'] == "new_hash"
                
                # Verify current session is kept
                current_db_session = await db_users.fetch_session(current_session_id, conn=mock_pool.conn)
                assert current_db_session is not None
                
                # Verify other session was deleted
                other_db_session = await db_users.fetch_session(other_session_id, conn=mock_pool.conn)
                assert other_db_session is None
    finally:
        app.dependency_overrides.clear()