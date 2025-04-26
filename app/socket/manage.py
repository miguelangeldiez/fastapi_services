from fastapi import WebSocket
from typing import List

class ConnectionManager:
    """
    Clase para gestionar las conexiones WebSocket.
    """
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """
        Envía un mensaje a todos los clientes conectados.
        """
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)


# Instancia del gestor de conexiones
manager = ConnectionManager()


async def notify_new_like(post_id: str, user_id: str):
    """
    Notifica a los clientes sobre un nuevo like.
    """
    message = {
        "event": "new_like",
        "post_id": post_id,
        "user_id": user_id,
    }
    await manager.broadcast(message)


async def notify_new_comment(post_id: str, comment_id: str, user_id: str):
    """
    Notifica a los clientes sobre un nuevo comentario.
    """
    message = {
        "event": "new_comment",
        "post_id": post_id,
        "comment_id": comment_id,
        "user_id": user_id,
    }
    await manager.broadcast(message)