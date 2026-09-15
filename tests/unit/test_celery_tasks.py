from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from requests.exceptions import RequestException

from apps.users.tasks import send_welcome_email_idempotent

User = get_user_model()


@pytest.mark.django_db
class TestCeleryTasksUnit:

    def setup_method(self):
        cache.clear()

    def teardown_method(self):
        cache.clear()

    def test_send_welcome_email_direct_execution(self):
        user = User.objects.create_user(username="unit_user", email="test@example.com")

        result = send_welcome_email_idempotent(user.id)

        assert result is True
        assert cache.get(f"welcome_email_sent:{user.id}") is True

    def test_send_welcome_email_idempotency(self):
        user = User.objects.create_user(
            username="idempotent_user", email="idempotent@example.com"
        )
        assert send_welcome_email_idempotent(user.id) is True
        assert send_welcome_email_idempotent(user.id) is True

    def test_send_welcome_email_retry_on_exception(self):
        user = User.objects.create_user(
            username="retry_user", email="retry@example.com"
        )
        task = send_welcome_email_idempotent

        with patch.object(
            task, "retry", side_effect=RequestException("Network Error")
        ) as mock_retry:
            with patch(
                "apps.users.tasks.cache.set",
                side_effect=RequestException("Network Error"),
            ):
                with pytest.raises(RequestException):
                    task(user.id)

                assert mock_retry.called
                assert cache.get(f"welcome_email_sent:{user.id}") is None
