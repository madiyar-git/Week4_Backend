from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework import generics, permissions
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
