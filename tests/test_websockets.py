import asyncio
import uuid
from httpx import AsyncClient
import pytest
import websockets

BASE_URL = "http://localhost:8000"  # Define the base URL
PASSWORD = "secure_password"  # Define a placeholder password

@pytest.mark.asyncio
async def test_websocket_notifications():
    email = f"ws_{uuid.uuid4().hex}@example.com"

    async with AsyncClient(base_url=BASE_URL) as client:
        # Registro + login
        await client.post("/auth/register", json={"email": email, "password": PASSWORD, "batch_id": None})
        login = await client.post("/auth/login", data={"username": email, "password": PASSWORD})
        assert login.status_code == 204, f"Login falló: {login.text}"
        cookie = login.cookies.get("threadfit_cookie")

    # Construir las cabeceras manualmente
    headers = {
        "Cookie": f"threadfit_cookie={cookie}"
    }

    # Conectar al WebSocket
    async with websockets.connect(
        "ws://localhost:8000/ws/notifications",
        extra_headers=[(key, value) for key, value in headers.items()]
    ) as ws:
        # Enviar y recibir mensajes
        await ws.send("Test message")
        response = await ws.recv()
        assert "Bienvenido" in response