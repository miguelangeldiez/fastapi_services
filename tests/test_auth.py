import pytest

@pytest.mark.asyncio
async def test_register_user(client):
    response = await client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data

@pytest.mark.asyncio
async def test_login_user(client):
    response = await client.post(
        "/auth/jwt/login",
        data={
            "username": "test@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    assert "threadfit_cookie" in response.cookies