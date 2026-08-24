import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


@pytest.fixture(autouse=True)
def disable_debug_toolbar(settings):
    settings.MIDDLEWARE = [m for m in settings.MIDDLEWARE if "debug_toolbar" not in m]
    settings.INSTALLED_APPS = [
        a for a in settings.INSTALLED_APPS if a != "debug_toolbar"
    ]


User = get_user_model()


@pytest.fixture
def test_user(db):
    return User.objects.create_user(username="test_user", password="password123")


@pytest.fixture
def auth_client(test_user):
    client = APIClient()
    client.force_login(test_user)
    client.force_authenticate(user=test_user)
    return client
