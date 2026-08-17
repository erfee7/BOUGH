import uuid
import pytest
from unittest.mock import patch

from app.core import titler

@pytest.mark.asyncio
async def test_titler_skips_if_title_exists():
    """Tests that titler does nothing if title exists and force=False."""
    conv_id = uuid.uuid4()
    
    mock_conv = {"title": "Existing Title", "active_leaf_id": uuid.uuid4()}
    with patch('app.core.titler.db_conversations.fetch_conversation', return_value=mock_conv):
        with patch('app.core.titler.llm_provider.generate_completion') as mock_gen:
            result = await titler.generate_title(conv_id, force=False)
            
            assert result == "Existing Title"
            mock_gen.assert_not_awaited()

@pytest.mark.asyncio
async def test_titler_no_content():
    """Tests that titler refuses if both user and assistant messages are missing."""
    conv_id = uuid.uuid4()
    leaf_id = uuid.uuid4()
    
    mock_conv = {"title": None, "active_leaf_id": leaf_id}
    mock_history = [{"role": "system", "content": "sys"}]
    
    with patch('app.core.titler.db_conversations.fetch_conversation', return_value=mock_conv):
        with patch('app.core.titler.db_messages.fetch_message_history', return_value=mock_history):
            with patch('app.core.titler.llm_provider.generate_completion') as mock_gen:
                result = await titler.generate_title(conv_id)
                
                assert result is None
                mock_gen.assert_not_awaited()

@pytest.mark.asyncio
async def test_titler_success_and_normalization():
    """Tests the full titler flow including quote/period stripping."""
    conv_id = uuid.uuid4()
    leaf_id = uuid.uuid4()
    
    mock_conv = {"title": None, "active_leaf_id": leaf_id}
    mock_history = [
        {"role": "system", "content": "sys"},
        {"role": "user", "content": "Hello there"},
        {"role": "assistant", "content": "Hi!"}
    ]
    # Simulate LLM returning a quoted string with a period
    mock_llm_response = {"content": '"A Great Title."', "usage": {}}
    
    with patch('app.core.titler.db_conversations.fetch_conversation', return_value=mock_conv):
        with patch('app.core.titler.db_messages.fetch_message_history', return_value=mock_history):
            with patch('app.core.titler.llm_provider.generate_completion', return_value=mock_llm_response) as mock_gen:
                with patch('app.core.titler.db_conversations.update_conversation') as mock_update:
                    
                    result = await titler.generate_title(conv_id, force=True)
                    
                    assert result == "A Great Title"
                    mock_gen.assert_awaited_once()
                    # Verify it saved the normalized title
                    mock_update.assert_awaited_once_with(conv_id, title="A Great Title")

@pytest.mark.asyncio
async def test_titler_includes_attachment_hint():
    """Tests that image-only conversations get a titling signal via the pure-text file indicator."""
    conv_id = uuid.uuid4()
    leaf_id = uuid.uuid4()
    att_id = str(uuid.uuid4())

    mock_conv = {"title": None, "active_leaf_id": leaf_id}
    mock_history = [
        {"role": "system", "content": "sys"},
        {"role": "user", "content": "", "attachments": [
            {"id": att_id, "mime_type": "image/png", "filename": "cat.png", "size": 4}]},
        {"role": "assistant", "content": "A cat sitting on a bough."}
    ]
    mock_llm_response = {"content": "Cat On A Bough", "usage": {}}

    with patch('app.core.titler.db_conversations.fetch_conversation', return_value=mock_conv):
        with patch('app.core.titler.db_messages.fetch_message_history', return_value=mock_history):
            with patch('app.core.titler.llm_provider.generate_completion', return_value=mock_llm_response) as mock_gen:
                with patch('app.core.titler.db_conversations.update_conversation') as mock_update:
                    result = await titler.generate_title(conv_id)

                    assert result == "Cat On A Bough"
                    mock_update.assert_awaited_once_with(conv_id, title="Cat On A Bough")

                    # The titling payload carries the filename + detected type indicator
                    sent_history = mock_gen.call_args.args[0]
                    user_payload = sent_history[1]["content"]
                    assert "[attachments: cat.png (image/png)]" in user_payload


@pytest.mark.asyncio
async def test_titler_plain_text_has_no_hint():
    """Tests that text-only conversations carry no attachment indicator."""
    conv_id = uuid.uuid4()
    leaf_id = uuid.uuid4()

    mock_conv = {"title": None, "active_leaf_id": leaf_id}
    mock_history = [
        {"role": "user", "content": "hello there"},
        {"role": "assistant", "content": "general reply"}
    ]
    mock_llm_response = {"content": "A Greeting", "usage": {}}

    with patch('app.core.titler.db_conversations.fetch_conversation', return_value=mock_conv):
        with patch('app.core.titler.db_messages.fetch_message_history', return_value=mock_history):
            with patch('app.core.titler.llm_provider.generate_completion', return_value=mock_llm_response) as mock_gen:
                await titler.generate_title(conv_id)

                user_payload = mock_gen.call_args.args[0][1]["content"]
                assert "attachments" not in user_payload
                assert "hello there" in user_payload