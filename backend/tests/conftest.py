import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from fastapi.testclient import TestClient

from app.main import app

from app.database import (
    Base,
    get_db
)

from app.config import settings

from app.models.user import User

from app.security import hash_password


# =========================================================
# TEST DATABASE
# =========================================================

TEST_DATABASE_NAME = (
    f"{settings.mysql_database}_test"
)


TEST_DATABASE_URL = (
    f"mysql+pymysql://"
    f"{settings.mysql_user}:"
    f"{settings.mysql_password}@"
    f"{settings.mysql_host}:"
    f"{settings.mysql_port}/"
    f"{TEST_DATABASE_NAME}"
)


test_engine = create_engine(
    TEST_DATABASE_URL,
    pool_pre_ping=True
)


TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False
)


# =========================================================
# CREATE TEST DATABASE TABLES
# =========================================================

@pytest.fixture(
    scope="session",
    autouse=True
)
def setup_test_database():

    Base.metadata.create_all(
        bind=test_engine
    )

    yield

    Base.metadata.drop_all(
        bind=test_engine
    )


# =========================================================
# DATABASE SESSION
# =========================================================

@pytest.fixture
def db():

    session = TestingSessionLocal()

    try:

        yield session

    finally:

        session.rollback()
        session.close()


# =========================================================
# BASIC TEST CLIENT
# =========================================================

@pytest.fixture
def client(db):

    def override_get_db():

        try:

            yield db

        finally:

            pass

    app.dependency_overrides[
        get_db
    ] = override_get_db

    with TestClient(app) as test_client:

        yield test_client

    app.dependency_overrides.clear()


# =========================================================
# TEST USER
# =========================================================

@pytest.fixture
def test_user(db):

    email = "testuser@example.com"

    password = "TestPassword123!"

    password_hash = hash_password(
        password
    )

    # -----------------------------------------
    # Remove existing test user
    # -----------------------------------------

    existing_user = (
        db.query(User)
        .filter(
            User.email == email
        )
        .first()
    )

    if existing_user:

        db.delete(existing_user)

        db.commit()

    # -----------------------------------------
    # Create test user
    # -----------------------------------------

    user = User(
        email=email,
        name="Test User",
        password_hash=password_hash
    )

    db.add(user)

    db.commit()

    db.refresh(user)

    yield {
        "user": user,
        "password": password
    }

    # -----------------------------------------
    # Cleanup after test
    # -----------------------------------------

    db.delete(user)

    db.commit()


# =========================================================
# AUTHENTICATED CLIENT
# =========================================================

@pytest.fixture
def authenticated_client(
    db,
    test_user
):

    def override_get_db():

        try:

            yield db

        finally:

            pass

    app.dependency_overrides[
        get_db
    ] = override_get_db

    with TestClient(app) as test_client:

        login_response = test_client.post(
            "/auth/login",
            json={
                "email":
                    test_user["user"].email,

                "password":
                    test_user["password"]
            }
        )

        assert login_response.status_code == 200

        token = login_response.json()[
            "access_token"
        ]

        test_client.headers.update(
            {
                "Authorization":
                    f"Bearer {token}"
            }
        )

        yield test_client

    app.dependency_overrides.clear()