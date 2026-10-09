import logging

import pytest


@pytest.mark.django_db
def test_task_creation_logging(auth_client, user, caplog):
    caplog.set_level(logging.INFO)

    url = "/api/tasks/"
    payload = {
        "title": "Test Task",
        "description": "Test Task Description",
    }

    response = auth_client.post(url, data=payload)

    assert response.status_code == 201, f"Server`s response: {response.data}"

    expected_log_substring = f"users ID ={user.id}"
    assert any(expected_log_substring in record.message for record in caplog.records), (
        f"Log not found. Substring expected: '{expected_log_substring}'"
    )
