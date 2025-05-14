# tests/test_posts.py

import uuid
import pytest
from httpx import AsyncClient
import os

from config import get_settings

settings = get_settings()
PASSWORD = "securepassword123"

# Example for test_create_post
@pytest.mark.asyncio
async def test_create_post():
    email = f"poster_{uuid.uuid4().hex}@example.com"

    async with AsyncClient(base_url=settings.ALLOWED_ORIGINS, verify=False) as client:
        # Registro + login
        reg = await client.post(
            "/auth/register",
            json={"email": email, "password": PASSWORD, "batch_id": None},
        )
        assert reg.status_code == 201, f"Registro falló: {reg.text}"

        login = await client.post(
            "/auth/login",
            data={"username": email, "password": PASSWORD},
        )
        assert login.status_code == 204, f"Login falló: {login.text}"

        # Set cookies on the client
        client.cookies.update(login.cookies)

        # Crear post
        resp = await client.post(
            "/posts/create_post",
            json={"title": "Mi título", "content": "Contenido chulo"},
        )
        print("Post creation response:", resp.status_code, resp.json())
    assert resp.status_code == 201, resp.text
    data = resp.json()["data"] # Accede al objeto `data`
    assert data["title"] == "Mi título"
    assert data["content"] == "Contenido chulo"

@pytest.mark.asyncio
async def test_list_posts():
    email = f"poster2_{uuid.uuid4().hex}@example.com"

    async with AsyncClient(base_url=settings.ALLOWED_ORIGINS, verify=False) as client:
        # Registro + login
        reg = await client.post(
            "/auth/register",
            json={"email": email, "password": PASSWORD, "batch_id": None},
        )
        assert reg.status_code == 201, f"Registro falló: {reg.text}"

        login = await client.post(
            "/auth/login",
            data={"username": email, "password": PASSWORD},
        )
        assert login.status_code == 204, f"Login falló: {login.text}"
        cookies = login.cookies

        # Listar posts paginados
        client.cookies.update(cookies)  # Configura las cookies en el cliente
        resp = await client.get("/posts/all_posts?page=1&per_page=10")
    assert resp.status_code == 200, resp.text
    page = resp.json()
    # Debe devolver un dict con items y metadatos
    assert isinstance(page, dict)
    assert "posts" in page and isinstance(page["posts"], list)
    assert page["current_page"] == 1
