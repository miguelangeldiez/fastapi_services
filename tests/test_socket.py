import uuid
import pytest
import asyncio
from httpx import AsyncClient
from app.config import logger, settings

def get_base_url():
    origins = settings.ALLOWED_ORIGINS
    if isinstance(origins, list):
        return origins[0]
    return origins

@pytest.mark.asyncio
async def test_websocket_generate_users():
    """
    Prueba real de conexión WebSocket al endpoint /ws/generate y generación de usuarios sintéticos.
    """
    base_url = get_base_url().rstrip("/")
    email = f"wsuser_{uuid.uuid4().hex}@example.com"
    password = "securepassword123"

    # 1. Registra y loguea un usuario para obtener la cookie JWT
    async with AsyncClient(base_url=base_url, verify=False) as client:
        reg = await client.post(
            "/auth/register",
            json={"email": email, "password": password, "batch_id": None},
        )
        assert reg.status_code == 201, f"Registro falló: {reg.text}"
        user_id = reg.json().get("data", {}).get("id") or reg.json().get("id")
        assert user_id, "No se obtuvo el id del usuario registrado"

        login = await client.post(
            "/auth/login",
            data={"username": email, "password": password},
        )
        assert login.status_code == 204, f"Login falló: {login.text}"
        cookies = login.cookies

    # 2. Conéctate al WebSocket usando la cookie de autenticación
    ws_url = base_url.replace("http", "ws") + "/ws/generate"
    async with AsyncClient(base_url=base_url, cookies=cookies, verify=False, timeout=10) as client:
        async with client.ws_connect(ws_url) as ws:
            # Envía un mensaje para generar usuarios sintéticos
            await ws.send_json({
                "action": "generate_users",
                "payload": {
                    "amount": 2,
                    "token": "",  # No es necesario, ya va la cookie
                    "user_id": user_id,
                },
                "speed_multiplier": 1.0,
            })

            # Recibe mensajes de progreso y completado
            progress = []
            for _ in range(10):  # Evita bucles infinitos
                try:
                    msg = await asyncio.wait_for(ws.receive_json(), timeout=5)
                except asyncio.TimeoutError:
                    pytest.fail("Timeout esperando mensaje del WebSocket.")
                logger.info(f"Mensaje recibido por WebSocket: {msg}")
                if msg["type"] == "progress":
                    progress.append(msg)
                elif msg["type"] == "completed":
                    assert msg["total"] == 2
                    break
                elif msg["type"] == "error":
                    pytest.fail(f"Error recibido por WebSocket: {msg['detail']}")
            else:
                pytest.fail("No se recibió mensaje de completado en el WebSocket.")

            assert len(progress) == 2
