import io
import tempfile
from http import HTTPStatus
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from app.backend.chat import get_response
from app.backend.endpoints import routes
from fastapi import FastAPI
from fastapi.testclient import TestClient
from langchain_core.documents import Document


def create_test_app() -> TestClient:
    app = FastAPI()
    app.include_router(routes)
    return TestClient(app)


@pytest.mark.asyncio
@patch("app.backend.endpoints.get_temp_file_path")
@patch("aiofiles.open")
async def test_upload_file_local(mock_aio_open: MagicMock, mock_get_temp_path: MagicMock) -> None:
    client = create_test_app()

    mock_path: Path = Path(tempfile.mkstemp(suffix=".pdf")[1])
    mock_get_temp_path.return_value = mock_path

    # Mock aiofiles
    mock_file: MagicMock = MagicMock()
    mock_cm: MagicMock = MagicMock()
    mock_cm.__aenter__.return_value = mock_file
    mock_aio_open.return_value = mock_cm

    file_content: bytes = b"dummy PDF content"
    file: tuple[str, io.BytesIO, str] = (
        "sample.pdf",
        io.BytesIO(file_content),
        "application/pdf",
    )

    response = client.post("/uploadFile", files={"data_file": file})

    assert response.status_code == HTTPStatus.OK
    data: dict = response.json()
    assert data["filename"].endswith(".pdf")
    assert data["file_path"] == str(mock_path.absolute())


@patch("app.backend.chat.get_openai_callback")
@patch("app.backend.chat.ConversationalRetrievalChain.from_llm")
@patch("app.backend.chat.HuggingFaceEmbeddings")
@patch("app.backend.chat.PyPDFLoader")
def test_get_response_returns_answer(
    pdf_loader_mock: MagicMock,
    embed_mock: MagicMock,
    chain_mock: MagicMock,
    cb_mock: MagicMock,
) -> None:
    # Mock document loader
    pdf_loader_mock.return_value.load.return_value = [
        Document(page_content="This is test content", metadata={"source": "sample"})
    ]

    # Mock embeddings
    embed_mock.return_value.embed_documents.return_value = [[0.1] * 384]

    # Mock chain execution
    mock_chain: MagicMock = MagicMock()
    mock_chain.return_value = {"answer": "Mocked answer"}
    chain_mock.return_value = mock_chain

    cb_context: MagicMock = MagicMock()
    cb_context.__enter__.return_value.total_tokens = 42
    cb_context.__enter__.return_value.prompt_tokens = 10
    cb_context.__enter__.return_value.completion_tokens = 32
    cb_context.__enter__.return_value.total_cost = 0.001
    cb_mock.return_value = cb_context

    response: dict = get_response(
        file_name="sample.pdf",
        session_id="abc123",
        query="What is this?",
    )

    expected_response: dict = {
        "answer": "Mocked answer",
        "total_tokens_used": 42,
        "prompt_tokens_used": 10,
        "completion_tokens_used": 32,
        "total_cost": 0.001,
    }

    assert isinstance(response, dict)
    assert response["answer"] == expected_response["answer"]
    assert response["total_tokens_used"] == expected_response["total_tokens_used"]
