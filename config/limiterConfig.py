import json


def get_ip_and_username(group, request):
    ip = request.META.get("REMOTE_ADDR", "127.0.0.1")
    username = "unknown"
    try:
        if hasattr(request, "data"):
            username = request.data.get("username", "unknown")
        elif request.body:
            data = json.loads(request.body)
            username = data.get("username", "unknown")
    except Exception:
        pass
    return f"{ip}:{username}"
