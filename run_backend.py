import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.backend:chat_app",
        host="localhost",
        port=8000,
        reload=True,
        log_level="debug",  # Set to debug, info, warning, error, or critical
    )
