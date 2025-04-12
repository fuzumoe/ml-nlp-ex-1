import gc
import logging
import tempfile
import uuid
from pathlib import Path
from typing import Any

import awswrangler as wr
from langchain.callbacks import get_openai_callback
from langchain.chains import ConversationalRetrievalChain
from langchain.document_loaders import (
    Docx2txtLoader,
    PyPDFLoader,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pymongo import errors as pymongo_errors

from app.accessors import get_collection, get_s3_session
from app.config import get_config_variables

LOG = logging.getLogger(__name__)

CONFIG = get_config_variables()

CHAT_HISTORY_COLLECTION = get_collection()


def get_response(
    file_name: str,
    session_id: str,
    query: str,
    model: str = "gpt-4",
    temperature: float = 0.0,
) -> Any:
    """Get the response from the model.

    This function retrieves the response from the model based on the
        provided file name, session ID, and query.

    Args:
        file_name (str): The name of the file to process.
        session_id (str): The session ID for the chat.
        query (str): The user's query.
        model (str): The model to use for generating the response.
        temperature (float): The temperature for the model.

    Returns:
        any: The response from the model.

    """
    LOG.info(f"file name is {file_name}")

    file_name = file_name.split("/")[-1]

    embeddings = OpenAIEmbeddings()

    wr.s3.download(
        path=f"s3://{CONFIG.S3_BUCKET}/{CONFIG.S3_PATH}/{file_name}",
        local_file=file_name,
        boto3_session=get_s3_session(),
    )

    loader: PyPDFLoader | Docx2txtLoader | None = None

    if file_name.endswith(".docx"):
        loader = Docx2txtLoader(file_path=file_name.split("/")[-1])
    else:
        loader = PyPDFLoader(file_name)

    data = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0, separators=["\n", " ", ""])

    all_splits = text_splitter.split_documents(data)
    vectorstore = FAISS.from_documents(all_splits, embeddings)

    llm = ChatOpenAI(
        model=model,
        temperature=temperature,
    )

    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 1}),
    )

    with get_openai_callback() as cb:
        answer = qa_chain(
            {
                "question": query,
                "chain_history": load_memory_to_pass(session_id=session_id),
            }
        )
        LOG.info(f"Total Tokens: {cb.total_tokens}")
        LOG.info(f"Prompt Tokens: {cb.prompt_tokens}")
        LOG.info(f"Completion Tokens: {cb.completion_tokens}")
        LOG.info(f"Total Cost (in $): {cb.total_cost}")

        answer["total_tokens_used"] = cb.total_tokens

    gc.collect()

    return answer


def load_memory_to_pass(session_id: str) -> list:
    """Load the memory history for a given session ID.

    This function retrieves the conversation history from the MongoDB
        collection and formats it for use in the chat.

    Args:
        session_id (str): The session ID to load memory for.

    Returns:
        list: The loaded memory history.

    """
    data = CHAT_HISTORY_COLLECTION.find_one({"session_id": session_id})
    history = []

    if data:
        data = data["conversion"]

        for x in range(0, len(data), 2):
            history.extend([(data[x], data[x + 1])])

    LOG.info(history)

    return history


def get_session() -> str:
    """Generate a new session ID.

    This function generates a new session ID for the chat.

    Returns:
        str: The generated session ID.

    """
    return str(uuid.uuid4())


def add_session_history(session_id: str, new_values: list) -> bool:
    """Add a new session history entry.

    This function adds a new entry to the chat history in the MongoDB
        collection.

    Args:
        session_id (str): The session ID for the chat.
        new_values (list): The new values to be added to the conversation history.

    Returns:
        bool: True if the entry was added successfully, False otherwise.

    """
    try:
        doc = CHAT_HISTORY_COLLECTION.find_one({"session_id": session_id})

        if doc:
            conversion = doc["conversion"]
            conversion.extend(new_values)
            CHAT_HISTORY_COLLECTION.update_one(
                {"session_id": session_id},
                {"$set": {"conversion": conversion}},
            )
        else:
            CHAT_HISTORY_COLLECTION.insert_one(
                {
                    "session_id": session_id,
                    "conversion": new_values,
                }
            )
    except pymongo_errors.PyMongoError as e:
        message = str(e)
        LOG.exception(f"Error adding session history: {message}")
        return False
    else:
        return True


def get_temp_file_path(filename: str | None) -> Path:
    """Validate filename and prepare a temporary file path.

    Args:
        filename: The original filename from the upload

    Returns:
        Path: Path object pointing to the temporary file location

    Raises:
        FileNotFoundError: If the filename is None

    """
    if filename is None:
        msg = "Uploaded file must have a filename."
        raise FileNotFoundError(msg)

    # Create a safe filename without potentially problematic characters
    safe_filename = Path(filename).name

    # Create path in secure temporary directory
    tmp_path = Path(tempfile.gettempdir()) / safe_filename

    LOG.info(f"Using temporary file path: {tmp_path}")

    return tmp_path
