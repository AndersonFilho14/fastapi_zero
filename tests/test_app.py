from http import HTTPStatus

from fastapi_zero.schemas import UserPublic


def test_read_root(client):
    response = client.get("/")
    # O endpoint atual retorna a chave "Message" (M maiúsculo)
    # Este teste valida esse contrato sem exigir o schema Pydantic
    payload = response.json()
    assert payload.get("message") == "Hello World"


def test_health(client):
    response = client.get("/health")
    assert response.text == """<h1>Tudo Ok patrão, pode ir dormir</h1>"""


def test_create_user(client):
    body = {
        "username": "string",
        "email": "user@example.com",
        "password": "testpassword",
    }

    response = client.post("/users/", json=body)

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        "id": 1,
        "username": body["username"],
        "email": body["email"],
    }


def test_read_users(client, user, token):

    user_schema = UserPublic.model_validate(user).model_dump()

    response = client.get(
        "/users/", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"users": [user_schema]}


def test_read_user(client, user):
    from fastapi_zero.schemas import UserPublic

    response = client.get("/user/1")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == UserPublic.model_validate(user).model_dump()


def test_update_user(client, user, token):
    response = client.put(
        f"/user/{user.id}",
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


def test_update_raise(client, token):
    response = client.put(
        "/user/0",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "mock_update",
            "email": "mock_update@example.com",
            "password": "mock_updatepassword",
        },
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {"detail": "Não tem permissão pra isso cumpade"}


def test_delete_user(client, user, token):
    response = client.delete(
        f"/user/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == HTTPStatus.OK


def test_update_integrity_error(client, user, token):
    post_result = client.post(
        "/users/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "fausto",
            "email": "fausto@example.com",
            "password": "secret",
        },
    )

    response_update = client.put(
        f"/user/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "fausto",
            "email": "bob@example.com",
            "password": "mynewpassword",
        },
    )

    assert response_update.status_code == HTTPStatus.CONFLICT


def test_get_token(client, user):

    response = client.post(
        "/token",
        data={"username": user.email, "password": user.clean_password},
    )

    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert token["token_type"] == "Bearer"
    assert "token_type" in token
