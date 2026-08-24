from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings


DATABASE_URL = (
    f"mysql+pymysql://"
    f"{settings.mysql_user}:"
    f"{settings.mysql_password}@"
    f"{settings.mysql_host}:"
    f"{settings.mysql_port}/"
    f"{settings.mysql_database}"
)


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()