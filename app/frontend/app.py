import logging
import tempfile
import time
from http import HTTPStatus
from pathlib import Path

import requests
import streamlit as st

# Base URL of the backend API server
BACKEND_URL = "http://localhost:8000"

# Initialize logger for this module
LOG = logging.getLogger(__name__)


def chat(user_input: str, data: str, session_id: str | None = None) -> tuple[str, str] | None:
    """Send a user input to a chat API and returns the response.

    Args:
        user_input (str): The user's input.
        data (str): The data source.
        session_id (str, optional): Session identifier. Defaults to None.

    Returns:
        tuple[str, str] | None: A tuple containing the response answer and
            the updated session_id, or None if the request failed.

    """
    # API endpoint for chat
    url = BACKEND_URL + "/chat"

    # Log inputs for debugging
    LOG.info(f"User input: {user_input}")
    LOG.info(f"Data source: {data}")
    LOG.info(f"Session ID: {session_id}")

    # Prepare payload for the API request - ALWAYS include session_id
    # even if it's None/null - the API requires this field
    payload = {
        "user_input": user_input,
        "data_source": data,
        "session_id": session_id,  # Always include this field, even if None
    }

    # Set headers for the API request
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    try:
        # Make a POST request to the chat API
        response = requests.post(
            url,
            headers=headers,
            json=payload,  # Use json parameter for automatic serialization
            timeout=30,
        )

        LOG.info(f"Response status: {response.status_code}")
        LOG.info(f"Request payload: {payload}")

        # Check if the request was successful (status code 200)
        if response.status_code == HTTPStatus.OK:
            result = response.json()
            LOG.info(f"Success response: {result}")
            # Return the response answer and updated session_id
            return result["response"]["answer"], result["session_id"]

    except Exception as e:
        message = str(e)
        LOG.exception(f"Request failed: {message}")
        return None
    else:
        LOG.error(f"Error response: {response.status_code} - {response.text}")
        return None


def upload_file(file_path: str) -> str | None:
    """Upload a file to a specified API endpoint.

    Args:
        file_path (str): The path to the file to be uploaded.

    Returns:
        str | None: The file path returned by the API, or None if the upload failed.

    """
    LOG.info(f"path: {file_path}")

    # Convert to Path object if it's a string
    path_obj = Path(file_path) if isinstance(file_path, str) else file_path

    # Extract the filename from the Path object
    filename = path_obj.name

    # API endpoint for file upload
    url = BACKEND_URL + "/uploadFile"
    LOG.info(url)

    # Prepare payload for the file upload request
    payload: dict[str, str] = {}

    # Use context manager with Path.open() to safely open and read the file
    with Path(file_path).open("rb") as file:
        file_content = file.read()

    files = [
        (
            "data_file",
            (filename, file_content, "application/pdf"),
        )
    ]

    # Set headers for the file upload request
    headers = {"accept": "application/json"}

    # Make a POST request to upload the file
    response = requests.request("POST", url, headers=headers, data=payload, files=files, timeout=10)
    LOG.info(response.status_code)

    # Check if the file upload was successful (status code 200)
    if response.status_code == HTTPStatus.OK:
        # LOG.info the API response for debugging
        LOG.info(f"response: {response.json()}")
        # Return the file path returned by the API
        return response.json()["file_path"]

    LOG.error(f"File upload failed with status code: {response.status_code}")
    return None


# Set page configuration for the Streamlit app
st.set_page_config(page_title="Semantic Document Chat", page_icon="🧠", layout="wide")

# Initialize chat history and session variables
if "messages" not in st.session_state:
    st.session_state.messages = []
if "sessionid" not in st.session_state:
    st.session_state.sessionid = None

# Allow user to upload a file (PDF or DOCX)
data_file = st.file_uploader(label="Input file", accept_multiple_files=False, type=["pdf", "docx"])
st.divider()

# Process the uploaded file if available
if data_file is not None:
    # Create temp directory if it doesn't exist
    temp_dir = Path(tempfile.gettempdir()) / "ml-nlp-app"
    temp_dir.mkdir(exist_ok=True, parents=True)

    # Save the file temporarily
    file_path = temp_dir / data_file.name
    with file_path.open("wb") as f:
        f.write(data_file.getbuffer())

    # Upload the file to a specified API endpoint
    s3_upload_url = upload_file(file_path=file_path)

    if s3_upload_url is not None:
        s3_upload_url = s3_upload_url.split("/")[-1]
    else:
        st.error("Failed to upload file. Please try again.")
        st.stop()  # Stop execution if upload failed

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input

    # Accept user input

    # Accept user input
    if prompt := st.chat_input("You can ask any question"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            if st.session_state.sessionid is None:
                # If no existing session ID, start a new session
                result = chat(prompt, data=s3_upload_url, session_id=None)
                if result is None:
                    st.error("Failed to get response from the chat service. Please try again.")
                    st.stop()
                assistant_response, session_id = result
                st.session_state.sessionid = session_id
            else:
                # If existing session ID, continue the session
                result = chat(prompt, session_id=st.session_state.sessionid, data=s3_upload_url)
                if result is None:
                    st.error("Failed to get response from the chat service. Please try again.")
                    st.stop()
                assistant_response, session_id = result

            message_placeholder = st.empty()
            full_response = ""

            # Simulate stream of response with milliseconds delay
            for chunk in assistant_response.split():
                full_response += chunk + " "
                time.sleep(0.05)

                # Add a blinking cursor to simulate typing
                message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})
