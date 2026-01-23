from http import HTTPStatus
from zoneinfo import ZoneInfo
from pwdlib import PasswordHash
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from jwt import encode, decode, DecodeError
from fastapi.security import OAuth2PasswordBearer


from fastapi_zero.models import User
from fastapi_zero.database import get_session


SECRET_KEY = "123"
ALGORITHM = "HS256"
ACESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(tz=ZoneInfo("UTC")) + timedelta(
        minutes=ACESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    encode_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encode_jwt


def get_current_user(
    session: Session = Depends(get_session),
    token: str = Depends(oauth2_scheme),
) -> User:
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail="Não pode ser validado esse token chefia",
        headers={"www-authenticate": "Bearer"},
    )

    try:
        payload = decode(token, SECRET_KEY, algorithms=ALGORITHM)
        email = payload.get("sub")

        if not email:
            raise credentials_exception

    except DecodeError:
        raise credentials_exception

    user = session.scalar(select(User).where(User.email == email))

    if not user:
        raise credentials_exception

    return user
