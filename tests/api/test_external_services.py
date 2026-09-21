from unittest.mock import patch

from rest_framework import status

from apps.users.tasks import send_task_created_notification


@patch.object(send_task_created_notification, "delay")
@patch.object(send_task_created_notification, "apply_async")
def test_outer_request(mock_apply_async, mock_delay, auth_client):
    payload = {"title": "Hello", "priority": "high", "completed": False}
    response = auth_client.post("/api/tasks/", data=payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    # Проверяем, что таска Celery была вызвана через .delay() или .apply_async()
    assert mock_delay.called or mock_apply_async.called


@patch.object(send_task_created_notification, "delay")
@patch.object(send_task_created_notification, "apply_async")
def test_outer_request_failure_returns_201(mock_apply_async, mock_delay, auth_client):
    mock_delay.side_effect = Exception("Connection error")
    mock_apply_async.side_effect = Exception("Connection error")

    payload = {"title": "Hello", "priority": "high", "completed": False}
    response = auth_client.post("/api/tasks/", data=payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED