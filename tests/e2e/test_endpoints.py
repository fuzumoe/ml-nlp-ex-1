# tests/unit/test_chat_endpoint.py

from http import HTTPStatus

from app.backend import chat
from app.backend.endpoints import routes
from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_post_chat(monkeypatch):
    app = FastAPI()
    app.include_router(routes)
    client = TestClient(app)

    # Mock get_response
    def mock_get_response(
        file_name: str,  # noqa: ARG001
        session_id: str,  # noqa: ARG001
        query: str,  # noqa: ARG001
        model: str = "test",  # noqa: ARG001
        temperature: float = 0.0,  # noqa: ARG001
    ) -> dict[str, str | int]:
        return {"answer": "Mocked response", "total_tokens_used": 42}

    monkeypatch.setattr(chat, "get_response", mock_get_response)

    payload = {
        "session_id": "test-session",
        "user_input": "What is this?",
        "data_source": "sample.pdf",
    }

    response = client.post("/chat", json=payload)

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert "response" in data
    assert data["response"]["answer"] == "Mocked response"
    assert data["session_id"] == "test-session"
