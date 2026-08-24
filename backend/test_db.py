from app.database import SessionLocal
from app.services.user_service import create_user


db = SessionLocal()

try:

    user = create_user(
        db,
        email="test@example.com",
        name="Test User"
    )

    print("User created:")
    print("ID:", user.id)
    print("Email:", user.email)
    print("Name:", user.name)

finally:

    db.close()