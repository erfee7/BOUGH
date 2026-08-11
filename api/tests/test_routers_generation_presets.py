import uuid
import pytest
import httpx
from httpx import ASGITransport
from unittest.mock import patch

from app.main import app
from app.db import generation_presets as db_presets

_TEST_PRESET_NAME = "Test Preset"
_TEST_MODEL = "test-model"
_TEST_PARAMETERS = {"temperature": 0.5, "reasoning": {"effort": "low"}}

@pytest.mark.asyncio
async def test_create_preset_endpoint(mock_pool):
    """Tests the POST /api/chat/presets endpoint."""
    # Patch the get_pool in database layer to use our transactional FakePool
    with patch('app.db.connection.get_pool', return_value=mock_pool):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            payload = {
                "name": _TEST_PRESET_NAME,
                "model": _TEST_MODEL,
                "parameters": _TEST_PARAMETERS
            }
            response = await client.post("/api/chat/presets", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            
            # Validate response structure
            assert data["name"] == _TEST_PRESET_NAME
            assert data["model"] == _TEST_MODEL
            assert data["parameters"] == _TEST_PARAMETERS
            assert "id" in data
            
            # Verify it actually wrote to the DB using the transactional connection
            preset_id = uuid.UUID(data["id"])
            db_preset = await db_presets.fetch_preset(preset_id, conn=mock_pool.conn)
            assert db_preset is not None
            assert db_preset['name'] == _TEST_PRESET_NAME

@pytest.mark.asyncio
async def test_create_preset_defaults(mock_pool):
    """Tests that creating a preset with no model/parameters defaults correctly."""
    with patch('app.db.connection.get_pool', return_value=mock_pool):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            payload = {"name": "Defaults Test"}
            response = await client.post("/api/chat/presets", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["model"] is None
            assert data["parameters"] == {}

@pytest.mark.asyncio
async def test_get_preset_endpoint(mock_pool):
    """Tests the GET /api/chat/presets/{id} endpoint."""
    preset_id = await db_presets.create_preset(
        name=_TEST_PRESET_NAME,
        model=_TEST_MODEL,
        parameters=_TEST_PARAMETERS,
        conn=mock_pool.conn
    )
    
    with patch('app.db.connection.get_pool', return_value=mock_pool):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/api/chat/presets/{preset_id}")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["id"] == str(preset_id)
            assert data["name"] == _TEST_PRESET_NAME
            assert data["model"] == _TEST_MODEL
            assert data["parameters"] == _TEST_PARAMETERS

@pytest.mark.asyncio
async def test_get_preset_not_found(mock_pool):
    """Tests that fetching a non-existent preset returns 404."""
    with patch('app.db.connection.get_pool', return_value=mock_pool):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            random_id = uuid.uuid4()
            response = await client.get(f"/api/chat/presets/{random_id}")
            
            assert response.status_code == 404
            assert response.json()["detail"] == "Generation preset not found"

@pytest.mark.asyncio
async def test_list_presets_endpoint(mock_pool):
    """Tests the GET /api/chat/presets endpoint."""
    await db_presets.create_preset(name="First", model="m1", parameters={}, conn=mock_pool.conn)
    await db_presets.create_preset(name="Second", model="m2", parameters={"top_p": 0.9}, conn=mock_pool.conn)
    
    with patch('app.db.connection.get_pool', return_value=mock_pool):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/chat/presets")
            
            assert response.status_code == 200
            data = response.json()
            
            assert isinstance(data, list)
            assert all(isinstance(item, dict) for item in data)
            assert len(data) == 2

            names = [p['name'] for p in data]
            assert "First" in names
            assert "Second" in names

@pytest.mark.asyncio
async def test_update_preset_endpoint(mock_pool):
    """Tests the PATCH /api/chat/presets/{id} endpoint."""
    preset_id = await db_presets.create_preset(
        name="Old Name",
        model="Old Model",
        parameters={},
        conn=mock_pool.conn
    )
    
    with patch('app.db.connection.get_pool', return_value=mock_pool):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            payload = {"name": "New Name", "parameters": {"temperature": 0.8}}
            response = await client.patch(f"/api/chat/presets/{preset_id}", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["id"] == str(preset_id)
            assert data["name"] == "New Name"
            assert data["parameters"] == {"temperature": 0.8}
            assert data["model"] == "Old Model"  # Unchanged
            
            # Verify it actually wrote to the DB
            db_preset = await db_presets.fetch_preset(preset_id, conn=mock_pool.conn)
            assert db_preset is not None
            assert db_preset['name'] == "New Name"

@pytest.mark.asyncio
async def test_update_preset_not_found(mock_pool):
    """Tests that PATCHing a non-existent preset returns 404."""
    with patch('app.db.connection.get_pool', return_value=mock_pool):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            random_id = uuid.uuid4()
            payload = {"name": "Doesn't matter"}
            response = await client.patch(f"/api/chat/presets/{random_id}", json=payload)
            
            assert response.status_code == 404
            assert response.json()["detail"] == "Generation preset not found"

@pytest.mark.asyncio
async def test_delete_preset_endpoint(mock_pool):
    """Tests the DELETE /api/chat/presets/{id} endpoint."""
    preset_id = await db_presets.create_preset(
        name="To Delete",
        model="m1",
        parameters={},
        conn=mock_pool.conn
    )
    
    with patch('app.db.connection.get_pool', return_value=mock_pool):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete(f"/api/chat/presets/{preset_id}")
            
            assert response.status_code == 200
            
            # Verify it was actually deleted from the DB
            db_preset = await db_presets.fetch_preset(preset_id, conn=mock_pool.conn)
            assert db_preset is None
            
            # Delete again should 404
            response = await client.delete(f"/api/chat/presets/{preset_id}")
            assert response.status_code == 404