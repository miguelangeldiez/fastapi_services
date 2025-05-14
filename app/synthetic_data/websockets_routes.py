"""WebSocket endpoints de generación de datos en tiempo real (push).

Este módulo expone un único endpoint `/ws/generate` que replica las
funciones de `generation_routes.py`, pero enviando actualizaciones
(push) al cliente conforme se van creando los registros.  Cada mensaje
que recibe el servidor debe cumplir el esquema `WSRequest`:

{
    "action": "generate_users" | "generate_posts" | "generate_comments",
    "payload": { ... },              # parámetros de la generación
    "speed_multiplier": 1.0          # opcional, ralentiza/acelera
}

La respuesta se envía en tiempo real con eventos JSON de tipo
`progress`, `completed` o `error`.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Awaitable, Callable, Dict
from uuid import UUID

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status

# --- Dependencias de la app ---------------------------------------------------
from app.routes.auth_routes import current_active_user # Devuelve `User | None`
from app.db.models import User
from app.synthetic_data.schemas import WSRequest
from app.synthetic_data import generation_routes

logger = logging.getLogger(__name__)

websocket_router = APIRouter(prefix="/ws", tags=["websockets-generation"])


# -----------------------------------------------------------------------------
# Gestor de conexiones (reutilizable en otros módulos)
# -----------------------------------------------------------------------------
class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: Dict[UUID, int] = {}

    async def connect(self, websocket: WebSocket, user_id: UUID) -> None:
        if self.active_connections.get(user_id, 0) >= 5:  # Máximo 5 conexiones por usuario
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        await websocket.accept()
        self.active_connections[user_id] = self.active_connections.get(user_id, 0) + 1

    def disconnect(self, websocket: WebSocket, user_id: UUID) -> None:
        if user_id in self.active_connections:
            self.active_connections[user_id] -= 1
            if self.active_connections[user_id] == 0:
                del self.active_connections[user_id]


manager = ConnectionManager()

# Tipo para el mapeo de acciones → función de generación
ActionHandler = Callable[[Dict[str, Any], float], Awaitable[int]]

# -----------------------------------------------------------------------------
# Mapeo de acciones a funciones de servicio (¡añade aquí las futuras acciones!)
# -----------------------------------------------------------------------------
ACTION_MAP: Dict[str, ActionHandler] = {
    "generate_users": generation_routes.generate_users,
    "generate_posts": generation_routes.generate_posts,
    "generate_comments": generation_routes.generate_comments,
}


# -----------------------------------------------------------------------------
# Endpoint principal
# -----------------------------------------------------------------------------
@websocket_router.websocket("/generate")
async def websocket_generate(
    websocket: WebSocket,
    current_user: User | None = Depends(current_active_user),  # Cookie `threadfit_cookie`
) -> None:
    """Gestiona las peticiones de generación enviadas por WebSocket.

    Si el usuario no está autenticado, cerramos la conexión con código
    1008 (POLICY_VIOLATION).  El cliente debe refrescar su JWT o
    autenticarse por HTTP antes de intentar la conexión.
    """

    if current_user is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(websocket, current_user.id)

    try:
        while True:
            # Esperamos petición del cliente
            data = await websocket.receive_json()
            try:
                req = WSRequest(**data)
            except Exception as exc:  # noqa: BLE001
                await websocket.send_json(
                    {"type": "error", "detail": f"Solicitud inválida: {exc}"}
                )
                continue

            handler = ACTION_MAP.get(req.action)
            if handler is None:
                await websocket.send_json(
                    {"type": "error", "detail": f"Acción '{req.action}' no soportada"}
                )
                continue

            # Lanzamos la generación en segundo plano para no bloquear el loop WS
            asyncio.create_task(
                _run_generation(
                    websocket=websocket,
                    handler=handler,
                    payload=req.payload,
                    speed_multiplier=req.speed_multiplier,
                    action=req.action,
                )
            )

    except WebSocketDisconnect:
        manager.disconnect(websocket)


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
async def _run_generation(
    *,
    websocket: WebSocket,
    handler: ActionHandler,
    payload: Dict[str, Any],
    speed_multiplier: float,
    action: str,
) -> None:
    """Ejecuta la función de generación y envía progreso en tiempo real."""
    try:
        total_created = 0

        # Las funciones de `generation_service` deben ser *async generators*
        # que vayan `yield`‑ando cada elemento creado.
        async for item in handler(payload, speed_multiplier):
            total_created += 1
            await websocket.send_json(
                {
                    "type": "progress",
                    "action": action,
                    "payload": item,
                    "count": total_created,
                }
            )

        await websocket.send_json(
            {"type": "completed", "action": action, "total": total_created}
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Error durante la generación '%s'", action)
        await websocket.send_json(
            {"type": "error", "detail": str(exc), "action": action}
        )
