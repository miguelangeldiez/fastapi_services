# tests/test_auth.py

import uuid
import pytest
from httpx import AsyncClient
import os

from config import get_settings, logger  # Importa el logger global

settings = get_settings()
PASSWORD = "securepassword123"

# Verificar que la variable de entorno ALLOWED_ORIGINS esté configurada correctamente

@pytest.mark.asyncio
async def test_register_user():
    email = f"testregister_{uuid.uuid4().hex}@example.com"
    logger.info(f"Iniciando prueba de registro de usuario con email: {email}")
    async with AsyncClient(base_url=settings.ALLOWED_ORIGINS, verify=False) as client:
        payload = {
            "email": email,
            "password": PASSWORD,
        }
        logger.info(f"Enviando solicitud de registro con payload: {payload}")
        response = await client.post("/auth/register", json=payload)
    logger.info(f"Respuesta del servidor: {response.status_code} - {response.text}")
    assert response.status_code == 201, response.text
    data = response.json()
    logger.info(f"Datos recibidos: {data}")
    assert data["email"] == email
    assert "id" in data
    logger.info("Prueba de registro de usuario completada con éxito.")

@pytest.mark.asyncio
async def test_login_user():
    email = f"testlogin_{uuid.uuid4().hex}@example.com"
    logger.info(f"Iniciando prueba de inicio de sesión con email: {email}")
    async with AsyncClient(base_url=settings.ALLOWED_ORIGINS, verify=False) as client:
        # 1) Registro
        logger.info(f"Registrando usuario con email: {email}")
        reg = await client.post(
            "/auth/register",
            json={"email": email, "password": PASSWORD },
        )
        logger.info(f"Respuesta del servidor al registro: {reg.status_code} - {reg.text}")
        assert reg.status_code == 201, f"Registro falló: {reg.text}"

        # 2) Login (envío form‐data)
        logger.info(f"Iniciando sesión para el usuario: {email}")
        login = await client.post(
            "/auth/login",
            data={"username": email, "password": PASSWORD},
        )
        logger.info(f"Respuesta del servidor al inicio de sesión: {login.status_code}")
    # FastAPI-Users responde 204 No Content al hacer login por cookie
    assert login.status_code == 204, login.text
    assert "threadfit_cookie" in login.cookies
    logger.info("Inicio de sesión completado con éxito.")
