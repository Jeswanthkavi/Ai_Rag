from pydantic import BaseModel


class ConversationCreate(BaseModel):

    document_id: str | None = None

    title: str | None = None


class ConversationResponse(BaseModel):

    conversation_id: str
    document_id: str | None
    title: str | None