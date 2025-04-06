import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_domain_creation():
    test_domain = {
        "name": "test-realm",
        "display_name": "Test Realm"
    }
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Test domain creation
        response = await ac.post("/domains", json=test_domain)
        assert response.status_code == 201
        assert response.json()["name"] == test_domain["name"]
        
        # Test domain retrieval
        get_response = await ac.get(f"/domains/{test_domain['name']}")
        assert get_response.status_code == 200
        assert get_response.json()["display_name"] == test_domain["display_name"]

@pytest.mark.asyncio
async def test_domain_listing():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/domains")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
