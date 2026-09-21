from unittest.mock import patch

from rest_framework import status


@patch("tasks.viewsets.send_task_created_notification")
def test_outer_request(
    mock_service, auth_client, django_capture_on_commit_callbacks
):
    payload = {"title": "Hello", "priority": "high", "completed": False}
    with django_capture_on_commit_callbacks(execute=True):
        response = auth_client.post("/api/tasks/", data=payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    mock_service.apply_async.assert_called_once()


@patch("tasks.viewsets.send_task_created_notification")
def test_outer_request_failure_returns_201(
    mock_service, auth_client, django_capture_on_commit_callbacks
):
    mock_service.apply_async.side_effect = Exception("Connection error")

    payload = {"title": "Hello", "priority": "high", "completed": False}

    with django_capture_on_commit_callbacks(execute=True):
        response = auth_client.post("/api/tasks/", data=payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED