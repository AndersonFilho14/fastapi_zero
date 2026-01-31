from http import HTTPStatus

import pytest


@pytest.mark.asyncio
async def test_get_token(client, user) -> None:

    response = await client.post(
        "/auth/token",
        data={"username": user.email, "password": user.clean_password},
    )

    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert token["token_type"] == "Bearer"
    assert "token_type" in token
