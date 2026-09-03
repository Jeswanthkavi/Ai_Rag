from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

import uuid

from app.database import get_db

from app.models.user import User
from app.models.document import Document
from app.models.conversation import Conversation
from app.models.message import Message

from dependencies import get_current_user

from app.schemas.conversation import (
    ConversationCreate,
    ConversationResponse
)


router = APIRouter()


@router.post("/",response_model=ConversationResponse)
def create_conversation(
    request: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    if request.document_id:

        document = (
            db.query(Document)
            .filter(
                Document.document_id
                == request.document_id,
                Document.user_id
                == current_user.id
            )
            .first()
        )

        if not document:

            raise HTTPException(
                status_code=404,
                detail="Document not found"
            )

    conversation = Conversation(
        conversation_id=str(uuid.uuid4()),
        user_id=current_user.id,
        document_id=request.document_id,
        title=request.title
    )

    db.add(conversation)

    db.commit()

    db.refresh(conversation)

    return conversation
@router.get("/")
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    conversations = (
        db.query(Conversation)
        .filter(
            Conversation.user_id
            == current_user.id
        )
        .order_by(
            Conversation.created_at.desc()
        )
        .all()
    )

    return [
        {
            "conversation_id": c.conversation_id,
            "document_id": c.document_id,
            "title": c.title,
            "created_at": c.created_at
        }
        for c in conversations
    ]
@router.get("/{conversation_id}")
def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.conversation_id
            == conversation_id,
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

    messages = (
        db.query(Message)
        .filter(
            Message.conversation_id
            == conversation.id
        )
        .order_by(
            Message.created_at.asc()
        )
        .all()
    )

    return {
        "conversation_id":
            conversation.conversation_id,

        "document_id":
            conversation.document_id,

        "title":
            conversation.title,

        "messages": [
            {
                "role": message.role,
                "content": message.content,
                "created_at":
                    message.created_at
            }
            for message in messages
        ]
    }