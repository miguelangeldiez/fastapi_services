from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable, Dict, Final
from uuid import UUID

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status
from fastapi.websockets import WebSocketState
from jose import JWTError, jwt  # usa **una** sola librería
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.main_db import get_db_session
from app.db.models import User
from app.synthetic_data import generation_routes
from app.synthetic_data.schemas import WSMessage
from config import get_settings

# ──────────────────────────────────────────────
# Configuración global
# ──────────────────────────────────────────────
logger = logging.getLogger(__name__)
settings = get_settings()

MAX_WS_PER_USER: Final[int] = 5
JWT_ALG: Final[str] = "HS256"

websocket_router = APIRouter(prefix="/ws", tags=["websockets-generation"])

# ──────────────────────────────────────────────
# Conexiones
# ──────────────────────────────────────────────
class ConnectionManager:
    def __init__(self) -> None:
        self._active: Dict[UUID, int] = {}

    async def connect(self, ws: WebSocket, user_id: UUID) -> None:
        if self._active.get(user_id, 0) >= MAX_WS_PER_USER:
            await ws.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        await ws.accept()
        self._active[user_id] = self._active.get(user_id, 0) + 1

    def disconnect(self, user_id: UUID) -> None:
        if user_id in self._active:
            self._active[user_id] -= 1
            if self._active[user_id] == 0:
                self._active.pop(user_id, None)


manager = ConnectionManager()

# ──────────────────────────────────────────────
# Mapeo acción → función generadora
# ──────────────────────────────────────────────
ActionHandler = Callable[[Dict[str, Any], float], Awaitable[int]]
ACTION_MAP: Dict[str, ActionHandler] = {
    "generate_users": generation_routes.generate_users,
    "generate_posts": generation_routes.generate_posts,
    "generate_comments": generation_routes.generate_comments,
}

# ──────────────────────────────────────────────
# WebSocket endpoint
# ──────────────────────────────────────────────
@websocket_router.websocket("/generate")
async def websocket_generate(
    ws: WebSocket,
    db: AsyncSession = Depends(get_db_session),
) -> None:
    try:
        user = await _authenticate_ws(ws, db)
        await manager.connect(ws, user.id)

        while True:
            try:
                raw = await ws.receive_json()
                msg = WSMessage(**raw)  # valida
            except (ValidationError, ValueError) as ve:
                await ws.send_json({"type": "error", "detail": str(ve)})
                continue

            handler = ACTION_MAP.get(msg.action)
            if not handler:
                await ws.send_json(
                    {"type": "error", "detail": f"Acción desconocida: {msg.action}"}
                )
                continue

            await _run_generation(ws, handler, msg)
    except WebSocketDisconnect:
        logger.info("WebSocket desconectado")
    except Exception:
        logger.exception("Error inesperado en WebSocket", exc_info=True)
        if ws.application_state != WebSocketState.DISCONNECTED:
            await ws.close(code=status.WS_1011_INTERNAL_ERROR)
    finally:
        manager.disconnect(user.id)


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────
async def _run_generation(
    ws: WebSocket,
    handler: ActionHandler,
    msg: WSMessage,
) -> None:
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
    token = ws.cookies.get("access_token")
    if not token:
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        raise WebSocketDisconnect()

    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[JWT_ALG])
        user_id = payload.get("sub")
        if not user_id:
            raise JWTError("missing sub")
    except JWTError:
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        raise WebSocketDisconnect()

    user = (
        (await db.execute(select(User).where(User.id == user_id)))
        .scalar_one_or_none()
    )
    if not user:
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        raise WebSocketDisconnect()
    return user
