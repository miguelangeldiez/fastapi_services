import pytest

@pytest.mark.asyncio
async def test_generate_posts_pull(client):
    response = await client.post(
        "/synthetic/posts",
        json={
            "num_posts": 3,
            "user_id": "valid_user_id",
            "seed": 456,
            "mode": "pull"
        },
        cookies={"threadfit_cookie": "valid_token"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["msg"] == "3 publicaciones registradas con éxito."
    assert len(data["data"]) == 3
    for post in data["data"]:
        assert "title" in post
        assert "content" in post

@pytest.mark.asyncio
async def test_generate_posts_push(client):
    async with client.websocket_connect("/ws/notifications") as websocket:
        response = await client.post(
            "/synthetic/posts",
            json={
                "num_posts": 2,
                "user_id": "valid_user_id",
                "seed": 456,
                "mode": "push"
            },
            cookies={"threadfit_cookie": "valid_token"}
        )
        assert response.status_code == 200
        for _ in range(2):
            msg = await websocket.receive_text()
            assert "Nueva publicación generada" in msg