import pytest
from rest_framework import status


@pytest.mark.django_db
def test_user_see_own_tasks(auth_client, tasks):
    response = auth_client.get("/api/tasks/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 3


@pytest.mark.django_db
def test_unauth_user_cant_see_list(api_client):
    response = api_client.get("/api/tasks/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
