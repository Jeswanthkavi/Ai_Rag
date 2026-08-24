from fastapi import FastAPI

from app.api.documents import router as document_router
from app.api.chat import router as chat_router
from app.api.auth import router as auth_router
from app.api.conversations import (
    router as conversation_router
)

app = FastAPI(
    title="AI Document Assistant",
    version="1.0.0"
)

app.include_router(
    conversation_router,
    prefix="/conversations",
    tags=["Conversations"]
)
app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"]
)

app.include_router(
    document_router,
    prefix="/documents",
    tags=["Documents"]
)

app.include_router(
    chat_router,
    prefix="/chat",
    tags=["Chat"]
)


@app.get("/health")
def health():

    return {
        "status": "ok"
    }