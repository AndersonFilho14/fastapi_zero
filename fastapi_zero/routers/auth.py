from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_zero.database import get_session
from fastapi_zero.models import User
from fastapi_zero.schemas import Token
from fastapi_zero.security import (
    create_access_token,
    get_current_user,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", status_code=HTTPStatus.OK)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    user = await session.scalar(select(User).where(User.email == form_data.username))

    if not user or not verify_password(plain_password=form_data.password, hashed_password=user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Email ou senha incorretos",
        )

    access_token = create_access_token(data={"sub": user.email})

    return {"access_token": access_token, "token_type": "Bearer"}


@router.post("/refresh", response_model=Token)
async def refresh_access_token(current_user: User = Depends(get_current_user)):
    access_token = create_access_token(data={"sub": current_user.email})
    return {"access_token": access_token, "token_type": "Bearer"}
