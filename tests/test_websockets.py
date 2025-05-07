import pytest

@pytest.mark.asyncio
async def test_websocket_notifications(client):
    async with client.websocket_connect("/ws/notifications") as websocket:
        await websocket.send_text("Test message")
        # No se espera respuesta del servidor, pero se verifica que la conexión no se cierre
        assert websocket.application_state == "CONNECTED"