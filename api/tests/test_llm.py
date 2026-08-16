import pytest
from unittest.mock import AsyncMock, MagicMock, patch

import base64

from app.llm.provider import generate_stream, generate_completion, list_models
import app.llm.provider as provider_module

_TEST_METADATA = {"prompt_tokens": 10, "completion_tokens": 2, "total_tokens": 12}
TEET_PARAMETERS = {"temperature": 0.5, "reasoning": {"effort": "low"}}

# --- Attachment assembly fixtures ---
PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"\x00" * 10
PDF_BYTES = b"%PDF-1.4\n" + b"\x00" * 10

def _att(mime: str, filename: str, data: bytes) -> dict:
    """An enriched attachment dict, as the stream manager hands them to the provider."""
    return {"id": "att-1", "mime_type": mime, "filename": filename, "size": len(data), "data": data}

# --- Helper Functions to Mock OpenAI SDK Chunks ---

class MockAsyncStream:
    """Wraps an async generator to act like an OpenAI AsyncStream with a close() method."""
    def __init__(self, gen):
        self._gen = gen

    def __aiter__(self):
        return self

    async def __anext__(self):
        return await self._gen.__anext__()

    async def close(self):
        await self._gen.aclose()

async def mock_stream_success():
    """Simulates a successful stream returning tokens and then usage."""
    # Chunk 1: Reasoning
    choice1 = MagicMock()
    choice1.delta.model_dump.return_value = {"content": None, "reasoning": "Sir!"}
    chunk1 = MagicMock(choices=[choice1], usage=None)
    yield chunk1
    
    # Chunk 2: Text
    choice2 = MagicMock()
    choice2.delta.model_dump.return_value = {"content": "Wonderful", "reasoning": None}
    chunk2 = MagicMock(choices=[choice2], usage=None)
    yield chunk2
    
    # Chunk 3: Text
    choice3 = MagicMock()
    choice3.delta.model_dump.return_value = {"content": " to", "reasoning": None}
    chunk3 = MagicMock(choices=[choice3], usage=None)
    yield chunk3
    
    # Chunk 4: Text
    choice4 = MagicMock()
    choice4.delta.model_dump.return_value = {"content": " see", "reasoning": None}
    chunk4 = MagicMock(choices=[choice4], usage=None)
    yield chunk4
    
    # Chunk 5: Text
    choice5 = MagicMock()
    choice5.delta.model_dump.return_value = {"content": " you", "reasoning": None}
    chunk5 = MagicMock(choices=[choice5], usage=None)
    yield chunk5
    
    # Chunk 6: Empty text, but contains usage data
    choice6 = MagicMock()
    choice6.delta.model_dump.return_value = {"content": None, "reasoning": None}
    usage = MagicMock()
    usage.model_dump.return_value = _TEST_METADATA
    chunk6 = MagicMock(choices=[choice6], usage=usage)
    yield chunk6

async def mock_stream_no_usage():
    """Simulates a stream that ends without sending a final usage chunk."""
    choice1 = MagicMock()
    choice1.delta.model_dump.return_value = {"content": "Hello", "reasoning": None}
    chunk1 = MagicMock(choices=[choice1], usage=None)
    yield chunk1

# --- Tests ---

@pytest.mark.asyncio
async def test_generate_stream_success():
    """Tests that tokens, reasoning, and metadata are yielded correctly."""
    # Arrange
    mock_client = AsyncMock()
    # create() returns an awaitable that resolves to an async iterator
    mock_client.chat.completions.create = AsyncMock(return_value=MockAsyncStream(mock_stream_success()))
    
    # Act
    events = []
    async for event in generate_stream(
        messages_history=[{"role": "user", "content": "I need a Bough"}], 
        model="test-model", 
        client=mock_client
    ):
        events.append(event)
        
    # Verify we passed the correct stream options to the SDK
    mock_client.chat.completions.create.assert_called_once_with(
        model="test-model",
        messages=[{"role": "user", "content": "I need a Bough"}],
        stream=True,
        stream_options={"include_usage": True},
        extra_body=None
    )
    assert len(events) == 6
    assert events[0] == {"type": "reasoning", "content": "Sir!"}
    assert events[1] == {"type": "token", "content": "Wonderful"}
    assert events[2] == {"type": "token", "content": " to"}
    assert events[3] == {"type": "token", "content": " see"}
    assert events[4] == {"type": "token", "content": " you"}
    assert events[5] == {"type": "done", "metadata": _TEST_METADATA}

