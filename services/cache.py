import random
from urllib.parse import urlencode

from django.core.cache import cache


def get_user_tasks_version(user_id: int) -> int:
    version_key = f"user:{user_id}:tasks_version"
    version = cache.get(version_key)
    if version is None:
        try:
            cache.set(version_key, 1, timeout=None)
            version = 1
        except Exception:
            version = 1
    return int(version)

def bump_user_tasks_version(user_id: int):
    version_key = f"user:{user_id}:tasks_version"
    try:
        cache.incr(version_key)
    except ValueError:
        cache.set(version_key, 1, timeout=None)
    except Exception:
        pass

def generate_tasks_cache_key(user_id: int, query_params) -> str:
    version = get_user_tasks_version(user_id)
    sorted_params = []
    for key in sorted(query_params.keys()):
        for val in sorted(query_params.getlist(key)):
            sorted_params.append((key, val))
    normalized_query = urlencode(sorted_params)
    return f"user:{user_id}:v{version}:tasks:{normalized_query}"

def get_jittered_ttl(base_ttl: int = 60, jitter: int = 10) -> int:
    return base_ttl + random.randint(-jitter, jitter)