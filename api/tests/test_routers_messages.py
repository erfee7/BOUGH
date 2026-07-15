import json
import uuid
import pytest
import httpx
from httpx import ASGITransport
from unittest.mock import patch, AsyncMock
from app.main import app
from app.db import conversations as db_conversations
from app.db import messages as db_messages

TEST_CONVERSATION_TITLE = "Msg API Test"
TEST_SYSTEM_PROMPT = "You are a test assistant."
TEST_USER_MESSAGE = "User input"
TEST_FINISHED_MESSAGE = "Assistant response"

@pytest.mark.asyncio
async def test_append_message_endpoint(mock_pool):
    """Tests POST /api/chat/messages/{parent_id}/append."""
    # Setup: Create conv and root msg directly in DB
    conv_id = await db_conversations.create_conversation(title=TEST_CONVERSATION_TITLE, conn=mock_pool.conn)
    root_id = await db_messages.create_message(
        conversation_id=conv_id, role="system", content=TEST_SYSTEM_PROMPT, 
        status="complete", creation_data={"source": "system_setup"}, conn=mock_pool.conn
    )
    
    # Action: Call API
    with patch('app.routers.messages.get_pool', return_value=mock_pool):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            payload = {"content": TEST_USER_MESSAGE, "role": "user"}
            response = await client.post(f"/api/chat/messages/{root_id}/append", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            new_msg_id = uuid.UUID(data["message_id"])
            
            # Verify DB
            msg = await db_messages.fetch_message(new_msg_id, conn=mock_pool.conn)
            assert msg['parent_id'] == root_id
            assert msg['role'] == "user"
            assert msg['status'] == "complete"
            assert msg['content'] == TEST_USER_MESSAGE
            assert msg['creation_data'] == {"source": "user_edit"}
            
            conv = await db_conversations.fetch_conversation(conv_id, conn=mock_pool.conn)
            assert conv['active_leaf_id'] == new_msg_id

@pytest.mark.asyncio
async def test_generate_message_endpoint(mock_pool):
    """Tests POST /api/chat/messages/{parent_id}/generate."""
    # Setup: Create conv, root, and user msg
    conv_id = await db_conversations.create_conversation(title=TEST_CONVERSATION_TITLE, conn=mock_pool.conn)
    root_id = await db_messages.create_message(
        conversation_id=conv_id, role="system", content=TEST_SYSTEM_PROMPT, 
        status="complete", creation_data={"source": "system_setup"}, conn=mock_pool.conn
    )
    user_msg_id = await db_messages.create_message(
        conversation_id=conv_id, role="user", parent_id=root_id, content=TEST_USER_MESSAGE,
        status="complete", creation_data={"source": "user_edit"}, conn=mock_pool.conn
    )
    
    # Action: Call API
    with patch('app.routers.messages.get_pool', return_value=mock_pool):
        with patch('app.routers.messages.stream_manager.start_stream') as mock_start:
            async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                payload = {"model": "test-model", "parameters": {"temperature": 0.5}}
                response = await client.post(f"/api/chat/messages/{user_msg_id}/generate", json=payload)
                
                assert response.status_code == 200
                data = response.json()
                asst_id = uuid.UUID(data["message_id"])
                
                # Verify DB
                msg = await db_messages.fetch_message(asst_id, conn=mock_pool.conn)
                assert msg['parent_id'] == user_msg_id
                assert msg['role'] == "assistant"
                assert msg['status'] == "pending"
                assert msg['creation_data']['source'] == "model_response"
                assert msg['creation_data']['model'] == "test-model"
                assert msg['creation_data']['parameters'] == {"temperature": 0.5}
                
                conv = await db_conversations.fetch_conversation(conv_id, conn=mock_pool.conn)
                assert conv['active_leaf_id'] == asst_id
                
                # Verify stream manager was called
                mock_start.assert_called_once()
                
                # call_args[0] is the tuple of positional arguments
                args = mock_start.call_args[0]
                assert args[0] == asst_id  # The assistant message ID
                
                # The second argument is the history list for generation
                history = args[1]
                assert len(history) == 2  # root, user; no assistant
                assert history[0]['role'] == 'system'
                assert history[1]['role'] == 'user'

@pytest.mark.asyncio
async def test_stream_message_endpoint_complete():
    """Tests GET /api/chat/messages/{id}/stream when message is already complete."""
    mock_msg = {
        'id': uuid.uuid4(), 'status': 'complete', 'content': TEST_FINISHED_MESSAGE,
        'metadata': {'tokens': 5}, 'error_data': None
    }
    with patch('app.routers.messages.db_messages.fetch_message', new_callable=AsyncMock, return_value=mock_msg):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/api/chat/messages/{mock_msg['id']}/stream")
            
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
            
            # Parse the SSE chunks
            lines = response.text.strip().split("\n\n")
            assert len(lines) == 2
            assert lines[0] == f'data: {json.dumps({"type": "done", "content": TEST_FINISHED_MESSAGE, "metadata": {"tokens": 5}})}'
            assert lines[1] == "data: [DONE]"

@pytest.mark.asyncio
async def test_stream_message_endpoint_live():
    """Tests GET /api/chat/messages/{id}/stream during live generation."""
    mock_msg = {
        'id': uuid.uuid4(), 'status': 'streaming', 'content': None,
        'metadata': None, 'error_data': None
    }
    
    # Mock the stream manager to yield one token then done
    async def mock_get_stream(msg_id):
        yield {"type": "token", "content": "Live"}
        yield {"type": "done", "metadata": {"tokens": 1}}

    with patch('app.routers.messages.db_messages.fetch_message', new_callable=AsyncMock, return_value=mock_msg):
        with patch('app.routers.messages.stream_manager.get_stream', side_effect=mock_get_stream):
            async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(f"/api/chat/messages/{mock_msg['id']}/stream")
                
                assert response.status_code == 200
                lines = response.text.strip().split("\n\n")
                assert len(lines) == 3
                assert lines[0] == f'data: {json.dumps({"type": "token", "content": "Live"})}'
                assert lines[1] == f'data: {json.dumps({"type": "done", "metadata": {"tokens": 1}})}'
                assert lines[2] == "data: [DONE]"