import asyncio
from uuid import uuid4
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status
from fastapi.websockets import WebSocketState
from config import logger  # Importa el logger global

# Ajusta el import al módulo real donde dejaste el código refactorizado
from app.synthetic_data.websockets_routes import (
    ConnectionManager,
    _run_generation,
    _authenticate_ws,
)

# -----------------------------------------------------------------------------
# Helpers y fixtures
# -----------------------------------------------------------------------------
@pytest.fixture
async def fake_websocket():
    """Crea un WebSocket simulado usando AsyncMock."""
    logger.info("Creando un WebSocket simulado.")
    ws = AsyncMock()
    ws.accept = AsyncMock()
    ws.close = AsyncMock()
    ws.send_json = AsyncMock()
    ws.receive_json = AsyncMock()
    ws.cookies = {}
    ws.application_state = WebSocketState.CONNECTED
    return ws


class _FakeResult:
    """Imita el resultado de Session.execute."""

    def __init__(self, user):
        self._user = user

    def scalar_one_or_none(self):
        return self._user


@pytest.fixture
async def fake_db_session():
    logger.info("Creando una sesión de base de datos simulada.")
    class _FakeSession:
        async def execute(self, *_):
            logger.info("Ejecutando consulta simulada en la base de datos.")
            return _FakeResult(user={"id": "user-123"})

    return _FakeSession()


# -----------------------------------------------------------------------------
# Tests ConnectionManager
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_connection_limit(fake_websocket):
    logger.info("Iniciando prueba para verificar el límite de conexiones.")
    cm = ConnectionManager()
    user_id = uuid4()

    websockets = [AsyncMock(**fake_websocket.__dict__) for _ in range(5)]
    for ws in websockets:
        await cm.connect(ws, user_id)
        logger.info(f"Conexión establecida para el usuario {user_id}.")

    assert cm._active[user_id] == 5
    logger.info(f"El usuario {user_id} tiene 5 conexiones activas.")

    sixth_ws = AsyncMock(**fake_websocket.__dict__)
    await cm.connect(sixth_ws, user_id)
    sixth_ws.close.assert_called_with(code=status.WS_1008_POLICY_VIOLATION)
    logger.info(f"Se rechazó la sexta conexión para el usuario {user_id}.")


@pytest.mark.asyncio
async def test_disconnect_decrements(fake_websocket):
    logger.info("Iniciando prueba para verificar la desconexión.")
    cm = ConnectionManager()
    user_id = uuid4()

    await cm.connect(fake_websocket, user_id)
    logger.info(f"Conexión establecida para el usuario {user_id}.")
    assert cm._active[user_id] == 1

    cm.disconnect(user_id)
    logger.info(f"Conexión desconectada para el usuario {user_id}.")
    assert user_id not in cm._active


# -----------------------------------------------------------------------------
# Tests _run_generation
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_run_generation_progress_and_complete(fake_websocket):
    logger.info("Iniciando prueba para verificar el progreso y la finalización de la generación.")

    async def dummy_handler(payload, speed):
        for i in range(3):
            logger.info(f"Generando elemento {i}.")
            yield {"n": i}
            await asyncio.sleep(0)

    class _Msg:
        action = "generate_users"
        payload = {}
        speed_multiplier = 1.0

    await _run_generation(fake_websocket, dummy_handler, _Msg)

    assert fake_websocket.send_json.call_count == 4
    logger.info("Se enviaron 4 mensajes JSON al WebSocket.")
    fake_websocket.send_json.assert_any_call(
        {"type": "completed", "action": _Msg.action, "total": 3}
    )
    logger.info("La generación se completó con éxito.")


# -----------------------------------------------------------------------------
# Tests _authenticate_ws
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_authenticate_success(fake_websocket, fake_db_session):
    logger.info("Iniciando prueba para verificar la autenticación exitosa.")
    fake_websocket.cookies = {"access_token": "valid.jwt.token"}

    with patch("jose.jwt.decode", return_value={"sub": "user-123"}):
        user = await _authenticate_ws(fake_websocket, fake_db_session)

    assert user["id"] == "user-123"
    logger.info(f"Autenticación exitosa para el usuario {user['id']}.")


@pytest.mark.asyncio
async def test_authenticate_missing_token(fake_websocket, fake_db_session):
    logger.info("Iniciando prueba para verificar la autenticación sin token.")
    fake_websocket.cookies = {}

    with pytest.raises(Exception):
        await _authenticate_ws(fake_websocket, fake_db_session)
    fake_websocket.close.assert_called_with(code=status.WS_1008_POLICY_VIOLATION)
    logger.info("Se rechazó la conexión debido a la falta de token.")


@pytest.mark.asyncio
async def test_authenticate_invalid_token(fake_websocket, fake_db_session):
    logger.info("Iniciando prueba para verificar la autenticación con token inválido.")
    fake_websocket.cookies = {"access_token": "invalid"}

    from jose import JWTError
    with patch("jose.jwt.decode", side_effect=JWTError("bad token")):
        with pytest.raises(Exception):
            await _authenticate_ws(fake_websocket, fake_db_session)
        fake_websocket.close.assert_called_with(code=status.WS_1008_POLICY_VIOLATION)
    logger.info("Se rechazó la conexión debido a un token inválido.")
