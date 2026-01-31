from http import HTTPStatus

import pytest

from fastapi_zero.schemas import UserPublic


@pytest.mark.asyncio
async def test_create_user(client):
    body = {
        "username": "string",
        "email": "user@example.com",
        "password": "testpassword",
    }

    response = await client.post("/users/", json=body)

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        "id": 1,
        "username": body["username"],
        "email": body["email"],
    }


@pytest.mark.asyncio
async def test_read_users(client, user, token):

    user_schema = UserPublic.model_validate(user).model_dump()

    response = await client.get("/users/", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"users": [user_schema]}


@pytest.mark.asyncio
async def test_read_user(client, user):
    from fastapi_zero.schemas import UserPublic

    response = await client.get("/users/1")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == UserPublic.model_validate(user).model_dump()


@pytest.mark.asyncio
async def test_update_user(client, user, token):
    response = await client.put(
        f"/users/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "mock_update",
            "email": "mock_update@example.com",
            "password": "mock_updatepassword",
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "id": 1,
        "username": "mock_update",
        "email": "mock_update@example.com",
    }


@pytest.mark.asyncio
async def test_update_raise(client, token):
    response = await client.put(
        "/users/0",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "mock_update",
            "email": "mock_update@example.com",
            "password": "mock_updatepassword",
        },
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {"detail": "Não tem permissão pra isso cumpade"}


@pytest.mark.asyncio
async def test_delete_user(client, user, token):
    response = await client.delete(
        f"/users/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.OK


@pytest.mark.asyncio
async def test_update_integrity_error(client, user, token):
    client.post(
        "/users/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "fausto",
            "email": "fausto@example.com",
            "password": "secret",
        },
    )

    response_update = client.put(
        f"/users/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "fausto",
            "email": "bob@example.com",
            "password": "mynewpassword",
        },
    )

    assert response_update.status_code == HTTPStatus.CONFLICT
