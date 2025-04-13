from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.backend.endpoints import routes

chat_app = FastAPI(
    title="🧠 Semantic Document Chat API",
    description=(
        "An intelligent API for uploading documents and engaging in "
        "context-aware conversations with your content. "
        "Powered by LLMs, vector embeddings, and retrieval-augmented generation (RAG)."
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
