import logging

import aiofiles
from fastapi import APIRouter, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

from app.backend.chat import get_response
from app.backend.config import get_config_variables
from app.backend.models import ChatMessageSent
from app.backend.utils import add_session_history, get_session, get_temp_file_path

LOG = logging.getLogger(__name__)

CONFIG = get_config_variables()


routes = APIRouter()


@routes.post("/chat")
async def create_chat_message(
    chats: ChatMessageSent,
) -> JSONResponse:
    """Create a chat message and obtain a response based on user input and session.

    This route allows users to send chat messages, and it returns responses based on
    the provided input and the associated session. If a session ID is not provided
    in the request, a new session is created. The conversation history is updated, and
    the response, along with the session ID, is returned.

    Args:
        chats (ChatMessageSent): A Pydantic model representing the chat message, including
        session ID, user input, and data source.

    Returns:
        JSONResponse: A JSON response containing the response message and the session ID.

    Raises:
        HTTPException: If an unexpected error occurs during the chat message processing,
        it returns a 204 NO CONTENT HTTP status with an "error" detail.

    """
    try:
        if chats.session_id is None:
            session_id = get_session()

            payload = ChatMessageSent(
                session_id=session_id,
                user_input=chats.user_input,
                data_source=chats.data_source,
            )
            payload_dict: dict[str, str] = payload.model_dump()

            response = get_response(
                file_name=payload_dict.get("data_source") or "",
                session_id=payload_dict.get("session_id") or "",
                query=payload_dict.get("user_input") or "",
            )

            add_session_history(
                session_id=session_id,
                new_values=[
                    payload_dict.get("user_input", "") or "",
                    response["answer"],
                ],
            )

            return JSONResponse(
                content={
                    "response": response,
                    "session_id": str(session_id),
                }
            )

        payload = ChatMessageSent(
            session_id=str(chats.session_id),
            user_input=chats.user_input,
            data_source=chats.data_source,
        )
        payload_dict = payload.model_dump()

        response = get_response(
            file_name=payload_dict.get("data_source") or "",
            session_id=payload_dict.get("session_id") or "",
            query=payload_dict.get("user_input") or "",
        )

        add_session_history(
            session_id=payload_dict.get("session_id") or "",
            new_values=[
                payload_dict.get("user_input") or "",
                response.get("answer", ""),
            ],
        )

        return JSONResponse(
            content={
                "response": response,
                "session_id": str(chats.session_id),
            }
        )
    except Exception as e:
        message = str(e)
        LOG.exception(f"Error in create_chat_message: {message}")
        raise HTTPException(  # noqa: B904
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@routes.post("/uploadFile")
async def upload_file(data_file: UploadFile) -> JSONResponse:
    """Upload a file locally.

    This function saves the uploaded file to a local temp directory and returns its path.

    Args:
        data_file (UploadFile): The file to be uploaded.

    Returns:
        JSONResponse: A JSON response with file metadata.

    Raises:
        HTTPException: If file saving fails.

    """
    LOG.info(f"Received file: {data_file.filename}")

    try:
        temp_file = get_temp_file_path(data_file.filename)

        # Save uploaded file to the temporary file path
        async with aiofiles.open(temp_file, "wb") as out_file:
            content: bytes = await data_file.read()
            await out_file.write(content)

        LOG.info(f"File saved locally: {temp_file.name}")
        response: dict[str, str] = {
            "filename": temp_file.name,
            "file_path": str(temp_file.absolute()),
        }
        return JSONResponse(content=response)

    except Exception as e:
        message: str = str(e)
        LOG.exception(f"Error saving file locally: {message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {message}",
        ) from e
