import gc
import logging
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

from app.accessors import get_collection, get_s3_session
from app.config import get_config_variables
from app.utils import load_memory_to_pass

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
