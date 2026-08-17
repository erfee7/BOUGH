import uuid
import pytest
import asyncpg

from app.db.conversations import create_conversation, delete_conversation, fetch_conversation
from app.db.messages import create_message, fetch_message, update_message, delete_message, fetch_message_history, fetch_conversation_messages
from app.db.attachments import create_attachment

@pytest.mark.asyncio
async def test_create_and_fetch_message(db_transaction: asyncpg.Connection):
    """Tests creating a message and fetching it back."""
    conversation_id = await create_conversation(title="Test", conn=db_transaction)
    message_id = await create_message(conversation_id=conversation_id, role="user", content="I need a Bough", conn=db_transaction)
    
    result = await fetch_message(message_id=message_id, conn=db_transaction)
    assert result is not None
    assert isinstance(result, dict)  # Enforces no Record type is returned
    assert result['id'] == message_id
    assert result['role'] == "user"
    assert result['content'] == "I need a Bough"
    assert result['reasoning'] is None  # Should be None if not provided

@pytest.mark.asyncio
async def test_update_message(db_transaction: asyncpg.Connection):
    """Tests updating message content, reasoning, and status."""
    conversation_id = await create_conversation(title="Test", conn=db_transaction)
    message_id = await create_message(conversation_id=conversation_id, role="assistant", content="", status="pending", conn=db_transaction)
    
    await update_message(message_id, conn=db_transaction, content="Wonderful to see you", reasoning="Sir!", status="complete", metadata={"tokens": 5})
    
    result = await fetch_message(message_id=message_id, conn=db_transaction)
    assert result['content'] == "Wonderful to see you"
    assert result['reasoning'] == "Sir!"
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
    child_id = await create_message(conversation_id=conversation_id, role="assistant", parent_id=root_id, content="Child", reasoning="Thinking...", conn=db_transaction)
    grandchild_id = await create_message(conversation_id=conversation_id, role="user", parent_id=child_id, content="Grandchild", conn=db_transaction)
    
    # Fetch history from the grandchild
    history = await fetch_message_history(message_id=grandchild_id, conn=db_transaction)

    assert isinstance(history, list)  # Enforces no Record type is returned
    assert all(isinstance(item, dict) for item in history)
    
    assert len(history) == 3
    # Ordered chronologically (root first)
    assert history[0]['content'] == "Root"
    assert history[1]['content'] == "Child"
    assert history[1]['reasoning'] == "Thinking..."
    assert history[2]['content'] == "Grandchild"

@pytest.mark.asyncio
async def test_fetch_conversation_messages_flat_list(db_transaction: asyncpg.Connection):
    """Tests fetching all messages for a conversation as a flat list."""
    conversation_id = await create_conversation(title="Test", conn=db_transaction)
    
    await create_message(conversation_id=conversation_id, role="user", content="Msg 1", conn=db_transaction)
    await create_message(conversation_id=conversation_id, role="assistant", content="Msg 2", reasoning="Reason 2", conn=db_transaction)
    
    messages = await fetch_conversation_messages(conversation_id=conversation_id, conn=db_transaction)
    
    assert isinstance(messages, list)  # Enforces no Record type is returned
    assert all(isinstance(item, dict) for item in messages)

    assert len(messages) == 2
    assert messages[0]['content'] == "Msg 1"
    assert messages[1]['content'] == "Msg 2"
    assert messages[1]['reasoning'] == "Reason 2"

@pytest.mark.asyncio
async def test_delete_message(db_transaction: asyncpg.Connection):
    """Tests deleting a message."""
    conversation_id = await create_conversation(title="Test", conn=db_transaction)
    message_id = await create_message(conversation_id=conversation_id, role="user", content="Hello", conn=db_transaction)
    
    await delete_message(message_id=message_id, conn=db_transaction)
    result = await fetch_message(message_id=message_id, conn=db_transaction)
    assert result is None

@pytest.mark.asyncio
async def test_delete_conversation_cascade(db_transaction: asyncpg.Connection):
    """Tests that deleting a conversation cascades to all child messages."""
    # 1. Create the conversation
    conversation_id = await create_conversation(title="To Delete", conn=db_transaction)
    
    # 2. Create a tree of messages: root -> user -> assistant
    root_id = await create_message(
        conversation_id=conversation_id, 
        role="system", 
        parent_id=None, 
        content="System Prompt", 
        status="complete", 
        conn=db_transaction
    )
    user_id = await create_message(
        conversation_id=conversation_id, 
        role="user", 
        parent_id=root_id, 
        content="User text", 
        status="complete", 
        conn=db_transaction
    )
    assistant_id = await create_message(
        conversation_id=conversation_id, 
        role="assistant", 
        parent_id=user_id, 
        content="Assistant response", 
        status="complete", 
        conn=db_transaction
    )
    
    # Verify they exist before deletion
    assert await fetch_message(root_id, conn=db_transaction) is not None
    assert await fetch_message(user_id, conn=db_transaction) is not None
    assert await fetch_message(assistant_id, conn=db_transaction) is not None
    
    # 3. Delete the conversation
    await delete_conversation(conversation_id=conversation_id, conn=db_transaction)
    
    # 4. Assert the conversation is gone
    result = await fetch_conversation(conversation_id=conversation_id, conn=db_transaction)
    assert result is None
    
    # 5. Assert all messages are gone (testing the ON DELETE CASCADE behavior)
    assert await fetch_message(root_id, conn=db_transaction) is None
    assert await fetch_message(user_id, conn=db_transaction) is None
    assert await fetch_message(assistant_id, conn=db_transaction) is None

@pytest.mark.asyncio
async def test_message_attachments_roundtrip(db_transaction: asyncpg.Connection):
    """Attachments metadata array survives create -> fetch -> history traversal, ids staying strings."""
    conversation_id = await create_conversation(title="Test", conn=db_transaction)
    attachment_id = await create_attachment(filename="cat.png", mime_type="image/png", data=b"\x89PNG", conn=db_transaction)
    attachments = [{"id": str(attachment_id), "mime_type": "image/png", "filename": "cat.png", "size": 4}]

    message_id = await create_message(
        conversation_id=conversation_id,
        role="user",
        content="What is this?",
        attachments=attachments,
        conn=db_transaction,
    )

    result = await fetch_message(message_id=message_id, conn=db_transaction)
    assert result['attachments'] == attachments
    assert result['attachments'][0]['id'] == str(attachment_id)  # Stays a string through the JSONB round-trip

    history = await fetch_message_history(message_id=message_id, conn=db_transaction)
    assert history[0]['attachments'] == attachments


@pytest.mark.asyncio
async def test_message_attachments_default_empty(db_transaction: asyncpg.Connection):
    """Messages created without attachments default to an empty list."""
    conversation_id = await create_conversation(title="Test", conn=db_transaction)
    message_id = await create_message(conversation_id=conversation_id, role="user", content="No files", conn=db_transaction)

    result = await fetch_message(message_id=message_id, conn=db_transaction)
    assert result['attachments'] == []