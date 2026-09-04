import pytest

from tasks.models import Task
from tests.factories import TaskFactory


@pytest.mark.django_db
def test_isolation_first_run():
    TaskFactory()
    assert Task.objects.count() == 1


@pytest.mark.django_db
def test_isolation_second_run():
    TaskFactory()
    assert Task.objects.count() == 1