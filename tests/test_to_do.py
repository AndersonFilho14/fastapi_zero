import pytest

@pytest.mark.asyncio
async def test_create_todo(client, token):
    response = await client.post(
        "/to_dos/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Test todo",
            "description": "Test todo description",
            "state": "draft",
        },
    )
    assert response.json() == {
        "id": 1,
        "title": "Test todo",
        "description": "Test todo description",
        "state": "draft",
    }
