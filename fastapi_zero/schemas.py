from typing import List
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from fastapi_zero.settings import ToDoState


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


class ToDoSchema(BaseModel):
    title: str
    description: str
    state: ToDoState = Field(default=ToDoState.todo)
    created_at: datetime
    updated_at: datetime

class ToDoResponse(ToDoSchema):
    id: int


class FilterToDo(FilterPage):
    title: str | None = Field(default=None, min_length=3, max_length=20)
    description: str | None = None
    state: ToDoState | None = None


class ToDoListResponse(BaseModel):
    to_dos: List[ToDoResponse]


class ToDoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    state: ToDoState | None = None
