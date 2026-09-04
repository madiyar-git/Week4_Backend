from unittest.mock import patch

from rest_framework import status

from tasks.viewsets import TaskViewSet


@patch.object(TaskViewSet, "send_task_created_notification")
def test_outer_request(mock_service, auth_client):
    mock_service.return_value = True
    payload = {"title": "Hello", "priority": "high", "completed": False, "id": 1}
    response = auth_client.post("/api/tasks/", data=payload)

    assert response.status_code == status.HTTP_201_CREATED
    mock_service.assert_called_once()


@patch.object(TaskViewSet, "send_task_created_notification")
def test_outer_request_failure_returns_201(mock_service, auth_client):
    mock_service.side_effect = Exception("Connection error")

    payload = {"title": "Hello", "priority": "high", "completed": False}
    response = auth_client.post("/api/tasks/", data=payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
