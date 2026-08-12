import uuid
import pytest
import asyncpg

from app.db.generation_presets import create_preset, fetch_preset, fetch_all_presets, update_preset, delete_preset

@pytest.mark.asyncio
async def test_create_and_fetch_preset(db_transaction: asyncpg.Connection):
    """Tests creating a preset and fetching it back."""
    test_name = "Test Preset"
    test_model = "test-model"
    test_parameters = {"temperature": 0.5, "reasoning": {"effort": "low"}}
    
    preset_id = await create_preset(
        name=test_name,
        model=test_model,
        parameters=test_parameters,
        conn=db_transaction
    )
    
    result = await fetch_preset(preset_id=preset_id, conn=db_transaction)
    
    assert result is not None
    assert isinstance(result, dict)  # Enforces no Record type is returned
    assert result['id'] == preset_id
    assert result['name'] == test_name
    assert result['model'] == test_model
    assert result['parameters'] == test_parameters

@pytest.mark.asyncio
async def test_fetch_missing_preset(db_transaction: asyncpg.Connection):
    """Tests that fetching a non-existent preset returns None."""
    random_uuid = uuid.uuid4()
    result = await fetch_preset(preset_id=random_uuid, conn=db_transaction)
    assert result is None

@pytest.mark.asyncio
async def test_fetch_all_presets(db_transaction: asyncpg.Connection):
    """Tests fetching all presets."""
    await create_preset(name="First", model="m1", parameters={}, conn=db_transaction)
    await create_preset(name="Second", model=None, parameters={"top_p": 0.9}, conn=db_transaction)
    
    presets = await fetch_all_presets(conn=db_transaction)
    
    assert len(presets) == 2
    assert isinstance(presets, list)
    assert all(isinstance(item, dict) for item in presets)  # Enforces no Record type is returned
    
    names = [p['name'] for p in presets]
    assert "First" in names
    assert "Second" in names

@pytest.mark.asyncio
async def test_update_preset(db_transaction: asyncpg.Connection):
    """Tests updating a preset's fields."""
    preset_id = await create_preset(name="Old", model="m1", parameters={}, conn=db_transaction)
    
    await update_preset(preset_id, conn=db_transaction, name="New", model="m2", parameters={"temperature": 0.7})
    
    result = await fetch_preset(preset_id=preset_id, conn=db_transaction)
    assert result['name'] == "New"
    assert result['model'] == "m2"
    assert result['parameters'] == {"temperature": 0.7}

@pytest.mark.asyncio
async def test_update_preset_no_args(db_transaction: asyncpg.Connection):
    """Tests that calling update with no valid args logs a warning and does nothing."""
    preset_id = await create_preset(name="Title", model="m1", parameters={}, conn=db_transaction)
    # This should just return None without crashing
    await update_preset(preset_id, conn=db_transaction, invalid_col="ignore_me")
    # Verify nothing changed
    result = await fetch_preset(preset_id=preset_id, conn=db_transaction)
    assert result['name'] == "Title"
    assert result['model'] == "m1"

@pytest.mark.asyncio
async def test_delete_preset(db_transaction: asyncpg.Connection):
    """Tests deleting a preset."""
    preset_id = await create_preset(name="To Delete", model="m1", parameters={}, conn=db_transaction)
    await delete_preset(preset_id=preset_id, conn=db_transaction)
    
    result = await fetch_preset(preset_id=preset_id, conn=db_transaction)
    assert result is None