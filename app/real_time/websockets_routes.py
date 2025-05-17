from __future__ import annotations

from typing import Any, AsyncIterable, Callable, Dict, Final
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status
from fastapi.websockets import WebSocketState
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.main_db import get_db_session
from app.db.models import User
from app.routes import generation_routes
from app.routes.schemas import WSMessage
from app.config import logger, get_settings
from app.services.synthetic_service import (
    create_batch,
    create_fake_user,
    create_fake_post,
    create_fake_comment,
)
from app.db.main_db import async_session
import uuid
import asyncio

settings = get_settings()

MAX_WS_PER_USER: Final[int] = 5
JWT_ALG: Final[str] = settings.JWT_ALGORITHM
COOKIE_NAME: Final[str] = settings.COOKIE_NAME

websocket_router = APIRouter(prefix="/ws", tags=["websockets-generation"])

class ConnectionManager:
    """
    Gestiona el número de conexiones WebSocket activas por usuario.
    Limita a MAX_WS_PER_USER conexiones concurrentes por usuario.
    """
    def __init__(self) -> None:
        self._active: Dict[UUID, int] = {}

    async def connect(self, ws: WebSocket, user_id: UUID) -> None:
        """
        Acepta una nueva conexión si el usuario no ha superado el límite.
        """
        count = self._active.get(user_id, 0)
        if count >= MAX_WS_PER_USER:
            await ws.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        await ws.accept()
        self._active[user_id] = count + 1

    def disconnect(self, user_id: UUID) -> None:
        """
        Elimina una conexión activa del usuario.
        """
        if user_id in self._active:
            self._active[user_id] -= 1
            if self._active[user_id] <= 0:
                self._active.pop(user_id, None)

manager = ConnectionManager()

# Mapeo de acciones a funciones generadoras asíncronas
ActionHandler = Callable[[Dict[str, Any], float], AsyncIterable[Dict[str, Any]]]
ACTION_MAP: Dict[str, ActionHandler] = {
    "generate_users": lambda payload, speed: ws_generate_items(
        amount=payload.get("amount", 1),
        create_fn=create_fake_user,
        batch_id=payload.get("batch_id"),
        batch_check_user_id=payload.get("user_id"),
        speed=speed,
        batch_id=payload.get("batch_id") or str(uuid.uuid4()),
    ),
    "generate_posts": lambda payload, speed: ws_generate_items(
        amount=payload.get("amount", 1),
        create_fn=create_fake_post,
        user_id=payload.get("user_id"),
        batch_id=payload.get("batch_id") or str(uuid.uuid4()),
        batch_check_user_id=payload.get("user_id"),
        speed=speed,
    ),
    "generate_comments": lambda payload, speed: ws_generate_items(
        amount=payload.get("amount", 1),
        create_fn=create_fake_comment,
        user_id=payload.get("user_id"),
        post_id=payload.get("post_id"),
        batch_id=payload.get("batch_id") or str(uuid.uuid4()),
        batch_check_user_id=payload.get("user_id"),
        speed=speed,
    ),
}

@websocket_router.websocket("/generate")
async def websocket_generate(
    ws: WebSocket,
    db: AsyncSession = Depends(get_db_session),
) -> None:
    """
    Endpoint principal para generación sintética vía WebSocket.
    Autentica al usuario, gestiona el ciclo de vida y enruta acciones.
    Espera mensajes con formato: {"action": str, "payload": dict, "speed_multiplier": float}
    """
    user = None
    logger.info("Nueva conexión WebSocket iniciada.")
    try:
        user = await _authenticate_ws(ws, db)
        logger.info(f"Usuario autenticado: {user.id}")
        await manager.connect(ws, user.id)
        logger.info(f"Conexión WebSocket establecida para el usuario {user.id}")

        while True:
            try:
                raw = await ws.receive_json()
                logger.info(f"Mensaje recibido: {raw}")
                msg = WSMessage(**raw)
            except (ValidationError, ValueError) as ve:
                logger.error(f"Error al validar el mensaje: {ve}")
                await ws.send_json({"type": "error", "detail": str(ve)})
                continue
            except WebSocketDisconnect:
                logger.info("WebSocket desconectado por el cliente.")
                break

            handler = ACTION_MAP.get(msg.action)
            if not handler:
                logger.warning(f"Acción desconocida: {msg.action}")
                await ws.send_json(
                    {"type": "error", "detail": f"Acción desconocida: {msg.action}"}
                )
                continue

            await _run_generation(ws, handler, msg)
    except WebSocketDisconnect:
        logger.info("WebSocket desconectado.")
    except Exception as e:
        logger.exception("Error inesperado en WebSocket", exc_info=True)
        if ws.application_state != WebSocketState.DISCONNECTED:
            await ws.close(code=status.WS_1011_INTERNAL_ERROR)
    finally:
        if user:
            manager.disconnect(user.id)
            logger.info(f"Conexión WebSocket cerrada para el usuario {user.id}")

async def _run_generation(
    ws: WebSocket,
    handler: ActionHandler,
    msg: WSMessage,
) -> None:
    """
    Ejecuta la función generadora asociada a la acción y envía mensajes de progreso.
    """
    total = 0
    try:
        async for item in handler(msg.payload, msg.speed_multiplier):
            total += 1
            if ws.application_state == WebSocketState.DISCONNECTED:
                break
            await ws.send_json(
                {
                    "type": "progress",
                    "action": msg.action,
                    "payload": item,
                    "count": total,
                }
            )
        if ws.application_state != WebSocketState.DISCONNECTED:
            await ws.send_json(
                {"type": "completed", "action": msg.action, "total": total}
            )
    except Exception as exc:
        logger.exception("Error durante la generación '%s'", msg.action, exc_info=True)
        if ws.application_state != WebSocketState.DISCONNECTED:
            await ws.send_json(
                {"type": "error", "detail": str(exc), "action": msg.action}
            )

async def _authenticate_ws(ws: WebSocket, db: AsyncSession) -> User:
    """
    Autentica el WebSocket usando el token JWT de la cookie.
    Cierra la conexión si la autenticación falla.
    """
    token = ws.cookies.get(COOKIE_NAME)
    if not token:
        logger.warning("Intento de conexión WebSocket sin token.")
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        raise WebSocketDisconnect()

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[JWT_ALG],
            audience="fastapi-users:auth"
        )
        user_id = payload.get("sub")
        if not user_id:
            raise JWTError("El token no contiene el campo 'sub'.")
        user_id = UUID(user_id)
    except (JWTError, ValueError) as e:
        logger.error(f"Error al decodificar el token JWT: {e}")
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        raise WebSocketDisconnect()

    user = (
        (await db.execute(select(User).where(User.id == user_id)))
        .scalar_one_or_none()
    )
    if not user:
        logger.warning(f"Usuario no encontrado para el ID: {user_id}")
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        raise WebSocketDisconnect()
    return user

async def ws_generate_items(
    amount: int,
    create_fn,
    *args,
    speed: float = 1.0,
    batch_check_user_id: str = None,
    batch_id: str = None,
    **kwargs
):
    if batch_check_user_id and not batch_id:
        batch_id = str(uuid.uuid4())
        async with async_session() as db:
            await create_batch(db, batch_check_user_id)
    for _ in range(amount):
        async with async_session() as db:
            item = await create_fn(db, *args, **kwargs)
        yield item
        await asyncio.sleep(max(0.01, 1.0 / speed))
