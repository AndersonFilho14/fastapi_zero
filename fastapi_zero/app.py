from http import HTTPStatus

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from fastapi_zero.schemas import Message

app = FastAPI(title="Minha Pomba")


@app.get("/", status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return Message(message="Hello World")


@app.get("/health", status_code=HTTPStatus.OK, response_class=HTMLResponse)
def health():
    return """<h1>Tudo Ok patrão, pode ir dormir</h1>"""
