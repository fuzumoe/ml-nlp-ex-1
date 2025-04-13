# tests/conftest.py

import mongomock
import pytest
from app.backend.config import get_config_variables
from app.backend.endpoints import routes
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture(scope="session", autouse=True)
def load_test_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_API_BASE", "http://fake.base")
    monkeypatch.setenv("MONGO_URL", "mongodb://localhost:27017")
    monkeypatch.setenv("MONGO_DB_NAME", "test-db")
    return get_config_variables()


@pytest.fixture(autouse=True)
def mock_mongo(monkeypatch):
    from app.backend import accessors

    mock_client = mongomock.MongoClient()
    monkeypatch.setattr(accessors, "get_client", lambda: mock_client)
    monkeypatch.setattr(accessors, "_mongo_client_cache", {"default": mock_client})
    yield
    mock_client.close()


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(routes)
    return TestClient(app)
