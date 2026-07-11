import uuid
import pytest
import asyncpg

from app.db.conversations import create_conversation
from app.db.messages import create_message, fetch_message, update_message, delete_message, fetch_message_history, fetch_conversation_messages

@pytest.mark.asyncio
async def test_create_and_fetch_message(db_transaction: asyncpg.Connection):
    """Tests creating a message and fetching it back."""
    conversation_id = await create_conversation(title="Test", conn=db_transaction)
    message_id = await create_message(conversation_id=conversation_id, role="user", content="I need a Bough", conn=db_transaction)
    
    result = await fetch_message(message_id=message_id, conn=db_transaction)
    assert result is not None
    assert result['id'] == message_id
    assert result['role'] == "user"
    assert result['content'] == "I need a Bough"

@pytest.mark.asyncio
async def test_update_message(db_transaction: asyncpg.Connection):
    """Tests updating message content and status."""
    conversation_id = await create_conversation(title="Test", conn=db_transaction)
    message_id = await create_message(conversation_id=conversation_id, role="assistant", content="", status="pending", conn=db_transaction)
    
    await update_message(message_id, conn=db_transaction, content="Wonderful to see you", status="complete", metadata={"tokens": 5})
    
    result = await fetch_message(message_id=message_id, conn=db_transaction)
    assert result['content'] == "Wonderful to see you"
    assert result['status'] == "complete"
    assert result['metadata'] == {"tokens": 5}

@pytest.mark.asyncio
async def test_update_message_no_args(db_transaction: asyncpg.Connection):
    """Tests that calling update with no valid args logs a warning and does nothing."""
    conversation_id = await create_conversation(title="Test", conn=db_transaction)
    message_id = await create_message(conversation_id=conversation_id, role="user", content="I need a Bough", conn=db_transaction)
    
    await update_message(message_id, conn=db_transaction, invalid_col="ignore_me")
    
    result = await fetch_message(message_id=message_id, conn=db_transaction)
    assert result['content'] == "I need a Bough"

@pytest.mark.asyncio
async def test_fetch_message_history_recursive(db_transaction: asyncpg.Connection):
    """Tests the recursive CTE that traverses the message tree upwards."""
    conversation_id = await create_conversation(title="Test", conn=db_transaction)
    
    # Create a chain: Root -> Child -> Grandchild
    root_id = await create_message(conversation_id=conversation_id, role="user", content="Root", conn=db_transaction)
    child_id = await create_message(conversation_id=conversation_id, role="assistant", parent_id=root_id, content="Child", conn=db_transaction)
    grandchild_id = await create_message(conversation_id=conversation_id, role="user", parent_id=child_id, content="Grandchild", conn=db_transaction)
    
    # Fetch history from the grandchild
    history = await fetch_message_history(message_id=grandchild_id, conn=db_transaction)
    
    assert len(history) == 3
    # Ordered chronologically (root first)
    assert history[0]['content'] == "Root"
    assert history[1]['content'] == "Child"
    assert history[2]['content'] == "Grandchild"

@pytest.mark.asyncio
async def test_fetch_conversation_messages_flat_list(db_transaction: asyncpg.Connection):
    """Tests fetching all messages for a conversation as a flat list."""
    conversation_id = await create_conversation(title="Test", conn=db_transaction)
    
    await create_message(conversation_id=conversation_id, role="user", content="Msg 1", conn=db_transaction)
    await create_message(conversation_id=conversation_id, role="assistant", content="Msg 2", conn=db_transaction)
    
    messages = await fetch_conversation_messages(conversation_id=conversation_id, conn=db_transaction)
    assert len(messages) == 2
    assert messages[0]['content'] == "Msg 1"
    assert messages[1]['content'] == "Msg 2"

@pytest.mark.asyncio
async def test_delete_message(db_transaction: asyncpg.Connection):
    """Tests deleting a message."""
    conversation_id = await create_conversation(title="Test", conn=db_transaction)
    message_id = await create_message(conversation_id=conversation_id, role="user", content="Hello", conn=db_transaction)
    
    await delete_message(message_id=message_id, conn=db_transaction)
    result = await fetch_message(message_id=message_id, conn=db_transaction)
    assert result is None