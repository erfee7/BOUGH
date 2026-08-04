import uuid
import pytest
import httpx
import asyncio
from httpx import ASGITransport
from unittest.mock import patch, AsyncMock

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
            assert msg['creation_data'] == {"source": "user"}

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
        creation_data = {"source": "user"},
        conn = mock_pool.conn
    )
    await db_conversations.update_conversation(conv_id, active_leaf_id = msg_id, conn = mock_pool.conn)
    
    # Patch the get_pool in database layer to use our transactional FakePool
    with patch('app.db.connection.get_pool', return_value = mock_pool):
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
    with patch('app.db.connection.get_pool', return_value = mock_pool):
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
    with patch('app.db.connection.get_pool', return_value=mock_pool):
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


@pytest.mark.asyncio
async def test_update_conversation_title_endpoint(mock_pool):
    """Tests the PATCH /api/chat/conversations/{id} endpoint for title updates."""
    # Setup: Create a conversation to update
    conv_id = await db_conversations.create_conversation(title="Old Title", conn=mock_pool.conn)
    
    # Patch the get_pool in database layer to use our transactional FakePool
    with patch('app.db.connection.get_pool', return_value=mock_pool):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            payload = {"title": TEST_CONVERSATION_TITLE}
            response = await client.patch(f"/api/chat/conversations/{conv_id}", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            
            # Validate response structure
            assert data["id"] == str(conv_id)
            assert data["title"] == TEST_CONVERSATION_TITLE
            
            # Verify it actually wrote to the DB
            conv = await db_conversations.fetch_conversation(conv_id, conn=mock_pool.conn)
            assert conv is not None
            assert conv['title'] == TEST_CONVERSATION_TITLE

@pytest.mark.asyncio
async def test_update_conversation_title_empty_string(mock_pool):
    """Tests that PATCHing an empty string normalizes to None (Untitled)."""
    conv_id = await db_conversations.create_conversation(title="Old Title", conn=mock_pool.conn)
    
    with patch('app.db.connection.get_pool', return_value=mock_pool):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            payload = {"title": ""}
            response = await client.patch(f"/api/chat/conversations/{conv_id}", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            
            # Should be null in the response
            assert data["title"] is None
            
            # Should be None in the DB
            conv = await db_conversations.fetch_conversation(conv_id, conn=mock_pool.conn)
            assert conv['title'] is None

@pytest.mark.asyncio
async def test_update_conversation_not_found(mock_pool):
    """Tests that PATCHing a non-existent conversation returns 404."""
    with patch('app.db.connection.get_pool', return_value=mock_pool):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            random_id = uuid.uuid4()
            payload = {"title": "Doesn't matter"}
            response = await client.patch(f"/api/chat/conversations/{random_id}", json=payload)
            
            assert response.status_code == 404
            assert response.json()["detail"] == "Conversation not found"

@pytest.mark.asyncio
async def test_update_conversation_title_too_long(mock_pool):
    """Tests that PATCHing a title too long chars returns 422 Validation Error."""
    conv_id = await db_conversations.create_conversation(title="Old Title", conn=mock_pool.conn)
    
    with patch('app.db.connection.get_pool', return_value=mock_pool):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            payload = {"title": "a" * 1729}
            response = await client.patch(f"/api/chat/conversations/{conv_id}", json=payload)
            
            assert response.status_code == 422

@pytest.mark.asyncio
async def test_update_conversation_active_leaf_valid(mock_pool):
    """Tests that PATCHing a valid active_leaf_id (a leaf) succeeds."""
    conv_id = await db_conversations.create_conversation(title="Test", conn=mock_pool.conn)
    root_id = await db_messages.create_message(
        conversation_id=conv_id, role="system", content="sys", 
        status="complete", creation_data={"source": "user"}, conn=mock_pool.conn
    )
    child_id = await db_messages.create_message(
        conversation_id=conv_id, role="user", parent_id=root_id, content="user", 
        status="complete", creation_data={"source": "user"}, conn=mock_pool.conn
    )
    
    with patch('app.db.connection.get_pool', return_value=mock_pool):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            payload = {"active_leaf_id": str(child_id)}
            response = await client.patch(f"/api/chat/conversations/{conv_id}", json=payload)
            
            assert response.status_code == 200
            
            conv = await db_conversations.fetch_conversation(conv_id, conn=mock_pool.conn)
            assert conv['active_leaf_id'] == child_id

@pytest.mark.asyncio
async def test_update_conversation_active_leaf_has_children(mock_pool):
    """Tests that PATCHing an active_leaf_id that has children fails."""
    conv_id = await db_conversations.create_conversation(title="Test", conn=mock_pool.conn)
    root_id = await db_messages.create_message(
        conversation_id=conv_id, role="system", content="sys", 
        status="complete", creation_data={"source": "user"}, conn=mock_pool.conn
    )
    # Root has a child, so it's not a leaf
    await db_messages.create_message(
        conversation_id=conv_id, role="user", parent_id=root_id, content="user", 
        status="complete", creation_data={"source": "user"}, conn=mock_pool.conn
    )
    
    with patch('app.db.connection.get_pool', return_value=mock_pool):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            payload = {"active_leaf_id": str(root_id)}
            response = await client.patch(f"/api/chat/conversations/{conv_id}", json=payload)
            
            assert response.status_code == 400
            assert response.json()["detail"] == "active_leaf_id must be a leaf node (cannot have children)"

@pytest.mark.asyncio
async def test_update_conversation_active_leaf_wrong_conv(mock_pool):
    """Tests that PATCHing an active_leaf_id from another conversation fails."""
    conv1_id = await db_conversations.create_conversation(title="Conv1", conn=mock_pool.conn)
    conv1_root = await db_messages.create_message(
        conversation_id=conv1_id, role="system", content="sys1", 
        status="complete", creation_data={"source": "user"}, conn=mock_pool.conn
    )

    conv2_id = await db_conversations.create_conversation(title="Conv2", conn=mock_pool.conn)
    conv2_root = await db_messages.create_message(
        conversation_id=conv2_id, role="system", content="sys2", 
        status="complete", creation_data={"source": "user"}, conn=mock_pool.conn
    )
    
    with patch('app.db.connection.get_pool', return_value=mock_pool):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            payload = {"active_leaf_id": str(conv2_root)} # Belongs to Conv2
            response = await client.patch(f"/api/chat/conversations/{conv1_id}", json=payload)
            
            assert response.status_code == 400
            assert response.json()["detail"] == "active_leaf_id does not belong to this conversation"

@pytest.mark.asyncio
async def test_update_conversation_active_leaf_null(mock_pool):
    """Tests that PATCHing a null active_leaf_id fails."""
    conv_id = await db_conversations.create_conversation(title="Test", conn=mock_pool.conn)
    await db_messages.create_message(
        conversation_id=conv_id, role="system", content="sys", 
        status="complete", creation_data={"source": "user"}, conn=mock_pool.conn
    )
    
    with patch('app.db.connection.get_pool', return_value=mock_pool):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            payload = {"active_leaf_id": None}
            response = await client.patch(f"/api/chat/conversations/{conv_id}", json=payload)
            
            assert response.status_code == 400
            assert response.json()["detail"] == "active_leaf_id cannot be null"

@pytest.mark.asyncio
async def test_generate_title_endpoint(mock_pool):
    """Tests the POST /api/chat/conversations/{id}/generate-title endpoint."""
    conv_id = await db_conversations.create_conversation(title=None, conn=mock_pool.conn)
    
    # Mock the titler engine so we don't hit the real LLM in router tests
    with patch('app.routers.conversations.titler.generate_title', return_value="Generated Title") as mock_titler:
        with patch('app.db.connection.get_pool', return_value=mock_pool):
            async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                payload = {"force": False}
                response = await client.post(f"/api/chat/conversations/{conv_id}/generate-title", json=payload)
                
                # Assert endpoint responds successfully
                assert response.status_code == 200
                
                # Verify the titler engine was called correctly
                mock_titler.assert_called_once_with(conv_id, force=False)

@pytest.mark.asyncio
async def test_generate_title_conversation_not_found(mock_pool):
    """Tests that generating title for a non-existent conversation returns 404."""
    with patch('app.db.connection.get_pool', return_value=mock_pool):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            random_conv_id = uuid.uuid4()
            payload = {"force": False}
            response = await client.post(f"/api/chat/conversations/{random_conv_id}/generate-title", json=payload)
            
            assert response.status_code == 404
            assert response.json()["detail"] == "Conversation not found"

@pytest.mark.asyncio
async def test_delete_conversation_endpoint_success(mock_pool):
    """Tests DELETE /api/chat/conversations/{id}."""
    conv_id = await db_conversations.create_conversation(title="To Delete", conn=mock_pool.conn)
    
    with patch('app.db.connection.get_pool', return_value=mock_pool):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete(f"/api/chat/conversations/{conv_id}")
            
            assert response.status_code == 204
            
            # Verify it's gone from DB
            result = await db_conversations.fetch_conversation(conv_id, conn=mock_pool.conn)
            assert result is None

@pytest.mark.asyncio
async def test_delete_conversation_endpoint_not_found(mock_pool):
    """Tests 404 when deleting non-existent conversation."""
    with patch('app.db.connection.get_pool', return_value=mock_pool):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            random_id = uuid.uuid4()
            response = await client.delete(f"/api/chat/conversations/{random_id}")
            assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_conversation_cancels_streams(mock_pool):
    """Tests that deleting a conversation cancels active streams."""
    conv_id = await db_conversations.create_conversation(title="Stream Conv", conn=mock_pool.conn)
    root_id = await db_messages.create_message(
        conversation_id=conv_id, role="system", content="Sys", 
        status="complete", creation_data={"source": "user"}, conn=mock_pool.conn
    )
    user_id = await db_messages.create_message(
        conversation_id=conv_id, role="user", parent_id=root_id, content="Hi", 
        status="complete", creation_data={"source": "user"}, conn=mock_pool.conn
    )
    streaming_msg_id = await db_messages.create_message(
        conversation_id=conv_id, role="assistant", parent_id=user_id, content=None, 
        status="streaming", creation_data={"source": "model"}, conn=mock_pool.conn
    )
    
    with patch('app.db.connection.get_pool', return_value=mock_pool):
        with patch('app.routers.conversations.stream_manager.cancel_stream') as mock_cancel:
            async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.delete(f"/api/chat/conversations/{conv_id}")
                
                assert response.status_code == 204
                # Verify cancel_stream was called with the streaming message ID
                mock_cancel.assert_called_once_with(streaming_msg_id)

@pytest.mark.asyncio
async def test_touch_conversation_endpoint(mock_pool):
    """Tests POST /api/chat/conversations/{id}/touch actually updates the timestamp."""
    conv_id = await db_conversations.create_conversation(title="Touch Me", conn=mock_pool.conn)
    
    # 1. Fetch the initial state directly from the DB
    initial_conv = await db_conversations.fetch_conversation(conv_id, conn=mock_pool.conn)
    
    # 2. Wait a moment so clock_timestamp() will be strictly greater
    await asyncio.sleep(0.01)
    
    # 3. Call the API endpoint
    with patch('app.db.connection.get_pool', return_value=mock_pool):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(f"/api/chat/conversations/{conv_id}/touch")
            
            assert response.status_code == 200
            assert response.json()["status"] == "ok"
            
    # 4. Fetch the updated state directly from the DB
    updated_conv = await db_conversations.fetch_conversation(conv_id, conn=mock_pool.conn)
    
    # 5. Assert that the DB function was actually called and the timestamp advanced
    assert updated_conv['updated_at'] > initial_conv['updated_at']

@pytest.mark.asyncio
async def test_touch_conversation_not_found(mock_pool):
    """Tests 404 when touching a non-existent conversation."""
    with patch('app.db.connection.get_pool', return_value=mock_pool):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            random_id = uuid.uuid4()
            response = await client.post(f"/api/chat/conversations/{random_id}/touch")
            assert response.status_code == 404