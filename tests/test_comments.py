import pytest

@pytest.mark.asyncio
async def test_generate_comments_pull(client):
    response = await client.post(
        "/synthetic/comments",
        json={
            "num_comments": 4,
            "post_id": "valid_post_id",
            "seed": 789,
            "mode": "pull"
        },
        cookies={"threadfit_cookie": "valid_token"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["msg"] == "4 comentarios registrados con éxito."
    assert len(data["data"]) == 4
    for comment in data["data"]:
        assert "content" in comment
        assert "post_id" in comment

@pytest.mark.asyncio
async def test_generate_comments_push(client):
    async with client.websocket_connect("/ws/notifications") as websocket:
        response = await client.post(
            "/synthetic/comments",
            json={
                "num_comments": 2,
                "post_id": "valid_post_id",
                "seed": 789,
                "mode": "push"
            },
            cookies={"threadfit_cookie": "valid_token"}
        )
        assert response.status_code == 200
        for _ in range(2):
            msg = await websocket.receive_text()
            assert "Nuevo comentario generado" in msg