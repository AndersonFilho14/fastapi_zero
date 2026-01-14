from http import HTTPStatus


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


def test_read_users(client):
    response = client.get("/users/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"users": []}


def test_read_users_with_users(client, user):
    from fastapi_zero.schemas import UserPublic

    user_schema = UserPublic.model_validate(user).model_dump()

    response = client.get("/users/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"users": [user_schema]}


def test_read_user(client, user):
    from fastapi_zero.schemas import UserPublic

    response = client.get("/user/1")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == UserPublic.model_validate(user).model_dump()


def test_update_user(client, user):
    response = client.put(
        "/user/1",
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


def test_update_raise(client):
    response = client.put(
        "/user/0",
        json={
            "username": "mock_update",
            "email": "mock_update@example.com",
            "password": "mock_updatepassword",
        },
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "Encontrei não patrão"}


def test_delete_user(client, user):
    response = client.delete("/user/1")
    assert response.status_code == HTTPStatus.OK


def test_delete_user_raise(client, user):
    response = client.delete("/user/0")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "Encontrei não patrão"}


def test_update_integrity_error(client, user):
    post_result = client.post(
        "/users/",
        json={
            "username": "fausto",
            "email": "fausto@example.com",
            "password": "secret",
        },
    )

    response_update = client.put(
        f"/user/{user.id}",
        json={
            "username": "fausto",
            "email": "bob@example.com",
            "password": "mynewpassword",
        },
    )

    assert response_update.status_code == HTTPStatus.CONFLICT
