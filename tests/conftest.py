# tests/conftest.py

import mongomock
import pytest
from app.backend import accessors
from app.backend.config import get_config_variables
from app.backend.endpoints import routes
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def load_test_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_API_BASE", "http://fake.base")
    monkeypatch.setenv("MONGO_URL", "mongodb://mock:27017")
    monkeypatch.setenv("MONGO_DB_NAME", "test-db")
    return get_config_variables()


@pytest.fixture(autouse=True)
def mock_mongo(monkeypatch):
    mock_client = mongomock.MongoClient()
    monkeypatch.setattr(accessors, "get_client", lambda: mock_client)
    monkeypatch.setitem(accessors.MONGO_CLIENT_CACHE, "default", mock_client)


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(routes)
    return TestClient(app)
