import pytest

@pytest.mark.asyncio
async def test_get_users_data(client):
    response = await client.get(
        "/data/users",
        params={"batch_id": "valid_batch_id", "format": "json"},
        cookies={"threadfit_cookie": "valid_token"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data