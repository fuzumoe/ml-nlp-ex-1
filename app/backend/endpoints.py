import logging

import aiofiles
from fastapi import APIRouter, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

from app.backend.accessors import get_s3_client
from app.backend.chat import get_response
from app.backend.config import get_config_variables
from app.backend.models import ChatMessageSent
from app.backend.utils import add_session_history, get_session, get_temp_file_path

LOG = logging.getLogger(__name__)

CONFIG = get_config_variables()
S3_CLIENT = get_s3_client()


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
            payload = payload.model_dump()

            response = get_response(
                file_name=payload.get("data_source"),
                session_id=payload.get("session_id"),
                query=payload.get("user_input"),
            )

            add_session_history(
                session_id=session_id,
                new_values=[payload.get("user_input"), response["answer"]],
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
        payload_dict: dict[str, str] = payload.model_dump()

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
    """Upload a file to S3.

    This function handles the file upload process and saves the file to S3.

    Args:
        data_file (UploadFile): The file to be uploaded.

    Returns:
        JSONResponse: A JSON response indicating the result of the upload.

    Raises:
        HTTPException: If there is an error during the file upload process.
            - 400: Bad Request if the file already exists.
            - 500: Internal Server Error for other exceptions.

    """
    LOG.info(f"File name: {data_file.filename}")

    try:
        temp_file = get_temp_file_path(data_file.filename)

        async with aiofiles.open(temp_file, "wb") as out_file:
            content = await data_file.read()
            await out_file.write(content)

            object_key = f"{CONFIG.S3_PATH}/{temp_file.name}"
            S3_CLIENT.upload_file(
                str(temp_file.absolute()),
                CONFIG.S3_BUCKET,  # Bucket name
                object_key,
            )

        LOG.info(f"File uploaded successfully: {data_file.filename}")
        response = {"filename": temp_file.name, "file_path": object_key}
        return JSONResponse(content=response)

    except FileNotFoundError as e:
        message = str(e)
        LOG.exception(f"Error saving file: {message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File already exists: {message}",
        ) from e
    except Exception as e:
        message = str(e)
        LOG.exception(f"Error uploading file: {message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {message}",
        ) from e
