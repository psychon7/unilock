import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_token_generation():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/auth/token")
        assert response.status_code == 200
        assert "access_token" in response.json()
