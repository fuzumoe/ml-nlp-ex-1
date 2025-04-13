from unittest.mock import MagicMock, patch

from app.backend.chat import get_response
from langchain_core.documents import Document


@patch("app.backend.chat.get_openai_callback")
@patch("app.backend.chat.ConversationalRetrievalChain.from_llm")
@patch("app.backend.chat.HuggingFaceEmbeddings")
@patch("app.backend.chat.PyPDFLoader")
def test_get_response_returns_answer(pdf_loader_mock, embed_mock, chain_mock, cb_mock):
    # Mock document loader
    pdf_loader_mock.return_value.load.return_value = [
        Document(page_content="This is test content", metadata={"source": "sample"})
    ]

    # Mock embeddings
    embed_mock.return_value.embed_documents.return_value = [[0.1] * 384]

    # Mock chain execution
    mock_chain = MagicMock()
    mock_chain.return_value = {"answer": "Mocked answer"}
    chain_mock.return_value = mock_chain

    # ✅ Mock callback context manager
    cb_context = MagicMock()
    cb_context.__enter__.return_value.total_tokens = 42
    cb_context.__enter__.return_value.prompt_tokens = 10
    cb_context.__enter__.return_value.completion_tokens = 32
    cb_context.__enter__.return_value.total_cost = 0.001
    cb_mock.return_value = cb_context

    # Call the function
    response = get_response(
        file_name="sample.pdf",
        session_id="abc123",
        query="What is this?",
    )

    expected_response = {
        "answer": "Mocked answer",
        "total_tokens_used": 42,
        "prompt_tokens_used": 10,
        "completion_tokens_used": 32,
        "total_cost": 0.001,
    }
    assert isinstance(response, dict)
    assert response["answer"] == expected_response["answer"]
    assert response["total_tokens_used"] == expected_response["total_tokens_used"]
