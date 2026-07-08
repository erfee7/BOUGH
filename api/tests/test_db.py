import uuid
import pytest
import asyncpg

from app.db import create_conversation, fetch_conversation

# Note: pytest-asyncio is configured in auto mode in pyproject.toml, 
# so we don't strictly need the @pytest.mark.asyncio decorator, 
# but we include it here for explicit clarity.

@pytest.mark.asyncio
async def test_pool_initializes(db_pool: asyncpg.Pool):
    """Tests that the session-scoped pool fixture successfully initialized."""
    assert db_pool is not None

@pytest.mark.asyncio
async def test_create_and_fetch_conversation(db_transaction: asyncpg.Connection):
    """Tests creating a conversation and fetching it back."""
    # 1. Arrange
    test_title = "My Test Chat"
    
    # 2. Act: Create a conversation using the transactional connection
    conv_id = await create_conversation(title=test_title, conn=db_transaction)
    
    # 3. Act: Fetch it back
    result = await fetch_conversation(conv_id=conv_id, conn=db_transaction)
    
    # 4. Assert
    assert result is not None
    assert result['id'] == conv_id
    assert result['title'] == test_title

@pytest.mark.asyncio
async def test_fetch_missing_conversation(db_transaction: asyncpg.Connection):
    """Tests that fetching a non-existent conversation returns None."""
    # 1. Arrange
    random_uuid = uuid.uuid4()
    
    # 2. Act
    result = await fetch_conversation(conv_id=random_uuid, conn=db_transaction)
    
    # 3. Assert
    assert result is None