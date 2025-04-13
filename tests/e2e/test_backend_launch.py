from http import HTTPStatus

from app.backend.endpoints import routes
from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_health_check():
    app = FastAPI()
    app.include_router(routes)
    client = TestClient(app)

    response = client.get("/health")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"status": "ok"}
