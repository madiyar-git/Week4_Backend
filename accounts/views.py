from django.db import connection
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from accounts.serializers import RegisterSerializer
from config.limiterConfig import get_ip_and_username


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class LimiterTokenObtainPairView(TokenObtainPairView):
    @method_decorator(ratelimit(key=get_ip_and_username, rate="5/m", block=True))
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


@extend_schema(exclude=True)
class SecurityTestView(APIView):
    def post(self, request):
        username_input = request.data.get("username", "")
        query = f"SELECT id, username, password FROM auth_user WHERE username = '{username_input}'"
        # query = "SELECT id, username FROM auth_user WHERE username = %s"

        with connection.cursor() as cursor:
            cursor.execute(query)
            # cursor.execute(query, [username_input])
            rows = cursor.fetchall()
        return Response({"result": rows})


# @extend_schema(exclude=True)
# class SecurityTestView(APIView):
#     def post(self, request):
#         username_input = request.data.get("username")
#         users = User.objects.filter(username=username_input).values("id", "username")
#         return Response({"result": list(users)})
