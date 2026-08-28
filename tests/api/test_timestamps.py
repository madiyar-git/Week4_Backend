import pytest
from freezegun import freeze_time
from rest_framework import status


@pytest.mark.django_db
@freeze_time("2026-08-28 12:00:00")
def test_task_creation_timestamp(auth_client):
    payload = {"title": "Task with frozen time", "priority": "high"}

    response = auth_client.post("/api/tasks/", data=payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED

    created_at = response.data["created_at"]
    assert "2026-08-28" in created_at
