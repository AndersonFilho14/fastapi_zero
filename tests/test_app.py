from fastapi.testclient import TestClient

from fastapi_zero.app import app


def test_read_root():
    cliente = TestClient(app)
    response = cliente.get("/")
    assert response.json() == {"Message": "Hello World"}
