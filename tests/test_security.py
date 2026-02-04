from http import HTTPStatus

from jwt import decode
from pytest import mark

from fastapi_zero.models import User
from fastapi_zero.security import (
    settings,
    create_access_token,
    get_current_user,
)


def test_jwt():
    data = {"test": "test"}
    token = create_access_token(data=data)

    decoded = decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)

    assert decoded["test"] == data["test"]
    assert "exp" in decoded


@mark.asyncio
async def test_get_current_user(session, token):
    # data = {"access_token": token, "token_type": "Bearer"}

    user = await get_current_user(session=session, token=token)
    assert User is type(user)


@mark.asyncio
async def test_jwt_invalids_token(client):
    response = await client.delete("/users/1", headers={"Authorization": "Bearer token-invalido"})

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Não pode ser validado esse token chefia"}
