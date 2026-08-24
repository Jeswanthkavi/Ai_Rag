from sqlalchemy.orm import Session

from app.models.user import User


def create_user(
    db: Session,
    email: str,
    name: str | None = None
):

    user = User(
        email=email,
        name=name
    )

    db.add(user)

    db.commit()

    db.refresh(user)

    return user