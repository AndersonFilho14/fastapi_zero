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
