from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.endpoints import routes

chat_app = FastAPI(title="My FastAPI Project")
chat_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

chat_app.include_router(routes)
