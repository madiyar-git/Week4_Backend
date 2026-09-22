import pytest
from rest_framework import serializers

from tasks.serializers import TaskSerializer


def test_validation_positive_case_200():
    payload = {"title": "                  Valid title                    "}
    response = TaskSerializer.validate_title(value=payload["title"], self=payload)
    assert response == "Valid title"


def test_validation_negative_case_400():
    payload = {"title": "                  Va                   "}
    with pytest.raises(serializers.ValidationError) as exc_info:
        response = TaskSerializer.validate_title(value=payload["title"], self=payload)
    assert "Title must be at least 6 7 characters" in str(exc_info.value)
