from dataclasses import asdict

from pytest import mark
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_zero.models import User


@mark.asyncio
async def test_create_user(session: AsyncSession, mock_db_time):
    with mock_db_time(model=User) as (creted_time, updated_time):
        new_user = User(
            username="testuser",
            email="testuser@example.com",
            password="securepassword",
        )

        session.add(new_user)
        await session.commit()

        user = await session.scalar(select(User).where(User.username == "testuser"))

    assert asdict(user) == {
        "id": 1,
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "securepassword",
        "created_at": creted_time,
        "updated_at": updated_time,
        "to_dos": [],
    }
