from http import HTTPStatus

import factory
import factory.fuzzy
import pytest

from fastapi_zero.models import ToDo, ToDoState


@pytest.mark.asyncio
async def test_create_to_do(client, token):
    response = await client.post(
        "/to_dos/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Test todo",
            "description": "Test todo description",
            "state": "draft",
        },
    )
    breakpoint()
    assert response.json() == {
        "id": 1,
        "title": "Test todo",
        "description": "Test todo description",
        "state": "draft",
    }


@pytest.mark.asyncio
async def test_list_todos_should_return_5_to_dos(session, client, user, token):
    expected_to_dos = 5
    session.add_all(ToDoFactory.create_batch(expected_to_dos, user_id=user.id))
    await session.commit()

    response = await client.get(
        "/to_dos/",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert len(response.json()["to_dos"]) == expected_to_dos


@pytest.mark.asyncio
async def test_list_todos_pagination_should_return_2_to_dos(session, user, client, token) -> None:

    expected_to_dos = 2
    session.add_all(ToDoFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = await client.get(
        "/to_dos/?offset=1&limit=2",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert len(response.json()["to_dos"]) == expected_to_dos


@pytest.mark.asyncio
async def test_list_todos_filter_title_should_return_5_to_dos(session, user, client, token):
    expected_to_dos = 5
    session.add_all(ToDoFactory.create_batch(expected_to_dos, user_id=user.id, title="Test to_do 1"))
    session.add_all(ToDoFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = await client.get(
        "/to_dos/?title=Test to_do 1",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert len(response.json()["to_dos"]) == expected_to_dos


@pytest.mark.asyncio
async def test_list_todos_filter_description_should_return_5_to_dos(session, user, client, token):
    expected_to_dos = 5
    session.add_all(
        ToDoFactory.create_batch(expected_to_dos, user_id=user.id, description="description")
        + ToDoFactory.create_batch(5, user_id=user.id, description="mock")
    )

    await session.commit()

    response = await client.get(
        "/to_dos/?description=desc",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert len(response.json()["to_dos"]) == expected_to_dos


@pytest.mark.asyncio
async def test_list_todos_filter_state_should_return_5_to_dos(session, user, client, token):
    expected_to_dos = 5
    session.add_all(ToDoFactory.create_batch(expected_to_dos, user_id=user.id, state=ToDoState.draft))

    await session.commit()

    response = await client.get(
        "/to_dos/?state=draft",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert len(response.json()["to_dos"]) == expected_to_dos


@pytest.mark.asyncio
async def test_delete_to_do_error(client, token):
    response = await client.delete(f"/to_dos/{10}", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "Achou essa tarefa não cumpade"}


@pytest.mark.asyncio
async def test_delete_to_do_success(session, user, client, token):

    to_do = ToDoFactory.create(user_id=user.id)
    session.add(to_do)
    await session.commit()
    await session.refresh(to_do)

    response = await client.delete(f"/to_dos/{to_do.id}", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Tarefa deletada com sucesso chefia"}


@pytest.mark.asyncio
async def test_update_to_do_failure(client, token):
    response = await client.patch(
        "/to_dos/10",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["detail"] == "Achou essa tarefa não"


@pytest.mark.asyncio
async def test_update_to_do_success(client, token, session, user):
    to_do = ToDoFactory(user_id=user.id)
    session.add(to_do)
    await session.commit()
    await session.refresh(to_do)
    breakpoint()
    data = {
        "title": "mock title",
        "description": "mock desc",
        "state": "doing",
    }

    response = await client.patch(
        f"/to_dos/{to_do.id}",
        headers={"Authorization": f"Bearer {token}"},
        json=data,
    )

    data["id"] = to_do.id

    assert response.status_code == HTTPStatus.OK
    assert response.json() == data


class ToDoFactory(factory.Factory):
    class Meta:
        model = ToDo

    title = factory.Faker("text")
    description = factory.Faker("text")
    state = factory.fuzzy.FuzzyChoice(ToDoState)
    user_id = 1
