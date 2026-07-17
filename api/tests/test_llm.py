import pytest
from unittest.mock import AsyncMock, MagicMock

from app.llm.provider import generate_stream, generate_completion

# --- Helper Functions to Mock OpenAI SDK Chunks ---

async def mock_stream_success():
    """Simulates a successful stream returning tokens and then usage."""
    # Chunk 1: Text
    choice1 = MagicMock()
    choice1.delta.content = "Wonderful"
    chunk1 = MagicMock(choices=[choice1], usage=None)
    yield chunk1
    
    # Chunk 2: Text
    choice2 = MagicMock()
    choice2.delta.content = " to"
    chunk2 = MagicMock(choices=[choice2], usage=None)
    yield chunk2
    
    # Chunk 3: Text
    choice3 = MagicMock()
    choice3.delta.content = " see"
    chunk3 = MagicMock(choices=[choice3], usage=None)
    yield chunk3
    
    # Chunk 4: Text
    choice4 = MagicMock()
    choice4.delta.content = " you"
    chunk4 = MagicMock(choices=[choice4], usage=None)
    yield chunk4
    
    # Chunk 5: Empty text, but contains usage data
    choice5 = MagicMock()
    choice5.delta.content = None
    usage = MagicMock()
    usage.model_dump.return_value = {"prompt_tokens": 10, "completion_tokens": 2, "total_tokens": 12}
    chunk5 = MagicMock(choices=[choice5], usage=usage)
    yield chunk5

# --- Tests ---

@pytest.mark.asyncio
async def test_generate_stream_success():
    """Tests that tokens and metadata are yielded correctly."""
    # Arrange
    mock_client = AsyncMock()
    # create() returns an awaitable that resolves to an async iterator
    mock_client.chat.completions.create = AsyncMock(return_value=mock_stream_success())
    
    # Act
    events = []
    async for event in generate_stream(
        messages_history=[{"role": "user", "content": "I need a Bough"}], 
        model="test-model", 
        client=mock_client
    ):
        events.append(event)
        
    # Assert
    assert len(events) == 5
    assert events[0] == {"type": "token", "content": "Wonderful"}
    assert events[1] == {"type": "token", "content": " to"}
    assert events[2] == {"type": "token", "content": " see"}
    assert events[3] == {"type": "token", "content": " you"}
    assert events[4] == {"type": "done", "metadata": {"prompt_tokens": 10, "completion_tokens": 2, "total_tokens": 12}}
    
    # Verify we passed the correct stream options to the SDK
    mock_client.chat.completions.create.assert_called_once_with(
        model="test-model",
        messages=[{"role": "user", "content": "I need a Bough"}],
        stream=True,
        stream_options={"include_usage": True}
    )

@pytest.mark.asyncio
async def test_generate_stream_error():
    """Tests that SDK exceptions are caught and yielded as error events."""
    # Arrange
    mock_client = AsyncMock()
    mock_client.chat.completions.create = AsyncMock(side_effect=Exception("Simulated API Error"))
    
    # Act
    events = []
    async for event in generate_stream(
        messages_history=[{"role": "user", "content": "Hi"}], 
        model="test-model", 
        client=mock_client
    ):
        events.append(event)
        
    # Assert
    assert len(events) == 1
    assert events[0]["type"] == "error"
    assert "Simulated API Error" in events[0]["error_data"]["message"]
    assert events[0]["error_data"]["type"] == "Exception"

@pytest.mark.asyncio
async def test_generate_completion_success():
    """Tests that non-streaming completion returns content and usage."""
    # Arrange
    mock_client = AsyncMock()
    
    # Setup mock response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Test Title"))]
    mock_response.usage = MagicMock()
    mock_response.usage.model_dump.return_value = {"prompt_tokens": 10, "completion_tokens": 2, "total_tokens": 12}
    
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
    
    messages_payload = [{"role": "developer", "content": "prompt"}, {"role": "user", "content": "hi"}]
    
    # Act
    result = await generate_completion(
        messages_history=messages_payload,
        model="test-model",
        client=mock_client
    )
    
    # Assert
    assert result["content"] == "Test Title"
    assert result["usage"]["total_tokens"] == 12
    
    mock_client.chat.completions.create.assert_called_once_with(
        model="test-model",
        messages=messages_payload,
        stream=False
    )