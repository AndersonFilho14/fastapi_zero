import pytest
import factory
import factory.fuzzy

from fastapi_zero.models import ToDo, ToDoState


@pytest.mark.asyncio
async def test_create_todo(client, token):
    response = await client.post(
        "/to_dos/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Test todo",
            "description": "Test todo description",
            "state": "draft",
        },
    )
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


class ToDoFactory(factory.Factory):
    class Meta:
        model = ToDo

    title = factory.Faker("text")
    description = factory.Faker("text")
    state = factory.fuzzy.FuzzyChoice(ToDoState)
    user_id = 1
