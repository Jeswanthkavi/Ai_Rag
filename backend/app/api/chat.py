from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from pydantic import BaseModel

from sqlalchemy.orm import Session

from app.database import get_db

from dependencies import (
    get_current_user
)

from app.models.user import User

from app.models.document import (
    Document
)

from app.models.conversation import (
    Conversation
)

from app.models.message import (
    Message
)

from app.services.embedding_service import (
    EmbeddingService
)

from app.services.vector_service import (
    VectorService
)

from app.services.retrieval_service import (
    RetrievalService
)

from app.services.reranker_service import (
    RerankerService
)

from app.services.context_service import (
    ContextService
)

from app.services.llm_service import (
    LLMService
)

from app.services.conversation_service import (
    get_recent_messages
)
from app.services.query_service import (
    QueryService
)
from app.config import settings


router = APIRouter()


# =========================================================
# SERVICES
# =========================================================

embedding_service = (
    EmbeddingService()
)

vector_service = (
    VectorService()
)

reranker_service = (
    RerankerService()
)

query_service = QueryService(

    settings.gemini_api_key,

    settings.gemini_model,
)

retrieval_service = RetrievalService(

    vector_service=
        vector_service,

    embedding_service=
        embedding_service,

    reranker_service=
        reranker_service,

    query_service=
        query_service,
)

context_service = (
    ContextService()
)
context_service = (
    ContextService()
)

llm_service = LLMService(

    settings.gemini_api_key,

    settings.gemini_model,
)


# =========================================================
# REQUEST MODEL
# =========================================================

class ChatRequest(BaseModel):

    question: str

    conversation_id: str


# =========================================================
# CHAT
# =========================================================

@router.post("/")
def chat(

    request: ChatRequest,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    ),
):

    # -----------------------------------------------------
    # 1. Validate question
    # -----------------------------------------------------

    question = (
        request.question
        .strip()
    )

    if not question:

        raise HTTPException(

            status_code=400,

            detail=
                "Question cannot be empty",
        )

    # -----------------------------------------------------
    # 2. Find conversation
    # -----------------------------------------------------

    conversation = (

        db.query(
            Conversation
        )

        .filter(

            Conversation.conversation_id
            ==
            request.conversation_id,

            Conversation.user_id
            ==
            current_user.id,
        )

        .first()
    )

    if not conversation:

        raise HTTPException(

            status_code=404,

            detail=
                "Conversation not found",
        )

    # -----------------------------------------------------
    # 3. Check document
    # -----------------------------------------------------

    if conversation.document_id:

        document = (

            db.query(
                Document
            )

            .filter(

                Document.document_id
                ==
                conversation.document_id,

                Document.user_id
                ==
                current_user.id,
            )

            .first()
        )

        if not document:

            raise HTTPException(

                status_code=404,

                detail=
                    "Document not found",
            )

        if document.status == "processing":

            raise HTTPException(

                status_code=409,

                detail=(
                    "Document is still "
                    "processing. Try again "
                    "later."
                ),
            )

        if document.status == "failed":

            raise HTTPException(

                status_code=409,

                detail=(
                    "Document processing "
                    "failed."
                ),
            )

        if document.status != "ready":

            raise HTTPException(

                status_code=409,

                detail=(
                    "Document is not ready "
                    "for querying."
                ),
            )

    # -----------------------------------------------------
    # 4. Get conversation history
    # -----------------------------------------------------

    history = get_recent_messages(

        db,

        conversation.id,

        limit=10,
    )

    # -----------------------------------------------------
    # 5. Save user message
    # -----------------------------------------------------

    user_message = Message(

        conversation_id=
            conversation.id,

        role="user",

        content=question,
    )

    db.add(
        user_message
    )

    db.commit()

    # -----------------------------------------------------
    # 6. Retrieve relevant chunks
    # -----------------------------------------------------

    chunks = retrieval_service.retrieve(

        question=question,

        document_id=
            conversation.document_id,
    )

    # -----------------------------------------------------
    # 7. No relevant information
    # -----------------------------------------------------

    if not chunks:

        answer = (
            "I could not find relevant "
            "information in the provided "
            "document."
        )

        sources = []

    else:

        # -------------------------------------------------
        # 8. Build context
        # -------------------------------------------------

        context = (
            context_service
            .build_context(
                chunks
            )
        )

        # -------------------------------------------------
        # 9. Generate answer
        # -------------------------------------------------

        answer = (
            llm_service
            .generate_answer(

                question=question,

                context=context,

                history=history,
            )
        )

        # -------------------------------------------------
        # 10. Build sources
        # -------------------------------------------------

        sources = (
            context_service
            .build_sources(
                chunks
            )
        )

    # -----------------------------------------------------
    # 11. Save assistant message
    # -----------------------------------------------------

    assistant_message = Message(

        conversation_id=
            conversation.id,

        role="assistant",

        content=answer,
    )

    db.add(
        assistant_message
    )

    db.commit()

    # -----------------------------------------------------
    # 12. Response
    # -----------------------------------------------------

    return {

        "answer": answer,

        "sources": sources,

        "retrieved_chunks":
            len(chunks),
    }