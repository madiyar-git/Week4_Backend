from unittest.mock import patch

from rest_framework import status


@patch("apps.users.tasks.send_task_created_notification")
def test_outer_request(mock_service, auth_client):
    payload = {"title": "Hello", "priority": "high", "completed": False}
    response = auth_client.post("/api/tasks/", data=payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert (
        mock_service.called
        or mock_service.delay.called
        or mock_service.apply_async.called
    )


@patch("apps.users.tasks.send_task_created_notification")
def test_outer_request_failure_returns_201(mock_service, auth_client):
    mock_service.side_effect = Exception("Connection error")
    mock_service.delay.side_effect = Exception("Connection error")

    payload = {"title": "Hello", "priority": "high", "completed": False}
    response = auth_client.post("/api/tasks/", data=payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED