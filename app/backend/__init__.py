from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.backend.endpoints import routes

chat_app = FastAPI(
    title="🚀 Awesome Chat API",
    description=(
        "An interactive API that allows users to upload documents and engage "
        "in intelligent, context-aware conversations with their content. "
        "Powered by OpenAI and document retrieval techniques."
    ),
    version="1.0.0",
)

chat_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

chat_app.include_router(routes)
