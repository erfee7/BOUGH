import uuid
import pytest
import httpx
from httpx import ASGITransport
from unittest.mock import patch
import asyncio

from app.main import app
from app.db import conversations as db_conversations
from app.db import messages as db_messages

TEST_CONVERSATION_TITLE = "Conv API Test"
TEST_SYSTEM_PROMPT = "You are a test assistant."

@pytest.mark.asyncio
async def test_create_conversation_endpoint(mock_pool):
    """Tests the POST /api/chat/conversations endpoint."""
    # Patch the get_pool in router layer to use our transactional FakePool
    with patch('app.routers.conversations.get_pool', return_value = mock_pool):
        async with httpx.AsyncClient(transport = ASGITransport(app = app), base_url = "http://test") as client:
            payload = {
                "title": TEST_CONVERSATION_TITLE,
                "system_prompt": TEST_SYSTEM_PROMPT
            }
            response = await client.post("/api/chat/conversations", json = payload)
            
            assert response.status_code == 200
            data = response.json()
            
            # Validate response structure
            assert "conversation" in data
            assert data["conversation"]["title"] == TEST_CONVERSATION_TITLE
            assert data["conversation"]["active_leaf_id"] == data["root_message_id"]
            
            # Verify it actually wrote to the DB using the transactional connection
            conv_id = uuid.UUID(data["conversation"]["id"])
            root_msg_id = uuid.UUID(data["root_message_id"])
            
            conv = await db_conversations.fetch_conversation(conv_id, conn = mock_pool.conn)
            assert conv is not None
            assert conv['title'] == TEST_CONVERSATION_TITLE
            assert conv['active_leaf_id'] == root_msg_id
            
            msg = await db_messages.fetch_message(root_msg_id, conn = mock_pool.conn)
            assert msg is not None
            assert msg['role'] == "system"
            assert msg['content'] == TEST_SYSTEM_PROMPT
            assert msg['creation_data'] == {"source": "system_setup"}

@pytest.mark.asyncio
async def test_get_conversation_endpoint(mock_pool):
    """Tests the GET /api/chat/conversations/{id} endpoint."""
    # Setup: Directly insert a conversation and message into our transaction
    conv_id = await db_conversations.create_conversation(title=TEST_CONVERSATION_TITLE, conn = mock_pool.conn)
    msg_id = await db_messages.create_message(
        conversation_id = conv_id,
        role = "system",
        content = TEST_SYSTEM_PROMPT,
        status = "complete",
        creation_data = {"source": "system_setup"},
        conn = mock_pool.conn
    )
    await db_conversations.update_conversation(conv_id, active_leaf_id = msg_id, conn = mock_pool.conn)
    
    # Patch the get_pool in database layer to use our transactional FakePool
    with patch('app.db.conversations.get_pool', return_value = mock_pool), \
         patch('app.db.messages.get_pool', return_value = mock_pool):
        async with httpx.AsyncClient(transport = ASGITransport(app = app), base_url = "http://test") as client:
            response = await client.get(f"/api/chat/conversations/{conv_id}")
            
            assert response.status_code == 200
            data = response.json()
            
            # Validate conversation structure
            assert data["conversation"]["id"] == str(conv_id)
            assert data["conversation"]["title"] == TEST_CONVERSATION_TITLE
            assert data["conversation"]["active_leaf_id"] == str(msg_id)
            
            # Validate messages structure
            assert len(data["messages"]) == 1
            msg = data["messages"][0]
            assert msg["id"] == str(msg_id)
            assert msg["role"] == "system"
            assert msg["content"] == TEST_SYSTEM_PROMPT
            assert msg["status"] == "complete"

@pytest.mark.asyncio
async def test_get_conversation_not_found(mock_pool):
    """Tests that fetching a non-existent conversation returns 404."""
    # Patch the get_pool in database layer to use our transactional FakePool
    with patch('app.db.conversations.get_pool', return_value = mock_pool), \
         patch('app.db.messages.get_pool', return_value = mock_pool):
        async with httpx.AsyncClient(transport = ASGITransport(app = app), base_url = "http://test") as client:
            random_id = uuid.uuid4()
            response = await client.get(f"/api/chat/conversations/{random_id}")
            
            assert response.status_code == 404
            assert response.json()["detail"] == "Conversation not found"

@pytest.mark.asyncio
async def test_list_conversations_endpoint(mock_pool):
    """Tests the GET /api/chat/conversations endpoint."""
    # Setup: Insert directly into DB using the mock_pool's connection
    await db_conversations.create_conversation(title="First", conn=mock_pool.conn)
    await db_conversations.create_conversation(title="Second", conn=mock_pool.conn)
    
    # Action: Call the API
    with patch('app.db.conversations.get_pool', return_value=mock_pool):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/chat/conversations")
            
            assert response.status_code == 200
            data = response.json()
            
            assert isinstance(data, list)
            assert all(isinstance(item, dict) for item in data)  # Enforces no Record type is returned

            assert len(data) == 2

            titles = [c['title'] for c in data]
            assert "First" in titles
            assert "Second" in titles

