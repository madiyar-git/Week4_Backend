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
def test_tasks_cache_hit_zero_queries( auth_client, user, django_assert_num_queries ):
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
def test_tasks_cache_user_isolation( api_client, user, other_user ):
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

    results_a = (res_a.data.get("results", res_a.data) if isinstance(res_a.data, dict) else res_a.data)
    results_b = (res_b.data.get("results", res_b.data) if isinstance(res_b.data, dict) else res_b.data)

    titles_a = [t["title"] for t in results_a]
    titles_b = [t["title"] for t in results_b]

    assert "Task User A" in titles_a
    assert "Task User A" not in titles_b
    assert "Task User B" in titles_b


@pytest.mark.django_db(transaction=True)
def test_task_mutation_invalidates_cache( auth_client, user ):
    url = reverse("task-list")

    res_miss = auth_client.get(url)
    assert res_miss.headers.get("X-Cache") == "MISS"
    assert len(res_miss.data.get("results", res_miss.data)) == 0

    res_hit = auth_client.get(url)
    assert res_hit.headers.get("X-Cache") == "HIT"

    response = auth_client.post(url, {"title": "New Task via API"})
    assert response.status_code == status.HTTP_201_CREATED

    res_after = auth_client.get(url)
    assert res_after.headers.get("X-Cache") == "MISS"

    results = res_after.data.get("results", res_after.data)
    assert len(results) == 1
    assert results[0]["title"] == "New Task via API"


@pytest.mark.django_db
def test_mutation_does_not_affect_other_user( api_client, user, other_user ):
    url = reverse("task-list")

    api_client.force_authenticate(user=user)
    api_client.get(url)

    api_client.force_authenticate(user=other_user)
    api_client.post(url, {"title": "Task by User B"})

    api_client.force_authenticate(user=user)
    res_a = api_client.get(url)

    results_a = res_a.data.get("results", res_a.data)
    assert len(results_a) == 0


@pytest.mark.django_db
def test_cache_isolation_between_users( api_client, user, other_user ):
    url = reverse("task-list")

    api_client.force_authenticate(user=user)
    res_a_1 = api_client.get(url)
    assert res_a_1.headers.get("X-Cache") == "MISS"

    res_a_2 = api_client.get(url)
    assert res_a_2.headers.get("X-Cache") == "HIT"

    api_client.force_authenticate(user=other_user)
    res_b_create = api_client.post(url, {"title": "Private Task of User B"})
    assert res_b_create.status_code == status.HTTP_201_CREATED

    api_client.force_authenticate(user=user)
    res_a_3 = api_client.get(url)
    assert res_a_3.headers.get("X-Cache") == "HIT"

    results_a = res_a_3.data.get("results", res_a_3.data)
    assert len(results_a) == 0

    api_client.force_authenticate(user=other_user)
    res_b_list = api_client.get(url)
    assert res_b_list.headers.get("X-Cache") == "MISS"
    results_b = res_b_list.data.get("results", res_b_list.data)
    assert len(results_b) == 1
    assert results_b[0]["title"] == "Private Task of User B"
