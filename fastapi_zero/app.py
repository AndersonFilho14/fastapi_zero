from http import HTTPStatus
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from fastapi_zero.schemas import (
    Message,
    UserSchema,
    UserPublic,
    UserDb,
    UserList,
)


app = FastAPI(title="Minha Pomba")
mock_database = []


@app.get("/", status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return Message(message="Hello World")


@app.get("/health", status_code=HTTPStatus.OK, response_class=HTMLResponse)
def health():
    return """<h1>Tudo Ok patrão, pode ir dormir</h1>"""


@app.post("/users/", status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema):
    user_with_id = UserDb(**user.model_dump(), id=len(mock_database) + 1)
    mock_database.append(user_with_id)
    return user_with_id


@app.get("/users/", status_code=HTTPStatus.OK, response_model=UserList)
def read_users():
    return {"users": mock_database}


@app.get(
    "/user/{user_id}", status_code=HTTPStatus.OK, response_model=UserPublic
)
def read_user(user_id):
    user_id = int(user_id)
    if user_id < 1 or user_id > len(mock_database):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Encontrei não patrão"
        )

    return mock_database[user_id - 1]


@app.put(
    "/user/{user_id}", status_code=HTTPStatus.OK, response_model=UserPublic
)
def update_user(user_id: int, user: UserSchema):
    if user_id < 1 or user_id > len(mock_database):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Encontrei não patrão"
        )

    user = UserDb(**user.model_dump(), id=user_id)
    mock_database[user_id - 1] = user
    return user


@app.delete("/user/{user_id}", status_code=HTTPStatus.OK)
def delete_user(user_id: int):
    if user_id < 1 or user_id > len(mock_database):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Encontrei não patrão"
        )

    del mock_database[user_id - 1]
