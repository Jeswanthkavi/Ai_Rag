from app.database import Base, engine

from app.models import (
    User,
    Document,
    Conversation,
    Message
)


print("Creating database tables...")

Base.metadata.create_all(
    bind=engine
)

print("Database tables created successfully.")