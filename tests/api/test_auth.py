import pytest
from rest_framework import status

from tasks.models import Task
from tests.factories import TaskFactory

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    "method, url",
    [
        ("get", "/api/tasks/"),
        ("post", "/api/tasks/"),
        ("get", "/api/tasks/1/"),
        ("put", "/api/tasks/1/"),
        ("patch", "/api/tasks/1/"),
        ("delete", "/api/tasks/1/"),
    ],
)
def test_unauth_user_return_401(api_client, method, url):
    http_method = getattr(api_client, method)
    response = http_method(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_invalid_or_expired_token_return_401(api_client):
    api_client.credentials(HTTP_AUTHORIZATION="Bearer invalid_garbage_token_999")
    response = api_client.get("/api/tasks/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_user_sees_only_own_tasks(auth_client, user, other_user):
    TaskFactory.create_batch(3, owner=user)
    TaskFactory.create_batch(2, owner=other_user)

    response = auth_client.get("/api/tasks/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 3

    fetched_owners = {item["owner"] for item in response.data["results"]}
    assert fetched_owners == {user.username}


def test_cannot_update_foreign_task(auth_client, other_user):
    foreign_task = TaskFactory(owner=other_user, title="Original Title")

    payload = {"title": "Change"}

    response = auth_client.patch(
        f"/api/tasks/{foreign_task.id}/", data=payload, format="json"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    foreign_task.refresh_from_db()
    assert foreign_task.title == "Original Title"


def test_cannot_delete_foreign_task(auth_client, other_user):
    foreign_task = TaskFactory(owner=other_user)
    initial_count = Task.objects.count()

    response = auth_client.delete(f"/api/tasks/{foreign_task.id}/")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert Task.objects.count() == initial_count
    assert Task.objects.filter(id=foreign_task.id).exists()


def test_cannot_spoof_owner_on_task_creation(auth_client, user, other_user):
    payload = {
        "title": "owner spoof check",
        "owner": other_user.username,
        "id": other_user.id,
    }

    response = auth_client.post("/api/tasks/", data=payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    created_task = Task.objects.get(id=response.data["id"])
    assert created_task.owner == user
    assert created_task.owner != other_user
