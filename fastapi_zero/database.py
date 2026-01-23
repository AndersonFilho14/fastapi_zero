from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from fastapi_zero.settings import settings


engine = create_engine(settings.DATABASE_URL)


def get_session():
    with Session(engine) as session:
        try:
            yield session
        finally:
            session.close()
