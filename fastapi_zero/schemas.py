from typing import List
from pydantic import BaseModel, EmailStr, ConfigDict


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
