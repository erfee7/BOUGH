import json
import uuid
import pytest
import httpx
import asyncio
from httpx import ASGITransport
from unittest.mock import patch, AsyncMock
from app.main import app
from app.db import conversations as db_conversations
from app.db import messages as db_messages

TEST_CONVERSATION_TITLE = "Msg API Test"
TEST_SYSTEM_PROMPT = "You are a test assistant."
TEST_USER_MESSAGE = "User input"
TEST_ASSISTANT_MESSAGE = "Manual assistant text"
TEST_ERROR_DATA = {'message': 'API Died', 'type': 'APIError'}

@pytest.mark.asyncio
async def test_append_message_endpoint(mock_pool):
    """Tests POST /api/chat/messages/{parent_id}/append."""
    # Setup: Create conv and root msg directly in DB
    conv_id = await db_conversations.create_conversation(title=TEST_CONVERSATION_TITLE, conn=mock_pool.conn)
    root_id = await db_messages.create_message(
        conversation_id=conv_id, role="system", content=TEST_SYSTEM_PROMPT, 
        status="complete", creation_data={"source": "user"}, conn=mock_pool.conn
    )

    # Wait a moment so clock_timestamp() will be strictly greater
    await asyncio.sleep(0.01)
    
    # Action: Call API
    with patch('app.routers.messages.get_pool', return_value=mock_pool):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            payload = {"content": TEST_USER_MESSAGE, "role": "user"}
            response = await client.post(f"/api/chat/messages/{root_id}/append", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            new_msg_id = uuid.UUID(data["id"])
            
            # Verify DB
            msg = await db_messages.fetch_message(new_msg_id, conn=mock_pool.conn)
            assert msg['parent_id'] == root_id
            assert msg['role'] == "user"
            assert msg['status'] == "complete"
            assert msg['content'] == TEST_USER_MESSAGE
            assert msg['creation_data'] == {"source": "user"}
            
            conv = await db_conversations.fetch_conversation(conv_id, conn=mock_pool.conn)
            assert conv['active_leaf_id'] == new_msg_id
            assert conv['updated_at'] > conv['created_at']

@pytest.mark.asyncio
async def test_append_message_assistant_role(mock_pool):
    """Tests appending an assistant message (e.g., manual edit)."""
    conv_id = await db_conversations.create_conversation(title=TEST_CONVERSATION_TITLE, conn=mock_pool.conn)
    root_id = await db_messages.create_message(
        conversation_id=conv_id, role="system", content=TEST_SYSTEM_PROMPT, 
        status="complete", creation_data={"source": "user"}, conn=mock_pool.conn
    )
    
    with patch('app.routers.messages.get_pool', return_value=mock_pool):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            payload = {"content": TEST_ASSISTANT_MESSAGE, "role": "assistant"}
            response = await client.post(f"/api/chat/messages/{root_id}/append", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            new_msg_id = uuid.UUID(data["id"])
            
            msg = await db_messages.fetch_message(new_msg_id, conn=mock_pool.conn)
            assert msg['role'] == "assistant"
            assert msg['content'] == TEST_ASSISTANT_MESSAGE
            assert msg['creation_data'] == {"source": "user"}

@pytest.mark.asyncio
async def test_append_message_invalid_role(mock_pool):
    """Tests that appending a message with an invalid role returns 422."""
    conv_id = await db_conversations.create_conversation(title=TEST_CONVERSATION_TITLE, conn=mock_pool.conn)
    root_id = await db_messages.create_message(
        conversation_id=conv_id, role="system", content=TEST_SYSTEM_PROMPT, 
        status="complete", creation_data={"source": "user"}, conn=mock_pool.conn
    )
    
    with patch('app.routers.messages.get_pool', return_value=mock_pool):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            payload = {"content": "Test", "role": "system"} # 'system' is forbidden for append
            response = await client.post(f"/api/chat/messages/{root_id}/append", json=payload)
            assert response.status_code == 422

@pytest.mark.asyncio
async def test_append_message_parent_not_found(mock_pool):
    """Tests that appending to a non-existent parent message returns 404."""
    with patch('app.routers.messages.get_pool', return_value=mock_pool):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            random_parent_id = uuid.uuid4()
            payload = {"content": "Test", "role": "user"}
            response = await client.post(f"/api/chat/messages/{random_parent_id}/append", json=payload)
            
            assert response.status_code == 404
            assert response.json()["detail"] == "Parent message not found"

@pytest.mark.asyncio
async def test_generate_message_endpoint(mock_pool):
    """Tests POST /api/chat/messages/{parent_id}/generate."""
    # Setup: Create conv, root, and user msg
    conv_id = await db_conversations.create_conversation(title=TEST_CONVERSATION_TITLE, conn=mock_pool.conn)
    root_id = await db_messages.create_message(
        conversation_id=conv_id, role="system", content=TEST_SYSTEM_PROMPT, 
        status="complete", creation_data={"source": "user"}, conn=mock_pool.conn
    )
    user_msg_id = await db_messages.create_message(
        conversation_id=conv_id, role="user", parent_id=root_id, content=TEST_USER_MESSAGE,
        status="complete", creation_data={"source": "user"}, conn=mock_pool.conn
    )

    # Wait so that update time will be later than create time
    await asyncio.sleep(0.01)
    
    # Action: Call API
    with patch('app.routers.messages.get_pool', return_value=mock_pool):
        with patch('app.routers.messages.stream_manager.start_stream') as mock_start:
            async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                payload = {"model": "test-model", "parameters": {"temperature": 0.5}}
                response = await client.post(f"/api/chat/messages/{user_msg_id}/generate", json=payload)
                
                assert response.status_code == 200
                data = response.json()
                asst_id = uuid.UUID(data["id"])
                
                # Verify DB
                msg = await db_messages.fetch_message(asst_id, conn=mock_pool.conn)
                assert msg['parent_id'] == user_msg_id
                assert msg['role'] == "assistant"
                assert msg['status'] == "pending"
                assert msg['creation_data']['source'] == "model"
                assert msg['creation_data']['model'] == "test-model"
                assert msg['creation_data']['parameters'] == {"temperature": 0.5}
                
                conv = await db_conversations.fetch_conversation(conv_id, conn=mock_pool.conn)
                assert conv['active_leaf_id'] == asst_id
                assert conv['updated_at'] > conv['created_at']
                
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

                # Model and parameters must be threaded through to the stream manager
                kwargs = mock_start.call_args.kwargs
                assert kwargs['model'] == "test-model"
                assert kwargs['parameters'] == {"temperature": 0.5}

@pytest.mark.asyncio
async def test_generate_message_parent_not_complete(mock_pool):
    """Tests that generating under a non-complete parent returns 400."""
    conv_id = await db_conversations.create_conversation(title=TEST_CONVERSATION_TITLE, conn=mock_pool.conn)
    root_id = await db_messages.create_message(
        conversation_id=conv_id, role="system", content=TEST_SYSTEM_PROMPT, 
        status="complete", creation_data={"source": "user"}, conn=mock_pool.conn
    )
    pending_user_msg = await db_messages.create_message(
        conversation_id=conv_id, role="user", parent_id=root_id, content=TEST_USER_MESSAGE,
        status="pending", creation_data={"source": "user"}, conn=mock_pool.conn
    )
    
    with patch('app.routers.messages.get_pool', return_value=mock_pool):
        with patch('app.routers.messages.stream_manager.start_stream') as mock_start:
            async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                payload = {}
                response = await client.post(f"/api/chat/messages/{pending_user_msg}/generate", json=payload)
                
                assert response.status_code == 400
                # assert response.json()["detail"] == "Parent message must be complete to generate a response."
                mock_start.assert_not_called()

@pytest.mark.asyncio
async def test_generate_message_parent_not_found(mock_pool):
    """Tests that generating from a non-existent parent message returns 404."""
    with patch('app.routers.messages.get_pool', return_value=mock_pool):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            random_parent_id = uuid.uuid4()
            payload = {"model": "test-model"}
            response = await client.post(f"/api/chat/messages/{random_parent_id}/generate", json=payload)
            
            assert response.status_code == 404
            assert response.json()["detail"] == "Parent message not found"

@pytest.mark.asyncio
async def test_generate_message_strips_reserved_parameters(mock_pool):
    """Tests that reserved parameter keys are stripped, and creation_data records exactly what is sent."""
    conv_id = await db_conversations.create_conversation(title=TEST_CONVERSATION_TITLE, conn=mock_pool.conn)
    root_id = await db_messages.create_message(
        conversation_id=conv_id, role="system", content=TEST_SYSTEM_PROMPT, 
        status="complete", creation_data={"source": "user"}, conn=mock_pool.conn
    )
    user_msg_id = await db_messages.create_message(
        conversation_id=conv_id, role="user", parent_id=root_id, content=TEST_USER_MESSAGE,
        status="complete", creation_data={"source": "user"}, conn=mock_pool.conn
    )

    with patch('app.routers.messages.get_pool', return_value=mock_pool):
        with patch('app.routers.messages.stream_manager.start_stream') as mock_start:
            async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                payload = {
                    "model": "test-model",
                    "parameters": {
                        "temperature": 0.5,
                        "model": "evil-model",
                        "messages": [{"role": "system", "content": "hacked"}],
                        "stream": False,
                        "stream_options": {}
                    }
                }
                response = await client.post(f"/api/chat/messages/{user_msg_id}/generate", json=payload)
                
                assert response.status_code == 200
                data = response.json()
                
                # creation_data (returned as server truth) must contain only the filtered dict
                assert data["creation_data"]["model"] == "test-model"
                assert data["creation_data"]["parameters"] == {"temperature": 0.5}
                
                # The stream manager receives the same filtered dict
                kwargs = mock_start.call_args.kwargs
                assert kwargs['model'] == "test-model"
                assert kwargs['parameters'] == {"temperature": 0.5}

@pytest.mark.asyncio
async def test_stream_message_endpoint_complete():
    """Tests GET /api/chat/messages/{id}/stream when message is already complete."""
    finished_msg = "Assistant response"
    finished_reasoning = "Thought process"
    mock_msg = {
        'id': uuid.uuid4(), 'status': 'complete', 'content': finished_msg,
        'reasoning': finished_reasoning,
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
            assert lines[0] == f'data: {json.dumps({"type": "done", "content": finished_msg, "reasoning": finished_reasoning, "metadata": {"tokens": 5}})}'
            assert lines[1] == "data: [DONE]"

@pytest.mark.asyncio
async def test_stream_message_endpoint_live():
    """Tests GET /api/chat/messages/{id}/stream during live generation."""
    mock_msg = {
        'id': uuid.uuid4(), 'status': 'streaming', 'content': None,
        'reasoning': None,
        'metadata': None, 'error_data': None
    }
    
    # Mock the stream manager to yield reasoning, token, then done
    async def mock_get_stream(msg_id):
        yield {"type": "reasoning", "content": "Think"}
        yield {"type": "token", "content": "Live"}
        yield {"type": "done", "metadata": {"tokens": 1}}

    with patch('app.routers.messages.db_messages.fetch_message', new_callable=AsyncMock, return_value=mock_msg):
        with patch('app.routers.messages.stream_manager.get_stream', side_effect=mock_get_stream):
            async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(f"/api/chat/messages/{mock_msg['id']}/stream")
                
                assert response.status_code == 200
                lines = response.text.strip().split("\n\n")
                assert len(lines) == 4
                assert lines[0] == f'data: {json.dumps({"type": "reasoning", "content": "Think"})}'
                assert lines[1] == f'data: {json.dumps({"type": "token", "content": "Live"})}'
                assert lines[2] == f'data: {json.dumps({"type": "done", "metadata": {"tokens": 1}})}'
                assert lines[3] == "data: [DONE]"

@pytest.mark.asyncio
async def test_stream_message_not_found(mock_pool):
    """Tests that streaming a non-existent message returns 404."""
    with patch('app.routers.messages.db_messages.fetch_message', new_callable=AsyncMock, return_value=None):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            random_msg_id = uuid.uuid4()
            response = await client.get(f"/api/chat/messages/{random_msg_id}/stream")
            
            assert response.status_code == 404
            assert response.json()["detail"] == "Message not found"

@pytest.mark.asyncio
async def test_generate_message_parent_canceled(mock_pool):
    """Tests that generating under a canceled parent is allowed (e.g., continuing from partial)."""
    conv_id = await db_conversations.create_conversation(title=TEST_CONVERSATION_TITLE, conn=mock_pool.conn)
    root_id = await db_messages.create_message(
        conversation_id=conv_id, role="system", content=TEST_SYSTEM_PROMPT, 
        status="complete", creation_data={"source": "user"}, conn=mock_pool.conn
    )
    canceled_user_msg = await db_messages.create_message(
        conversation_id=conv_id, role="user", parent_id=root_id, content=TEST_USER_MESSAGE,
        status="canceled", creation_data={"source": "user"}, conn=mock_pool.conn
    )
    
    with patch('app.routers.messages.get_pool', return_value=mock_pool):
        with patch('app.routers.messages.stream_manager.start_stream') as mock_start:
            async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                payload = {}
                response = await client.post(f"/api/chat/messages/{canceled_user_msg}/generate", json=payload)
                
                assert response.status_code == 200
                mock_start.assert_called_once()

@pytest.mark.asyncio
async def test_cancel_message_endpoint(mock_pool):
    """Tests POST /api/chat/messages/{id}/cancel."""
    conv_id = await db_conversations.create_conversation(title=TEST_CONVERSATION_TITLE, conn=mock_pool.conn)
    msg_id = await db_messages.create_message(
        conversation_id=conv_id, role="assistant", parent_id=None, content="Partial",
        status="streaming", creation_data={"source": "model"}, conn=mock_pool.conn
    )
    
    with patch('app.db.connection.get_pool', return_value=mock_pool):
        with patch('app.routers.messages.stream_manager.cancel_stream') as mock_cancel:
            async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(f"/api/chat/messages/{msg_id}/cancel")
                
                assert response.status_code == 200
                assert response.json()["status"] == "ok"
                mock_cancel.assert_called_once_with(msg_id)

@pytest.mark.asyncio
async def test_cancel_message_not_found(mock_pool):
    """Tests that canceling a non-existent message returns 404."""
    with patch('app.db.connection.get_pool', return_value=mock_pool):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            random_msg_id = uuid.uuid4()
            response = await client.post(f"/api/chat/messages/{random_msg_id}/cancel")
            assert response.status_code == 404

@pytest.mark.asyncio
async def test_stream_message_endpoint_canceled():
    """Tests GET /api/chat/messages/{id}/stream when message was canceled (e.g., reconnecting after cancel)."""
    mock_msg = {
        'id': uuid.uuid4(), 'status': 'canceled', 'content': 'Partial gen',
        'reasoning': 'Partial think',
        'metadata': None, 'error_data': None
    }
    with patch('app.routers.messages.db_messages.fetch_message', new_callable=AsyncMock, return_value=mock_msg):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/api/chat/messages/{mock_msg['id']}/stream")
            
            assert response.status_code == 200
            lines = response.text.strip().split("\n\n")
            assert len(lines) == 2
            assert lines[0] == f'data: {json.dumps({"type": "canceled", "content": "Partial gen", "reasoning": "Partial think"})}'
            assert lines[1] == "data: [DONE]"

@pytest.mark.asyncio
async def test_stream_message_endpoint_error():
    """Tests GET /api/chat/messages/{id}/stream when message has error status."""
    mock_msg = {
        'id': uuid.uuid4(), 'status': 'error', 'content': 'Partial gen',
        'reasoning': 'Partial think',
        'metadata': None, 'error_data': TEST_ERROR_DATA
    }
    with patch('app.routers.messages.db_messages.fetch_message', new_callable=AsyncMock, return_value=mock_msg):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/api/chat/messages/{mock_msg['id']}/stream")
            
            assert response.status_code == 200
            lines = response.text.strip().split("\n\n")
            assert len(lines) == 2
            assert lines[0] == f'data: {json.dumps({"type": "error", "content": "Partial gen", "reasoning": "Partial think", "error_data": TEST_ERROR_DATA})}'
            assert lines[1] == "data: [DONE]"