# tests/test_comments.py

import uuid
import pytest
from httpx import AsyncClient
from config import get_settings, logger  # Importa el logger global

settings = get_settings()
PASSWORD = "securepassword123"

@pytest.mark.asyncio
async def test_create_and_list_comments():
    email = f"commenter_{uuid.uuid4().hex}@example.com"
    logger.info(f"Iniciando prueba para crear y listar comentarios con email: {email}")

    async with AsyncClient(base_url=settings.ALLOWED_ORIGINS, verify=False) as client:
        # Registro + login
        logger.info(f"Registrando usuario con email: {email}")
        reg = await client.post(
            "/auth/register",
            json={"email": email, "password": PASSWORD, "batch_id": None},
        )
        logger.info(f"Respuesta del servidor al registro: {reg.status_code} - {reg.text}")
        assert reg.status_code == 201, f"Registro falló: {reg.text}"

        logger.info(f"Iniciando sesión para el usuario: {email}")
        login = await client.post(
            "/auth/login",
            data={"username": email, "password": PASSWORD},
        )
        logger.info(f"Respuesta del servidor al inicio de sesión: {login.status_code}")
        assert login.status_code == 204, f"Login falló: {login.text}"

        # Debug cookies
        logger.info(f"Cookies después del inicio de sesión: {login.cookies}")

        # Set cookies on the client
        client.cookies.update(login.cookies)

        # Crear un post para poder comentar
        logger.info("Creando un post para asociar comentarios.")
        post_resp = await client.post(
            "/posts/create_post",
            json={"title": "Hola", "content": "Cuerpo del post"},
        )
        logger.info(f"Respuesta del servidor al crear el post: {post_resp.status_code} - {post_resp.text}")
        assert post_resp.status_code == 201, post_resp.text
        post_data = post_resp.json()["data"]  # Accede al objeto `data`
        post_id = post_data["id"]
        logger.info(f"Post creado con ID: {post_id}")

        # Crear un comentario
        logger.info("Creando un comentario en el post.")
        comment_resp = await client.post(
            f"/interactions/{post_id}/comments",
            json={"content": "Un comentario"},
        )
        logger.info(f"Respuesta del servidor al crear el comentario: {comment_resp.status_code} - {comment_resp.text}")
        assert comment_resp.status_code == 201, comment_resp.text
        comment_data = comment_resp.json()["data"]  # Accede al objeto `data`
        assert comment_data["content"] == "Un comentario"
        logger.info(f"Comentario creado con éxito: {comment_data}")

        # Listar comentarios
        logger.info("Listando comentarios del post.")
        list_resp = await client.get(f"/interactions/{post_id}/comments")
        logger.info(f"Respuesta del servidor al listar comentarios: {list_resp.status_code} - {list_resp.text}")
        assert list_resp.status_code == 200, list_resp.text
        comments = list_resp.json()
        assert isinstance(comments, list)
        assert any(c["id"] == comment_data["id"] for c in comments)
        logger.info(f"Comentarios listados con éxito. Total: {len(comments)}")
