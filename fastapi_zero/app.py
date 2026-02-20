from http import HTTPStatus

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from fastapi_zero.routers import auth, to_do, users
from fastapi_zero.schemas import Message

app = FastAPI(title="Minha Pomba")
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(to_do.router)


@app.post("/star_db", status_code=HTTPStatus.OK)
async def start_db():
    from sqlalchemy.ext.asyncio import create_async_engine

    from fastapi_zero.models import table_registry
    from fastapi_zero.settings import Settings

    engine = create_async_engine(Settings().DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    return """Criado db"""


@app.get("/", status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return Message(message="Hello World")


@app.get("/health", status_code=HTTPStatus.OK, response_class=HTMLResponse)
def health():
    return """<h1>Tudo Ok patrão, pode ir dormir</h1>"""
