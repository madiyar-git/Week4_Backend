import pytest
from rest_framework import status

from tasks.models import Task
from tests.factories import TaskFactory

pytestmark = pytest.mark.django_db


def test_get_tasks_list_with_full_data(auth_client, tasks):
    response = auth_client.get("/api/tasks/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 3
    assert len(response.data["results"]) == 3

    first_item = response.data["results"][0]
    expected_fields = {
        "id",
        "title",
        "description",
        "completed",
        "priority",
        "category",
        "created_at",
        "updated_at",
        "owner",
        "tags",
    }

    assert expected_fields.issubset(first_item.keys())


def test_get_one_task_from_list(auth_client, tasks):
    target_task = tasks[0]
    response = auth_client.get(f"/api/tasks/{target_task.id}/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == target_task.id
    assert response.data["title"] == target_task.title


def test_post_new_task_into_list(auth_client, user):
    initial_count = Task.objects.count()
    payload = {
        "title": "Integration test post method",
        "description": "HElloooooo",
        "completed": False,
        "priority": "medium",
    }

    response = auth_client.post("/api/tasks/", data=payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert Task.objects.count() == initial_count + 1

    created_task = Task.objects.get(id=response.data["id"])
    assert created_task.title == payload["title"]
    assert created_task.owner == user


def test_partial_update_for_task(auth_client, tasks):
    task = tasks[0]
    original_title = task.title
    payload = {"completed": True}

    response = auth_client.patch(f"/api/tasks/{task.id}/", data=payload, format="json")
    assert response.status_code == status.HTTP_200_OK

    task.refresh_from_db()
    assert task.completed is True
    assert task.title == original_title


def test_full_update_for_task(auth_client, tasks):
    task = tasks[0]
    payload = {
        "title": "Updated Title",
        "description": "Updated Description",
        "completed": True,
        "priority": "high",
    }

    response = auth_client.patch(f"/api/tasks/{task.id}/", data=payload, format="json")
    assert response.status_code == status.HTTP_200_OK

    task.refresh_from_db()
    assert task.title == payload["title"]
    assert task.priority == 3


def test_delete_task_from_list(auth_client, tasks):
    task = tasks[0]
    initial_count = Task.objects.count()
    response = auth_client.delete(f"/api/tasks/{task.id}/")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Task.objects.count() == initial_count - 1
    assert not Task.objects.filter(id=task.id).exists()


def test_filter_tasks_by_completed_status(auth_client, user):
    TaskFactory.create_batch(2, owner=user, completed=True)
    TaskFactory.create_batch(1, owner=user, completed=False)

    response = auth_client.get("/api/tasks/?completed=true")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 2
    assert all(item["completed"] is True for item in response.data["results"])


@pytest.mark.parametrize(
    "invalid_payload, expected_field",
    [
        ({"title": ""}, "title"),
        ({"title": "Valid Title", "priority": "gyuidewsefvf"}, "priority"),
    ],
)
def test_create_task_validation_error(auth_client, invalid_payload, expected_field):
    response = auth_client.post("/api/tasks/", data=invalid_payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert expected_field in response.data
