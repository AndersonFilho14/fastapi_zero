from typing import List
from pydantic import BaseModel, EmailStr


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


class UserList(BaseModel):
    users: List[UserPublic]


class UserDb(UserSchema):
    id: int
