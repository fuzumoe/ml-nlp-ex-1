import gc
import logging
from typing import Any

from langchain.chains import ConversationalRetrievalChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.callbacks.manager import get_openai_callback
from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI

from app.backend.accessors import get_collection
from app.backend.config import get_config_variables
from app.backend.utils import get_temp_file_path, load_memory_to_pass

LOG = logging.getLogger(__name__)
CONFIG = get_config_variables()

CHAT_HISTORY_COLLECTION = get_collection()


def get_response(
    file_name: str,
    session_id: str,
    query: str,
    model: str = "mistralai/Mistral-7B-Instruct-v0.1",
    temperature: float = 0.0,
) -> Any:
    """Get a response from the model using the provided file and query.

    Args:
        file_name (str): The name of the file to process.
        session_id (str): The session ID for chat history.
        query (str): The user's query.
        model (str): The model to use for generating responses.
        temperature (float): The temperature setting for the model.

    Returns:
        Any: The response from the model.

    """
    LOG.info(f"file name is {file_name}")

    # Ensure local path to file
    file_name = file_name.split("/")[-1]
    local_file = str(get_temp_file_path(file_name).absolute())

    # Load document from local disk
    loader = Docx2txtLoader(file_path=local_file) if file_name.endswith(".docx") else PyPDFLoader(local_file)
    data = loader.load()

    # Split into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0, separators=["\n", " ", ""])
    all_splits = text_splitter.split_documents(data)

    # Use open-source embedding model (no API key required)
    embeddings = HuggingFaceEmbeddings(model_name="intfloat/e5-small-v2")

    # Build FAISS vectorstore
    vectorstore = FAISS.from_documents(all_splits, embeddings)

    # Initialize the LLM
    llm = ChatOpenAI(
        model=model,
        temperature=temperature,
    )

    # Setup the QA chain
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 1}),
    )

    # Generate the answer
    with get_openai_callback() as cb:
        answer = qa_chain(
            {
                "question": query,
                "chat_history": load_memory_to_pass(session_id=session_id),
            }
        )
        LOG.info(f"Total Tokens: {cb.total_tokens}")
        LOG.info(f"Prompt Tokens: {cb.prompt_tokens}")
        LOG.info(f"Completion Tokens: {cb.completion_tokens}")
        LOG.info(f"Total Cost (in $): {cb.total_cost}")

        answer["total_tokens_used"] = cb.total_tokens

    gc.collect()
    return answer
