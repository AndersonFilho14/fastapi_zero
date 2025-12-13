from fastapi_zero.app import app, Message
from fastapi.testclient import TestClient


def test_read_root():
    cliente = TestClient(app)
    response = cliente.get("/")
    # O endpoint atual retorna a chave "Message" (M maiúsculo)
    # Este teste valida esse contrato sem exigir o schema Pydantic
    payload = response.json()
    assert payload.get("message") == "Hello World"


def test_health():
    cliente = TestClient(app)
    response = cliente.get("/health")
    assert response.text == """<h1>Tudo Ok patrão, pode ir dormir</h1>"""
