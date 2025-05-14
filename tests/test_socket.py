import asyncio
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from starlette.websockets import WebSocketDisconnect

from app.synthetic_data.websockets_routes import ACTION_MAP
import os

allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:8000")

# ---------- Fixtures ------------------------------------------------------------------

@pytest.fixture
async def ws_client() -> AsyncGenerator:
    async with AsyncClient(base_url=allowed_origins, verify=False) as client:
        async with client.websocket_connect("/ws/generate") as ws:
            yield ws
            
# ---------- Mocks ---------------------------------------------------------------------

class _DummyGen:
    """Simula generate_users/posts/comments → produce 3 items."""

    def __init__(self, name: str):
        self.name = name

    async def __call__(self, payload, speed_multiplier):
        for i in range(3):
            await asyncio.sleep(0)   # cede al loop
            yield {"idx": i, "payload": payload}


@pytest.fixture(autouse=True)
def monkeypatch_generations(monkeypatch):
    for action in ("generate_users", "generate_posts", "generate_comments"):
        monkeypatch.setitem(ACTION_MAP, action, _DummyGen(action))
    yield


# ---------- Tests ---------------------------------------------------------------------

@pytest.mark.asyncio
async def test_valid_action(ws_client):
    await ws_client.send_json(
        {"action": "generate_users", "payload": {"amount": 3}, "speed_multiplier": 1}
    )

    items = []
    async for _ in range(4):  # 3 progress + 1 completed
        msg = await ws_client.receive_json()
        items.append(msg["type"])

    assert items.count("progress") == 3
    assert "completed" in items


@pytest.mark.asyncio
async def test_invalid_action(ws_client):
    await ws_client.send_json({"action": "bad_action", "payload": {}, "speed_multiplier": 1})
    msg = await ws_client.receive_json()
    assert msg["type"] == "error"
    assert "no soportada" in msg["detail"]


@pytest.mark.asyncio
async def test_no_auth_closes():
    async with AsyncClient(base_url=allowed_origins, verify=False) as client:
        with pytest.raises(WebSocketDisconnect) as exc_info:
            async with client.websocket_connect("/ws/generate"):
                pass
    assert exc_info.value.code == 1008
