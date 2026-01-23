from http import HTTPStatus

from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from fastapi_zero.models import User
from fastapi_zero.database import get_session
from fastapi_zero.security import (
    verify_password,
    create_access_token,
)


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", status_code=HTTPStatus.OK)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = session.scalar(select(User).where(User.email == form_data.username))

    if not user or not verify_password(plain_password=form_data.password, hashed_password=user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Email ou senha incorretos",
        )

    acess_token = create_access_token(data={"sub": user.email})

    return {"acess_token": acess_token, "token_type": "Bearer"}
