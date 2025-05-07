# filepath: tests/test_users.py
import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_generate_users_pull(client):
    response = await client.post(
        "/synthetic/users",
        json={
            "num_users": 5,
            "seed": 123,
            "mode": "pull"
        },
        cookies={"threadfit_cookie": "valid_token"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["msg"] == "5 usuarios registrados con éxito."
    assert len(data["data"]) == 5
    for user in data["data"]:
        assert "email" in user
        assert "password" in user

@pytest.mark.asyncio
async def test_generate_users_push(client):
    async with client.websocket_connect("/ws/notifications") as websocket:
        response = await client.post(
            "/synthetic/users",
            json={
                "num_users": 2,
                "seed": 123,
                "mode": "push"
            },
            cookies={"threadfit_cookie": "valid_token"}
        )
        assert response.status_code == 200
        for _ in range(2):
            msg = await websocket.receive_text()
            assert "Nuevo usuario generado" in msg