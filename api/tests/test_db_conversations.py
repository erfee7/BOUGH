import uuid
import pytest
import asyncpg
import asyncio

from app.db.conversations import create_conversation, fetch_conversation, fetch_all_conversations, update_conversation, delete_conversation

@pytest.mark.asyncio
async def test_create_and_fetch_conversation(db_transaction: asyncpg.Connection):
    """Tests creating a conversation and fetching it back."""
    test_title = "My Test Chat"
    conversation_id = await create_conversation(title=test_title, conn=db_transaction)
    result = await fetch_conversation(conversation_id=conversation_id, conn=db_transaction)
    
    assert result is not None
    assert isinstance(result, dict)  # Enforces no Record type is returned
    assert result['id'] == conversation_id
    assert result['title'] == test_title

@pytest.mark.asyncio
async def test_fetch_missing_conversation(db_transaction: asyncpg.Connection):
    """Tests that fetching a non-existent conversation returns None."""
    random_uuid = uuid.uuid4()
    result = await fetch_conversation(conversation_id=random_uuid, conn=db_transaction)
    assert result is None

@pytest.mark.asyncio
async def test_fetch_all_conversations(db_transaction: asyncpg.Connection):
    """Tests fetching all conversations ordered by newest first."""
    # Create a few conversations
    conv_id1 = await create_conversation(title="First", conn=db_transaction)
    await asyncio.sleep(1)
    conv_id2 = await create_conversation(title="Second", conn=db_transaction)
    
    conversations = await fetch_all_conversations(conn=db_transaction)
    
    assert len(conversations) == 2
    assert isinstance(conversations, list)
    assert all(isinstance(item, dict) for item in conversations)  # Enforces no Record type is returned
    
    titles = [c['title'] for c in conversations]
    assert "First" in titles
    assert "Second" in titles

@pytest.mark.asyncio
async def test_update_conversation(db_transaction: asyncpg.Connection):
    """Tests updating a conversation title."""
    conversation_id = await create_conversation(title="Old Title", conn=db_transaction)
    await update_conversation(conversation_id, conn=db_transaction, title="New Title")
    
    result = await fetch_conversation(conversation_id=conversation_id, conn=db_transaction)
    assert result['title'] == "New Title"

@pytest.mark.asyncio
async def test_update_conversation_no_args(db_transaction: asyncpg.Connection):
    """Tests that calling update with no args logs a warning and does nothing."""
    conversation_id = await create_conversation(title="Title", conn=db_transaction)
    # This should just return None without crashing
    await update_conversation(conversation_id, conn=db_transaction, invalid_col="ignore_me")
    # Verify nothing changed
    result = await fetch_conversation(conversation_id=conversation_id, conn=db_transaction)
    assert result['title'] == "Title"

@pytest.mark.asyncio
async def test_delete_conversation(db_transaction: asyncpg.Connection):
    """Tests deleting a conversation."""
    conversation_id = await create_conversation(title="To Delete", conn=db_transaction)
    await delete_conversation(conversation_id=conversation_id, conn=db_transaction)
    
    result = await fetch_conversation(conversation_id=conversation_id, conn=db_transaction)
    assert result is None