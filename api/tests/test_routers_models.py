import pytest
import httpx
from httpx import ASGITransport
from unittest.mock import patch, AsyncMock

from app.main import app

@pytest.mark.asyncio
async def test_get_models_endpoint():
    """Tests the GET /api/chat/models endpoint."""
    mock_models = [
        {"id": "test-model-1", "name": "Test Model 1"},
        {"id": "test-model-2", "name": "Test Model 2"}
    ]
    
    with patch('app.routers.models.list_models', new_callable=AsyncMock) as mock_list_models:
        mock_list_models.return_value = mock_models
        
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/chat/models")
            
            assert response.status_code == 200
            data = response.json()
            
            assert isinstance(data, list)
            assert len(data) == 2
            assert data[0]["id"] == "test-model-1"
            assert data[0]["name"] == "Test Model 1"
            assert data[1]["id"] == "test-model-2"
            assert data[1]["name"] == "Test Model 2"

@pytest.mark.asyncio
async def test_get_models_endpoint_failure():
    """Tests that a provider fetch failure results in a 502 error."""
    with patch('app.routers.models.list_models', new_callable=AsyncMock) as mock_list_models:
        mock_list_models.side_effect = Exception("Network Error")
        
        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/chat/models")
            
            assert response.status_code == 502
            assert "Failed to fetch models" in response.json()["detail"]