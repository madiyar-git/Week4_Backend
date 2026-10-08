from django.core.cache import cache
from django.db import connections
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def get( self, request, *args, **kwargs ):
        db_healthy = True
        try:
            connection = connections['default']
            connection.cursor()
        except Exception:
            db_healthy = False

        if not db_healthy:
            return Response(
                {
                    "status": "unhealthy", "database": "unhealthy", "redis": "unknown"
                    }, status=status.HTTP_503_SERVICE_UNAVAILABLE
                )

        redis_healthy = True
        try:
            cache.set('health_check_ping', 'pong', timeout=5)
            redis_healthy = (cache.get('health_check_ping') == 'pong')
        except Exception:
            redis_healthy = False

        overall_status = "ok" if redis_healthy else "degraded"

        return Response(
            {
                "status": overall_status, "database": "healthy", "redis": "healthy" if redis_healthy else "unhealthy"
                }, status=status.HTTP_200_OK
            )
