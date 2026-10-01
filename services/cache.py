from urllib.parse import urlencode


def generate_tasks_cache_key(user_id: int, query_params) -> str:
    sorted_params = []

    for key in sorted(query_params.keys()):
        values = query_params.getlist(key)
        for val in sorted(values):
            sorted_params.append((key, val))

    normalized_query = urlencode(sorted_params)
    return f"user:{user_id}:tasks:{normalized_query}"
