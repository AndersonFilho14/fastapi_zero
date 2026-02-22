from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_zero.database import get_session
from fastapi_zero.models import ToDo, User
from fastapi_zero.schemas import FilterToDo, Message, ToDoListResponse, ToDoResponse, ToDoSchema, ToDoUpdate
from fastapi_zero.security import get_current_user

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


@router.get("/", status_code=HTTPStatus.OK, response_model=ToDoListResponse)
async def list_to_dos(
    to_dos_filter: Annotated[FilterToDo, Query()],
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    query = select(ToDo).where(ToDo.user_id == current_user.id)

    if to_dos_filter.title:
        query = query.filter(ToDo.title.contains(to_dos_filter.title))

    if to_dos_filter.description:
        query = query.filter(ToDo.description.contains(to_dos_filter.description))

    if to_dos_filter.state:
        query = query.filter(ToDo.state == to_dos_filter.state)

    result = await session.scalars(query.limit(to_dos_filter.limit).offset(to_dos_filter.offset))

    return {"to_dos": result.all()}


@router.delete("/{to_do_id}", status_code=HTTPStatus.OK, response_model=Message)
async def delete_to_do(
    to_do_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.scalar(select(ToDo).where(ToDo.id == to_do_id, current_user.id == ToDo.user_id))

    if not result:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Achou essa tarefa não cumpade")

    await session.delete(result)

    return Message(message="Tarefa deletada com sucesso chefia")


@router.patch("/{to_do_id}", status_code=HTTPStatus.OK, response_model=ToDoResponse)
async def patch_to_do(
    to_do_id: int,
    to_do: ToDoUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):

    db_to_do = await session.scalar(select(ToDo).filter(ToDo.user_id == current_user.id, ToDo.id == to_do_id))

    if not db_to_do:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Achou essa tarefa não")

    for key, value in to_do.model_dump(exclude_unset=True).items():
        setattr(db_to_do, key, value)

    session.add(db_to_do)
    await session.commit()
    await session.refresh(db_to_do)

    return db_to_do
