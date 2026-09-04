import pytest
from rest_framework.test import APIClient

from tests.factories import UserFactory, TaskFactory


@pytest.fixture(autouse=True)
def disable_debug_toolbar(settings):
    settings.MIDDLEWARE = [m for m in settings.MIDDLEWARE if "debug_toolbar" not in m]
    settings.INSTALLED_APPS = [
        a for a in settings.INSTALLED_APPS if a != "debug_toolbar"
    ]


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return UserFactory()


@pytest.fixture
def other_user(db):
    return UserFactory()


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def tasks(user):
    return TaskFactory.create_batch(3, owner=user)
