import pytest


@pytest.mark.django_db
def test_healthcheck_returns_200(auth_client):
    response = auth_client.get("/api/tasks/")
    assert response.status_code == 200
