from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict

websocket_router = APIRouter(prefix="/ws", tags=["WebSockets"])

# Lista para almacenar conexiones activas
active_connections: List[WebSocket] = []

# Diccionario para almacenar conexiones por usuario
user_connections: Dict[str, List[WebSocket]] = {}

# Función para conectar un cliente
async def connect_client(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)

# Función para desconectar un cliente
def disconnect_client(websocket: WebSocket):
    active_connections.remove(websocket)

# Función para enviar mensajes a todos los clientes conectados
async def broadcast_message(message: str):
    for connection in active_connections:
        await connection.send_text(message)

# Función para enviar mensajes a un usuario específico
async def broadcast_to_user(user_id: str, message: str):
    if user_id in user_connections:
        for connection in user_connections[user_id]:
            await connection.send_text(message)

# Endpoint WebSocket
@websocket_router.websocket("/notifications")
async def websocket_endpoint(websocket: WebSocket):
    await connect_client(websocket)
    try:
        # Enviar un mensaje inicial al cliente
        await websocket.send_text("Bienvenido al servidor de notificaciones")
        while True:
            # Escucha mensajes del cliente (si es necesario)
            data = await websocket.receive_text()
            print(f"Mensaje recibido del cliente: {data}")
    except WebSocketDisconnect:
        disconnect_client(websocket)