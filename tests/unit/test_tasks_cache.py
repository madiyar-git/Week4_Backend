import pytest
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status

from tests.factories import TaskFactory


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.mark.django_db
def test_tasks_cache_hit_zero_queries(auth_client, user, django_assert_num_queries):
    TaskFactory.create_batch(3, owner=user)

    url = reverse("task-list")

    res1 = auth_client.get(url)
    assert res1.status_code == status.HTTP_200_OK
    assert res1.headers.get("X-Cache") == "MISS"

    with django_assert_num_queries(0):
        res2 = auth_client.get(url)
        assert res2.status_code == status.HTTP_200_OK
        assert res2.headers.get("X-Cache") == "HIT"
        assert res1.data == res2.data


@pytest.mark.django_db
def test_tasks_cache_user_isolation(api_client, user, other_user):
    TaskFactory.create(owner=user, title="Task User A")
    TaskFactory.create(owner=other_user, title="Task User B")

    url = reverse("task-list")

    api_client.force_authenticate(user=user)
    res_a = api_client.get(url)
    assert res_a.status_code == status.HTTP_200_OK
    assert res_a.headers.get("X-Cache") == "MISS"

    api_client.force_authenticate(user=other_user)
    res_b = api_client.get(url)
    assert res_b.status_code == status.HTTP_200_OK
    assert res_b.headers.get("X-Cache") == "MISS"

    results_a = (
        res_a.data.get("results", res_a.data)
        if isinstance(res_a.data, dict)
        else res_a.data
    )
    results_b = (
        res_b.data.get("results", res_b.data)
        if isinstance(res_b.data, dict)
        else res_b.data
    )

    titles_a = [t["title"] for t in results_a]
    titles_b = [t["title"] for t in results_b]

    assert "Task User A" in titles_a
    assert "Task User A" not in titles_b
    assert "Task User B" in titles_b