@pytest.mark.asyncio
async def test_generate_stream_custom_parameters():
    """Tests that custom parameters are passed through to the provider via extra_body."""
    mock_client = AsyncMock()
    mock_client.chat.completions.create = AsyncMock(return_value=MockAsyncStream(mock_stream_no_usage()))
    
    async for _ in generate_stream(
        messages_history=[{"role": "user", "content": "Hi"}],
        model="test-model",
        parameters=TEET_PARAMETERS,
        client=mock_client
    ):
        pass
        
    mock_client.chat.completions.create.assert_called_once_with(
        model="test-model",
        messages=[{"role": "user", "content": "Hi"}],
        stream=True,
        stream_options={"include_usage": True},
        extra_body=TEET_PARAMETERS
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
    mock_response.usage.model_dump.return_value = _TEST_METADATA
    
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

@pytest.mark.asyncio
async def test_generate_stream_no_usage():
    """Tests that 'done' is yielded even if no usage chunk is received."""
    mock_client = AsyncMock()
    mock_client.chat.completions.create = AsyncMock(return_value=MockAsyncStream(mock_stream_no_usage()))
    
    events = []
    async for event in generate_stream(
        messages_history=[{"role": "user", "content": "Hi"}], 
        model="test-model", 
        client=mock_client
    ):
        events.append(event)
        
    assert len(events) == 2
    assert events[0] == {"type": "token", "content": "Hello"}
    # Ensure done is yielded with empty metadata, preventing frontend hangs
    assert events[1] == {"type": "done", "metadata": {}}

@pytest.mark.asyncio
async def test_list_models_fetch_and_cache():
    """Tests that list_models fetches from the provider and caches the result."""
    # Reset cache before test
    provider_module._models_cache = None
    provider_module._models_cache_at = None
    
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "data": [
            {"id": "m1", "name": "Model 1"},
            {"id": "m2", "name": "Model 2"}
        ]
    }
    
    # Patch the env var AND the httpx client
    with patch('app.llm.provider.httpx.AsyncClient') as mock_client_cls, \
         patch.dict('os.environ', {'PROVIDER_BASE_URL': 'http://mock-provider/api/v1'}):
        
        mock_client_instance = AsyncMock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value.__aenter__.return_value = mock_client_instance
        
        # First call: should fetch
        models = await list_models()
        assert len(models) == 2
        assert models[0] == {"id": "m1", "name": "Model 1"}
        assert models[1] == {"id": "m2", "name": "Model 2"}
        
        # Assert against the mocked env var URL
        mock_client_instance.get.assert_called_once_with("http://mock-provider/api/v1/models")
        
        # Second call: should use cache (get not called again)
        models_cached = await list_models()
        assert models_cached == models
        mock_client_instance.get.assert_called_once_with("http://mock-provider/api/v1/models")

@pytest.mark.asyncio
async def test_list_models_force_refresh():
    """Tests that force=True bypasses the cache."""
    # Set a fake cache
    provider_module._models_cache = [{"id": "old", "name": "Old"}]
    
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {"data": [{"id": "new", "name": "New"}]}
    
    with patch('app.llm.provider.httpx.AsyncClient') as mock_client_cls, \
         patch.dict('os.environ', {'PROVIDER_BASE_URL': 'http://mock-provider/api/v1'}):
        
        mock_client_instance = AsyncMock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value.__aenter__.return_value = mock_client_instance
        
        models = await list_models(force=True)
        assert models == [{"id": "new", "name": "New"}]
        
        # Assert against the mocked env var URL
        mock_client_instance.get.assert_called_once_with("http://mock-provider/api/v1/models")

@pytest.mark.asyncio
async def test_generate_stream_assembles_image_content():
    """Attachment-bearing messages become multimodal arrays (text first); text-only siblings stay strings."""
    mock_client = AsyncMock()
    mock_client.chat.completions.create = AsyncMock(return_value=MockAsyncStream(mock_stream_no_usage()))

    history = [
        {"role": "system", "content": "You are a test."},
        {"role": "user", "content": "What is in this picture?",
         "attachments": [_att("image/png", "cat.png", PNG_BYTES)]},
    ]

    async for _ in generate_stream(messages_history=history, model="test-model", client=mock_client):
        pass

    sent = mock_client.chat.completions.create.call_args.kwargs["messages"]
    assert sent[0]["content"] == "You are a test."  # no attachments -> plain string, unchanged
    content = sent[1]["content"]
    assert isinstance(content, list)
    assert content[0] == {"type": "text", "text": "What is in this picture?"}  # text part first
    b64 = base64.b64encode(PNG_BYTES).decode("utf-8")
    assert content[1] == {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}


@pytest.mark.asyncio
async def test_generate_stream_assembles_pdf_content():
    """PDFs use the file content type with filename and data-URI file_data."""
    mock_client = AsyncMock()
    mock_client.chat.completions.create = AsyncMock(return_value=MockAsyncStream(mock_stream_no_usage()))

    history = [{"role": "user", "content": "Summarize this",
                "attachments": [_att("application/pdf", "doc.pdf", PDF_BYTES)]}]

    async for _ in generate_stream(messages_history=history, model="test-model", client=mock_client):
        pass

    content = mock_client.chat.completions.create.call_args.kwargs["messages"][0]["content"]
    b64 = base64.b64encode(PDF_BYTES).decode("utf-8")
    assert content[0] == {"type": "text", "text": "Summarize this"}
    assert content[1] == {"type": "file", "file": {"filename": "doc.pdf", "file_data": f"data:application/pdf;base64,{b64}"}}


@pytest.mark.asyncio
async def test_generate_stream_attachment_only_omits_text_part():
    """Messages with no text send attachment parts only — no empty-string text noise."""
    mock_client = AsyncMock()
    mock_client.chat.completions.create = AsyncMock(return_value=MockAsyncStream(mock_stream_no_usage()))

    history = [{"role": "user", "content": "", "attachments": [_att("image/png", "cat.png", PNG_BYTES)]}]

    async for _ in generate_stream(messages_history=history, model="test-model", client=mock_client):
        pass

    content = mock_client.chat.completions.create.call_args.kwargs["messages"][0]["content"]
    assert len(content) == 1
    assert all(part["type"] != "text" for part in content)


@pytest.mark.asyncio
async def test_generate_stream_unknown_mime_raises():
    """Unknown MIME types are internal failures: ValueError escapes (no error event), provider never called."""
    mock_client = AsyncMock()
    history = [{"role": "user", "content": "hi", "attachments": [_att("video/mp4", "v.mp4", b"\x00\x00\x00\x00")]}]

    with pytest.raises(ValueError):
        async for _ in generate_stream(messages_history=history, model="test-model", client=mock_client):
            pass

    mock_client.chat.completions.create.assert_not_called()