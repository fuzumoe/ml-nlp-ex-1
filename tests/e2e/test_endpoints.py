import io
import logging
from http import HTTPStatus
from pathlib import Path

import pytest
from app.backend.endpoints import routes
from fastapi import FastAPI
from fastapi.testclient import TestClient

LOG = logging.getLogger(__name__)


def create_test_app() -> TestClient:
    app = FastAPI()
    app.include_router(routes)
    return TestClient(app)


@pytest.mark.usefixtures("mock_mongo")
def test_post_chat(monkeypatch):
    client = create_test_app()

    def mock_get_response(
        file_name: str,  # noqa: ARG001
        session_id: str,  # noqa: ARG001
        query: str,  # noqa: ARG001
        model: str = "test",  # noqa: ARG001
        temperature: float = 0.0,  # noqa: ARG001
    ) -> dict[str, str | int]:
        return {"answer": "Mocked response", "total_tokens_used": 42}

    monkeypatch.setattr("app.backend.endpoints.get_response", mock_get_response)

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


def test_upload_docx_file_e2e() -> None:
    app = FastAPI()
    app.include_router(routes)
    client = TestClient(app)

    # Load a real DOCX file from testdata
    test_file_path = Path("tests/testdata/sample.docx")
    LOG.debug(f"Test DOCX file path: {test_file_path.absolute()}")
    assert test_file_path.exists(), "Test DOCX file does not exist"

    with test_file_path.open("rb") as f:
        file = (
            "sample.docx",
            io.BytesIO(f.read()),
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

    response = client.post("/uploadFile", files={"data_file": file})

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert "filename" in data
    assert "file_path" in data
    assert data["filename"].endswith(".docx")
    assert data["file_path"].endswith(".docx")
