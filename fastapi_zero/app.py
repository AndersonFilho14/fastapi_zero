from http import HTTPStatus

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from fastapi_zero.schemas import Message
from fastapi_zero.routers import auth, users


app = FastAPI(title="Minha Pomba")
app.include_router(auth.router)
app.include_router(users.router)


@app.post("/star_db", status_code=HTTPStatus.OK)
def start_db():

    from sqlalchemy import create_engine

    from fastapi_zero.settings import Settings
    from fastapi_zero.models import table_registry

    engine = create_engine(Settings().DATABASE_URL)
    table_registry.metadata.create_all(bind=engine)

    return """Criado db"""


@app.get("/", status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return Message(message="Hello World")


@app.get("/health", status_code=HTTPStatus.OK, response_class=HTMLResponse)
def health():
    return """<h1>Tudo Ok patrão, pode ir dormir</h1>"""
