import email
from sqlalchemy import select
from dataclasses import asdict

from fastapi_zero.models import User


def test_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username="testuser",
            email="testuser@example.com",
            password="securepassword",
        )
        session.add(new_user)
        session.commit()

        user = session.scalar(select(User).where(User.username == "testuser"))

        breakpoint()

    assert asdict(user) == {
        "id": 1,
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "securepassword",
        "created_at": time,
    }
