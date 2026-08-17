import pytest

from fastapi.testclient import TestClient

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models

from app.api.dependencies.auth import (
    get_current_user,
    get_optional_user,
)
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.user import User


test_engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)


TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    expire_on_commit=False,
)


def override_get_db():
    with TestingSessionLocal() as db:
        yield db


app.dependency_overrides[
    get_db
] = override_get_db


@pytest.fixture(autouse=True)
def reset_database():
    # Every test starts with an empty database.
    Base.metadata.drop_all(
        bind=test_engine
    )

    Base.metadata.create_all(
        bind=test_engine
    )

    yield


@pytest.fixture
def db_session():
    with TestingSessionLocal() as db:
        yield db


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth_user():
    with TestingSessionLocal() as db:
        user = User(
            email="driver@example.com",
            password_hash="not-used-in-this-test",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        db.expunge(user)

        return user


@pytest.fixture
def authenticated_client(
    auth_user,
):
    app.dependency_overrides[
        get_current_user
    ] = lambda: auth_user

    app.dependency_overrides[
        get_optional_user
    ] = lambda: auth_user

    try:
        with TestClient(app) as test_client:
            yield test_client

    finally:
        app.dependency_overrides.pop(
            get_current_user,
            None,
        )

        app.dependency_overrides.pop(
            get_optional_user,
            None,
        )