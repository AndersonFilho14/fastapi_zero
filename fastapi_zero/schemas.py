from typing import List
from pydantic import BaseModel, EmailStr, ConfigDict, Field


class Message(BaseModel):
    message: str


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    username: str
    email: EmailStr
    id: int

    model_config = ConfigDict(from_attributes=True)


class UserList(BaseModel):
    users: List[UserPublic]


class UserDb(UserSchema):
    id: int


class Token(BaseModel):
    access_token: str
    token_type: str


class FilterPage(BaseModel):
    limit: int = Field(ge=1, default=10)
    offset: int = Field(ge=0, default=0)
