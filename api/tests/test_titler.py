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