from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from pydantic import BaseModel

from sqlalchemy.orm import Session

from app.database import get_db

from dependencies import get_current_user

from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message

from app.services.embedding_service import (
    EmbeddingService
)

from app.services.vector_service import (
    VectorService
)

from app.services.llm_service import (
    LLMService
)
from app.services.conversation_service import (
    get_recent_messages
)

from app.config import settings


router = APIRouter()


embedding_service = EmbeddingService()

vector_service = VectorService()

llm_service = LLMService(
    settings.gemini_api_key,
    settings.gemini_model
)


class ChatRequest(BaseModel):

    question: str

    conversation_id: str


@router.post("/")
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    # --------------------------------
    # 1. Find conversation
    # --------------------------------

    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.conversation_id
            == request.conversation_id,
            Conversation.user_id
            == current_user.id
        )
        .first()
    )

    if not conversation:

        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    # --------------------------------
    # 2. Save user message
    # --------------------------------

    history = get_recent_messages(
    db,
    conversation.id,
    limit=10
)

    
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.question
    )

    db.add(user_message)

    db.commit()

    # --------------------------------
    # 3. Create question embedding
    # --------------------------------

    query_vector = (
        embedding_service
        .embed_query(
            request.question
        )
    )

    # --------------------------------
    # 4. Search Qdrant
    # --------------------------------

    results = vector_service.search(
        query_vector,
        limit=3,
        document_id=conversation.document_id
    )

    if not results:

        answer = (
            "I could not find relevant "
            "information in the document."
        )

    else:

        # ----------------------------
        # 5. Generate answer
        # ----------------------------
        history = get_recent_messages(db,conversation.id,limit=10)
        answer = llm_service.generate_answer(
            request.question,
            results,
            history
        )

    # --------------------------------
    # 6. Save AI message
    # --------------------------------

    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=answer
    )

    db.add(assistant_message)

    db.commit()

    # --------------------------------
    # 7. Sources
    # --------------------------------

    sources = []

    for result in results:

        payload = result.payload

        sources.append({
            "filename": payload["filename"],
            "page": payload["page"],
            "score": round(
                result.score,
                4
            )
        })

    return {
        "answer": answer,
        "sources": sources
    }