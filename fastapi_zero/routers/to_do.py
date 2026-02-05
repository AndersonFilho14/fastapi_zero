from http import HTTPStatus

from fastapi import APIRouter

from fastapi_zero.schemas import ToDoSchema

router = APIRouter(prefix="/to_do", tags=["to_do"])


@router.post("/", status_code=HTTPStatus.OK)
async def creat_to_do(to_do: ToDoSchema):
    return {"to_dos": ["Tarefa 1", "Tarefa 2"]}
