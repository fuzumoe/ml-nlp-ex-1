import uvicorn
from app import chat_app

if __name__ == "__main__":
    uvicorn.run(chat_app, host="localhost", port=8000, log_level="info")
