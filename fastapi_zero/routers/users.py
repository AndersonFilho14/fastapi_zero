from http import HTTPStatus
from typing import Annotated

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import Depends, HTTPException, APIRouter, Query

from fastapi_zero.models import User
from fastapi_zero.database import get_session
from fastapi_zero.security import (
    get_current_user,
    get_password_hash,
)
from fastapi_zero.schemas import (
    Message,
    UserList,
    UserPublic,
    UserSchema,
    FilterPage,
)


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: Session = Depends(get_session)):
    db_user = session.scalar(select(User).where((User.username == user.username) | (User.email == user.email)))

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(status_code=HTTPStatus.CONFLICT, detail="User já existe")

        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail="Email já existe já existe")

    db_user = User(
        **user.model_dump(exclude={"password"}),
        password=get_password_hash(user.password),
    )
    session.add(instance=db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@router.get("/", status_code=HTTPStatus.OK, response_model=UserList)
def read_users(
    filter_users: Annotated[FilterPage, Query()],
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):

    users = session.scalars(select(User).limit(limit=filter_users.limit).offset(offset=filter_users.offset))
    return {"users": users}


@router.get("/{user_id}", status_code=HTTPStatus.OK, response_model=UserPublic)
def read_user(user_id, session: Session = Depends(get_session)):
    user_db = session.scalar(select(User).where(User.id == user_id))

    if not user_db:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Encontrei não patrão")

    return user_db


@router.put("/{user_id}", status_code=HTTPStatus.OK, response_model=UserPublic)
def update_user(
    user_id: int,
    user: UserSchema,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):

    if not current_user.id == user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="Não tem permissão pra isso cumpade",
        )

    try:
        current_user.username = user.username
        current_user.password = get_password_hash(user.password)
        current_user.email = user.email
        session.commit()
        session.refresh(current_user)

        return current_user

    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Username or Email already exists",
        )


@router.delete("/{user_id}", status_code=HTTPStatus.OK, response_model=Message)
def delete_user(
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):

    session.delete(instance=current_user)
    session.commit()

    return {"message": "User deletado patrão, pode ir dormi!!!"}
