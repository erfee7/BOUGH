import uuid
import pytest
import asyncpg

from app.db.prompts import create_prompt, fetch_prompt, fetch_all_prompts, update_prompt, delete_prompt

@pytest.mark.asyncio
async def test_create_and_fetch_prompt(db_transaction: asyncpg.Connection):
    """Tests creating a prompt and fetching it back."""
    test_name = "Test Prompt"
    test_content = "You are a test assistant."
    test_role = "system"
    test_description = "A test description"
    
    prompt_id = await create_prompt(
        name=test_name,
        content=test_content,
        role=test_role,
        description=test_description,
        conn=db_transaction
    )
    
    result = await fetch_prompt(prompt_id=prompt_id, conn=db_transaction)
    
    assert result is not None
    assert isinstance(result, dict)  # Enforces no Record type is returned
    assert result['id'] == prompt_id
    assert result['name'] == test_name
    assert result['content'] == test_content
    assert result['role'] == test_role
    assert result['description'] == test_description

@pytest.mark.asyncio
async def test_fetch_missing_prompt(db_transaction: asyncpg.Connection):
    """Tests that fetching a non-existent prompt returns None."""
    random_uuid = uuid.uuid4()
    result = await fetch_prompt(prompt_id=random_uuid, conn=db_transaction)
    assert result is None

@pytest.mark.asyncio
async def test_fetch_all_prompts(db_transaction: asyncpg.Connection):
    """Tests fetching all prompts."""
    # Create a few prompts
    await create_prompt(name="First", content="c1", role="system", conn=db_transaction)
    await create_prompt(name="Second", content="c2", role="developer", conn=db_transaction)
    
    prompts = await fetch_all_prompts(conn=db_transaction)
    
    assert len(prompts) == 2
    assert isinstance(prompts, list)
    assert all(isinstance(item, dict) for item in prompts)  # Enforces no Record type is returned
    
    names = [p['name'] for p in prompts]
    assert "First" in names
    assert "Second" in names

@pytest.mark.asyncio
async def test_fetch_all_prompts_with_role_filter(db_transaction: asyncpg.Connection):
    """Tests fetching prompts filtered by role."""
    await create_prompt(name="Sys1", content="c1", role="system", conn=db_transaction)
    await create_prompt(name="Dev1", content="c2", role="developer", conn=db_transaction)
    
    sys_prompts = await fetch_all_prompts(role="system", conn=db_transaction)
    assert len(sys_prompts) == 1
    assert sys_prompts[0]['name'] == "Sys1"
    
    dev_prompts = await fetch_all_prompts(role="developer", conn=db_transaction)
    assert len(dev_prompts) == 1
    assert dev_prompts[0]['name'] == "Dev1"

@pytest.mark.asyncio
async def test_update_prompt(db_transaction: asyncpg.Connection):
    """Tests updating a prompt's fields."""
    prompt_id = await create_prompt(name="Old", content="Old", role="system", conn=db_transaction)
    
    await update_prompt(prompt_id, conn=db_transaction, name="New", description="New Desc")
    
    result = await fetch_prompt(prompt_id=prompt_id, conn=db_transaction)
    assert result['name'] == "New"
    assert result['description'] == "New Desc"
    assert result['content'] == "Old"  # Unchanged

@pytest.mark.asyncio
async def test_update_prompt_no_args(db_transaction: asyncpg.Connection):
    """Tests that calling update with no args logs a warning and does nothing."""
    prompt_id = await create_prompt(name="Title", content="c", role="system", conn=db_transaction)
    # This should just return None without crashing
    await update_prompt(prompt_id, conn=db_transaction, invalid_col="ignore_me")
    # Verify nothing changed
    result = await fetch_prompt(prompt_id=prompt_id, conn=db_transaction)
    assert result['name'] == "Title"

@pytest.mark.asyncio
async def test_delete_prompt(db_transaction: asyncpg.Connection):
    """Tests deleting a prompt."""
    prompt_id = await create_prompt(name="To Delete", content="c", role="system", conn=db_transaction)
    await delete_prompt(prompt_id=prompt_id, conn=db_transaction)
    
    result = await fetch_prompt(prompt_id=prompt_id, conn=db_transaction)
    assert result is None