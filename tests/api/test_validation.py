import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_validate_request_without_required_field_400(auth_client, tasks):

    payload = {
        "title": "",
        "description": "HElloooooo",
        "completed": False,
        "priority": "medium",
    }

    response = auth_client.post("/api/tasks/", data=payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["title"][0].code == "blank"


@pytest.mark.parametrize(
    "method, url, payload, expected_field",
    [
        (
            "post",
            "/api/tasks/",
            {
                "title": "",
                "description": "HElloooooo",
                "completed": False,
                "priority": "medium",
            },
            "title",
        ),
        (
            "post",
            "/api/tasks/",
            {
                "title": "    ",
                "description": "HElloooooo",
                "completed": False,
                "priority": "medium",
            },
            "title",
        ),
        (
            "post",
            "/api/tasks/",
            {
                "title": "Hi",
                "description": "HElloooooo",
                "completed": False,
                "priority": "medium",
            },
            "title",
        ),
        (
            "post",
            "/api/tasks/",
            {
                "title": "HHEllo",
                "description": "HElloooooo",
                "completed": False,
                "priority": "little_bit_medium",
            },
            "priority",
        ),
        (
            "post",
            "/api/tasks/",
            {
                "title": "HHEllo",
                "description": "HElloooooo",
                "completed": [],
                "priority": "medium",
            },
            "completed",
        ),
    ],
)
def test_validate_different_requests_400(
    auth_client, method, url, payload, expected_field
):
    http_method = getattr(auth_client, method)
    response = http_method(url, data=payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert expected_field in response.data
