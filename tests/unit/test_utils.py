import pytest
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User


def test_django_make_and_check_password():
    raw_password = "my_secret_password_123"

    hashed_password = make_password(raw_password)

    assert hashed_password != raw_password
    assert check_password(raw_password, hashed_password) is True
    assert check_password("wrong_password", hashed_password) is False


def test_user_model_in_memory():
    user = User(username="test_user", first_name="madiyar", last_name="test")
    user.set_password("super_secret")

    assert user.get_full_name() == "madiyar test"
    assert user.check_password("super_secret") is True


def test_saving_user_without_db_mark_raises_error():
    user = User(username="test_user")

    with pytest.raises(RuntimeError) as exc_info:
        user.save()

    assert "Database access not allowed" in str(exc_info.value)
