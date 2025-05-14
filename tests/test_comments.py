# tests/test_comments.py

import uuid
import pytest
from httpx import AsyncClient
import os

allowed_origins = os.getenv("ALLOWED_ORIGINS", "")
PASSWORD = "securepassword123"

@pytest.mark.asyncio
async def test_create_and_list_comments():
    email = f"commenter_{uuid.uuid4().hex}@example.com"

    async with AsyncClient(base_url=allowed_origins) as client:
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

        # Debug cookies
        print("Cookies after login:", login.cookies)

        # Set cookies on the client
        client.cookies.update(login.cookies)

        # Crear un post para poder comentar
        post_resp = await client.post(
            "/posts/create_post",
            json={"title": "Hola", "content": "Cuerpo del post"},
        )
        assert post_resp.status_code == 201, post_resp.text
        post_data = post_resp.json()["data"]  # Accede al objeto `data`
        post_id = post_data["id"]

        # Crear un comentario
        comment_resp = await client.post(
            f"/interactions/{post_id}/comments",
            json={"content": "Un comentario"},
        )
        assert comment_resp.status_code == 201, comment_resp.text
        comment_data = comment_resp.json()["data"]  # Accede al objeto `data`
        assert comment_data["content"] == "Un comentario"

        # Listar comentarios
        list_resp = await client.get(f"/interactions/{post_id}/comments")
        assert list_resp.status_code == 200, list_resp.text
        comments = list_resp.json()
        assert isinstance(comments, list)
        assert any(c["id"] == comment_data["id"] for c in comments)
