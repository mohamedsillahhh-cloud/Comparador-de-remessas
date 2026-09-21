import contextlib
import os

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["ADMIN_TOKEN"] = "test-admin-token"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_session
from app.main import app
from app.seed import seed_providers

TEST_ENGINE = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TEST_SESSION = sessionmaker(bind=TEST_ENGINE, autoflush=False, expire_on_commit=False)


@contextlib.asynccontextmanager
async def noop_lifespan(_):
    yield


@pytest.fixture()
def client():
    Base.metadata.create_all(TEST_ENGINE)
    with TEST_SESSION() as session:
        seed_providers(session)

    def override_get_session():
        session = TEST_SESSION()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = override_get_session
    app.router.lifespan_context = noop_lifespan
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.pop(get_session, None)
    Base.metadata.drop_all(TEST_ENGINE)