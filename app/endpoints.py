import logging

import aiofiles
from fastapi import APIRouter, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

from app.accessors import get_s3_client
from app.chat import get_response
from app.config import get_config_variables
from app.models import ChatMessageSent
from app.utils import add_session_history, get_session, get_temp_file_path

LOG = logging.getLogger(__name__)

CONFIG = get_config_variables()
S3_CLIENT = get_s3_client()


routes = APIRouter()


@routes.post("/chat")
async def create_chat_message(chats: ChatMessageSent) -> JSONResponse:
    """Create a chat message.

    This function handles the chat message creation process and returns a JSON response.

    Args:
        chats (ChatMessageSent): The chat message object containing user input and session ID.

    Returns:
        JSONResponse: A JSON response containing the chat message and session ID.

    Raises:
        HTTPException: If there is an error during the chat message creation process.
            - 400: Bad Request if the session ID is invalid.
            - 500: Internal Server Error for other exceptions.

    """
    try:
        if chats.session_id is None:
            session_id = get_session()

            chat_object = ChatMessageSent(
                session_id=session_id,
                user_input=chats.user_input,
                data_source=chats.data_source,
            )

            payload = chat_object.model_dump()

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
        chat_object = ChatMessageSent(
            session_id=str(chats.session_id),
            user_input=chats.user_input,
            data_source=chats.data_source,
        )

        payload = chat_object.model_dump()  # Fixed the method call to dict()

        response = get_response(
            file_name=str(payload.get("data_source")),
            session_id=str(payload.get("session_id")),
            query=str(payload.get("user_input")),
        )
        add_session_history(
            session_id=str(payload.get("session_id")),
            new_values=[payload.get("user_input"), response["answer"]],
        )
        return JSONResponse(
            content={
                "response": response,
                "session_id": str(payload.get("session_id")),
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
    else:
        LOG.info(f"File uploaded successfully: {data_file.filename}")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"detail": "File uploaded successfully"},
        )
