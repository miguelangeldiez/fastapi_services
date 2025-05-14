# tests/test_auth.py

import uuid
import pytest
from httpx import AsyncClient
import os

from config import get_settings

settings = get_settings()
PASSWORD = "securepassword123"

# Verificar que la variable de entorno ALLOWED_ORIGINS esté configurada correctamente

@pytest.mark.asyncio
async def test_register_user():
    email = f"testregister_{uuid.uuid4().hex}@example.com"
    async with AsyncClient(base_url=settings.ALLOWED_ORIGINS, verify=False) as client:
        payload = {
            "email": email,
            "password": PASSWORD,
        }
        response = await client.post("/auth/register", json=payload)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["email"] == email
    assert "id" in data

@pytest.mark.asyncio
async def test_login_user():
    email = f"testlogin_{uuid.uuid4().hex}@example.com"
    async with AsyncClient(base_url=settings.ALLOWED_ORIGINS, verify=False) as client:
        # 1) Registro
        reg = await client.post(
            "/auth/register",
            json={"email": email, "password": PASSWORD },
        )
        assert reg.status_code == 201, f"Registro falló: {reg.text}"

        # 2) Login (envío form‐data)
        login = await client.post(
            "/auth/login",
            data={"username": email, "password": PASSWORD},
        )
    # FastAPI-Users responde 204 No Content al hacer login por cookie
    assert login.status_code == 204, login.text
    assert "threadfit_cookie" in login.cookies
