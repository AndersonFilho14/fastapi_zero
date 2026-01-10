from http import HTTPStatus
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, Depends, HTTPException

from fastapi_zero.models import User
from fastapi_zero.database import get_session
from fastapi_zero.schemas import (
    Message,
    UserList,
    UserPublic,
    UserSchema,
)


app = FastAPI(title="Minha Pomba")


@app.post("/star_db", status_code=HTTPStatus.OK)
def start_db():

    from sqlalchemy import create_engine
    from fastapi_zero.models import table_registry

    from fastapi_zero.settings import Settings

    engine = create_engine(Settings().DATABASE_URL)
    table_registry.metadata.create_all(bind=engine)

    return """Criado db"""


@app.get("/", status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return Message(message="Hello World")


@app.get("/health", status_code=HTTPStatus.OK, response_class=HTMLResponse)
def health():
    return """<h1>Tudo Ok patrão, pode ir dormir</h1>"""


@app.post("/users/", status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: Session = Depends(get_session)):

    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT, detail="User já existe"
            )

        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail="Email já existe já existe"
        )

    db_user = User(**user.model_dump())
    session.add(instance=db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@app.get("/users/", status_code=HTTPStatus.OK, response_model=UserList)
def read_users(
    limit: int = 10,
    offset: int = 0,
    session: Session = Depends(get_session),
):

    users = session.scalars(
        select(User).limit(limit=limit).offset(offset=offset)
    )
    return {"users": users}


@app.get(
    "/user/{user_id}", status_code=HTTPStatus.OK, response_model=UserPublic
)
def read_user(user_id, session: Session = Depends(get_session)):
    user_db = session.scalar(select(User).where(User.id == user_id))

    if not user_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Encontrei não patrão"
        )

    return user_db


@app.put(
    "/user/{user_id}", status_code=HTTPStatus.OK, response_model=UserPublic
)
def update_user(
    user_id: int, user: UserSchema, session: Session = Depends(get_session)
):
    user_db = session.scalar(select(User).where(User.id == user_id))

    if not user_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Encontrei não patrão"
        )

    try:
        user_db.username = user.username
        user_db.password = user.password
        user_db.email = user.email
        session.commit()
        session.refresh(user_db)

        return user_db

    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Username or Email already exists",
        )


@app.delete(
    "/user/{user_id}", status_code=HTTPStatus.OK, response_model=Message
)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    user_db = session.scalar(select(User).where(User.id == user_id))

    if not user_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Encontrei não patrão"
        )

    session.delete(instance=user_db)
    session.commit()

    return {"message": "User deletado patrão, pode ir dormi!!!"}
