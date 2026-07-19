import uuid
import pytest
import httpx
from httpx import ASGITransport
from unittest.mock import patch

from app.main import app
from app.db import prompts as db_prompts

TEST_PROMPT_NAME = "Test Prompt"
TEST_PROMPT_CONTENT = "You are a test assistant."
TEST_PROMPT_ROLE = "system"
TEST_PROMPT_DESCRIPTION = "A test description"

@pytest.mark.asyncio
async def test_create_prompt_endpoint(mock_pool):
    """Tests the POST /api/chat/prompts endpoint."""
    # Patch the get_pool in database layer to use our transactional FakePool
    with patch('app.db.connection.get_pool', return_value=mock_pool):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            payload = {
                "name": TEST_PROMPT_NAME,
                "content": TEST_PROMPT_CONTENT,
                "role": TEST_PROMPT_ROLE,
                "description": TEST_PROMPT_DESCRIPTION
            }
            response = await client.post("/api/chat/prompts", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            
            # Validate response structure
            assert data["name"] == TEST_PROMPT_NAME
            assert data["content"] == TEST_PROMPT_CONTENT
            assert data["role"] == TEST_PROMPT_ROLE
            assert data["description"] == TEST_PROMPT_DESCRIPTION
            assert "id" in data
            
            # Verify it actually wrote to the DB using the transactional connection
            prompt_id = uuid.UUID(data["id"])
            db_prompt = await db_prompts.fetch_prompt(prompt_id, conn=mock_pool.conn)
            assert db_prompt is not None
            assert db_prompt['name'] == TEST_PROMPT_NAME

@pytest.mark.asyncio
async def test_get_prompt_endpoint(mock_pool):
    """Tests the GET /api/chat/prompts/{id} endpoint."""
    # Setup: Directly insert a prompt into our transaction
    prompt_id = await db_prompts.create_prompt(
        name=TEST_PROMPT_NAME,
        content=TEST_PROMPT_CONTENT,
        role=TEST_PROMPT_ROLE,
        description=TEST_PROMPT_DESCRIPTION,
        conn=mock_pool.conn
    )
    
    # Patch the get_pool in database layer to use our transactional FakePool
    with patch('app.db.connection.get_pool', return_value=mock_pool):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/api/chat/prompts/{prompt_id}")
            
            assert response.status_code == 200
            data = response.json()
            
            # Validate structure
            assert data["id"] == str(prompt_id)
            assert data["name"] == TEST_PROMPT_NAME
            assert data["role"] == TEST_PROMPT_ROLE

@pytest.mark.asyncio
async def test_get_prompt_not_found(mock_pool):
    """Tests that fetching a non-existent prompt returns 404."""
    # Patch the get_pool in database layer to use our transactional FakePool
    with patch('app.db.connection.get_pool', return_value=mock_pool):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            random_id = uuid.uuid4()
            response = await client.get(f"/api/chat/prompts/{random_id}")
            
            assert response.status_code == 404
            assert response.json()["detail"] == "Prompt not found"

@pytest.mark.asyncio
async def test_list_prompts_endpoint(mock_pool):
    """Tests the GET /api/chat/prompts endpoint."""
    # Setup: Insert directly into DB using the mock_pool's connection
    await db_prompts.create_prompt(name="First", content="c1", role="system", conn=mock_pool.conn)
    await db_prompts.create_prompt(name="Second", content="c2", role="developer", conn=mock_pool.conn)
    
    # Action: Call the API
    with patch('app.db.connection.get_pool', return_value=mock_pool):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/chat/prompts")
            
            assert response.status_code == 200
            data = response.json()
            
            assert isinstance(data, list)
            assert all(isinstance(item, dict) for item in data)  # Enforces no Record type is returned
            assert len(data) == 2

            names = [p['name'] for p in data]
            assert "First" in names
            assert "Second" in names

@pytest.mark.asyncio
async def test_list_prompts_with_role_filter(mock_pool):
    """Tests the GET /api/chat/prompts endpoint with role filter."""
    # Setup
    await db_prompts.create_prompt(name="Sys1", content="c1", role="system", conn=mock_pool.conn)
    await db_prompts.create_prompt(name="Dev1", content="c2", role="developer", conn=mock_pool.conn)
    
    with patch('app.db.connection.get_pool', return_value=mock_pool):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Filter by system
            response = await client.get("/api/chat/prompts?role=system")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["role"] == "system"
            
            # Filter by developer
            response = await client.get("/api/chat/prompts?role=developer")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["role"] == "developer"

@pytest.mark.asyncio
async def test_update_prompt_endpoint(mock_pool):
    """Tests the PATCH /api/chat/prompts/{id} endpoint."""
    # Setup: Create a prompt to update
    prompt_id = await db_prompts.create_prompt(
        name="Old Name",
        content="Old Content",
        role="system",
        conn=mock_pool.conn
    )
    
    with patch('app.db.connection.get_pool', return_value=mock_pool):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            payload = {"name": "New Name", "description": "New Description"}
            response = await client.patch(f"/api/chat/prompts/{prompt_id}", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            
            # Validate response structure
            assert data["id"] == str(prompt_id)
            assert data["name"] == "New Name"
            assert data["description"] == "New Description"
            assert data["content"] == "Old Content"  # Unchanged
            
            # Verify it actually wrote to the DB
            db_prompt = await db_prompts.fetch_prompt(prompt_id, conn=mock_pool.conn)
            assert db_prompt is not None
            assert db_prompt['name'] == "New Name"

@pytest.mark.asyncio
async def test_update_prompt_not_found(mock_pool):
    """Tests that PATCHing a non-existent prompt returns 404."""
    with patch('app.db.connection.get_pool', return_value=mock_pool):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            random_id = uuid.uuid4()
            payload = {"name": "Doesn't matter"}
            response = await client.patch(f"/api/chat/prompts/{random_id}", json=payload)
            
            assert response.status_code == 404
            assert response.json()["detail"] == "Prompt not found"

@pytest.mark.asyncio
async def test_delete_prompt_endpoint(mock_pool):
    """Tests the DELETE /api/chat/prompts/{id} endpoint."""
    # Setup: Create a prompt to delete
    prompt_id = await db_prompts.create_prompt(
        name="To Delete",
        content="c",
        role="system",
        conn=mock_pool.conn
    )
    
    with patch('app.db.connection.get_pool', return_value=mock_pool):
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.delete(f"/api/chat/prompts/{prompt_id}")
            
            assert response.status_code == 200
            
            # Verify it was actually deleted from the DB
            db_prompt = await db_prompts.fetch_prompt(prompt_id, conn=mock_pool.conn)
            assert db_prompt is None
            
            # Delete again should 404
            response = await client.delete(f"/api/chat/prompts/{prompt_id}")
            assert response.status_code == 404