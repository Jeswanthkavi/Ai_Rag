import logging

from fastapi import FastAPI

from fastapi.middleware.cors import (
    CORSMiddleware
)

from app.api import (
    auth,
    documents,
    chat,
    conversation
)

from app.utils.exceptions import (
    global_exception_handler
)

from app.middleware.logging_middleware import (
    logging_middleware
)


# =========================================================
# APPLICATION
# =========================================================

app = FastAPI(

    title="AI Document Assistant",

    version="1.0.0"
)


# =========================================================
# EXCEPTION HANDLER
# =========================================================

app.add_exception_handler(

    Exception,

    global_exception_handler
)


# =========================================================
# CORS
# =========================================================

origins = [

    "http://localhost:3000",

    "http://127.0.0.1:3000"
]


app.add_middleware(

    CORSMiddleware,

    allow_origins=origins,

    allow_credentials=True,

    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "DELETE"
    ],

    allow_headers=[
        "Authorization",
        "Content-Type"
    ]
)


# =========================================================
# LOGGING MIDDLEWARE
# =========================================================

@app.middleware("http")
async def request_logging_middleware(
    request,
    call_next
):

    return await logging_middleware(
        request,
        call_next
    )


# =========================================================
# ROUTES
# =========================================================

app.include_router(

    auth.router,

    prefix="/auth",

    tags=["Authentication"]
)


app.include_router(

    documents.router,

    prefix="/documents",

    tags=["Documents"]
)


app.include_router(

    chat.router,

    prefix="/chat",

    tags=["Chat"]
)


app.include_router(

    conversation.router,

    prefix="/conversations",

    tags=["Conversations"]
)


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():

    return {

        "application":
            "AI Document Assistant",

        "version":
            "1.0.0",

        "status":
            "running"
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health():

    return {

        "status":
            "healthy"
    }