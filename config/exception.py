from django_ratelimit.exceptions import Ratelimited
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, content):
    response = exception_handler(exc, content)

    if isinstance(exc, Ratelimited):
        return Response(
            {"detail": "Too many requests. Please wait"},
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )
    return response
