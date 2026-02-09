from http import HTTPStatus

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_zero.models import User, ToDo
from fastapi_zero.database import get_session
from fastapi_zero.security import get_current_user
from fastapi_zero.schemas import ToDoSchema, ToDoResponse

router = APIRouter(prefix="/to_dos", tags=["to_do"])


@router.post("/", status_code=HTTPStatus.OK, response_model=ToDoResponse)
async def creat_to_do(
    to_do: ToDoSchema, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)
):
    # return {"to_dos": ["Tarefa 1", "Tarefa 2"], "to_do": to_do}
    to_do_model = ToDo(description=to_do.description, title=to_do.title, state=to_do.state, user_id=current_user.id)
    session.add(to_do_model)
    await session.commit()
    await session.refresh(to_do_model)
    return to_do_model
