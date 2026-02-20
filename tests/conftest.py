from contextlib import contextmanager
from datetime import datetime

import factory
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from fastapi_zero.app import app
from fastapi_zero.database import get_session
from fastapi_zero.models import User, table_registry
from fastapi_zero.security import get_password_hash


@pytest_asyncio.fixture
async def client(session):
    async def get_session_override():
        return session

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@contextmanager
def _mock_db_time(*, model=User, time=datetime.now()):
    def fake_time_hook(mapper, connection, target):
        if hasattr(target, "created_at"):
            target.created_at = time
        if hasattr(target, "updated_at"):
            target.updated_at = time

    event.listen(model, "before_insert", fake_time_hook)

    yield time, time

    event.remove(model, "before_insert", fake_time_hook)


@pytest.fixture
def mock_db_time():
    yield _mock_db_time


@pytest_asyncio.fixture
async def user(session: AsyncSession):
    clean_password = "testtest"

    user = UserFactory(
        password=get_password_hash(clean_password),
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = clean_password

    return user


@pytest_asyncio.fixture
async def other_user(session: AsyncSession):
    clean_password = "testtest"

    user = UserFactory(
        password=get_password_hash(clean_password),
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = clean_password

    return user


@pytest_asyncio.fixture
async def token(client, user):
    response = await client.post(
        "/auth/token",
        data={"username": user.email, "password": user.clean_password},
    )

    return response.json()["access_token"]


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"test_user{n}")
    email = factory.lazy_attribute(lambda obj: f"{obj.username}@test.com")
    password = factory.lazy_attribute(lambda obj: f"{obj.username}_senha")
