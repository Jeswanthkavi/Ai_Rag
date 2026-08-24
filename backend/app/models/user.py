from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import datetime

from app.database import Base


class User(Base):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )

    name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    documents = relationship(
        "Document",
        back_populates="user"
    )

    conversations = relationship(
        "Conversation",
        back_populates="user"
    )