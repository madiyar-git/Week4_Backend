import logging
from urllib.parse import urlencode

from django.core.cache import cache
from django.db import models, connection
from rest_framework import permissions, viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from apps.users.tasks import send_task_created_notification
from .models import Task, Tag
from .serializers import TaskSerializer, TagSerializer

logger = logging.getLogger(__name__)


class TaskPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class TagViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TagSerializer
    queryset = Tag.objects.all()

    def get_queryset(self):
        return Tag.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TaskSerializer
    pagination_class = TaskPagination
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ["created_at", "priority", "completed", "title"]
    ordering = ["-created_at"]
    search_fields = ["title", "description"]

    def _generate_cache_key(self, user_id: int, query_params) -> str:
        sorted_params = []
        for key in sorted(query_params.keys()):
            for val in sorted(query_params.getlist(key)):
                sorted_params.append((key, val))

        normalized_query = urlencode(sorted_params)
        return f"user:{user_id}:tasks:{normalized_query}"

    def list(self, request, *args, **kwargs):
        user = request.user
        cache_key = self._generate_cache_key(user.id, request.query_params)

        cached_data = None
        try:
            cached_data = cache.get(cache_key)
            print(f"DEBUG: GET '{cache_key}' -> found: {cached_data is not None}")
        except Exception as exc:
            logger.warning("Ошибка чтения из Redis кэша: %s", exc)

        if cached_data is not None:
            response = Response(cached_data, status=status.HTTP_200_OK)
            response["X-Cache"] = "HIT"
            return response

        response = super().list(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            try:
                data_to_cache = (
                    dict(response.data)
                    if isinstance(response.data, dict)
                    else response.data
                )
                success = cache.set(cache_key, data_to_cache, timeout=60)
                print(f"DEBUG: SET '{cache_key}' -> success: {success}")
            except Exception as exc:
                print(f"DEBUG EXCEPTION ON SET: {exc}")
                logger.warning("Ошибка записи в Redis кэш: %s", exc)

        response["X-Cache"] = "MISS"
        return response

    def get_queryset(self):
        queryset = (
            Task.objects.filter(owner=self.request.user)
            .select_related("owner", "category")
            .prefetch_related("tags")
        )

        completed = self.request.query_params.get("completed")
        if completed is not None:
            queryset = queryset.filter(completed=completed.lower() == "true")

        tag_id = self.request.query_params.get("tag")
        if tag_id:
            queryset = queryset.filter(tags__id=tag_id)
        return queryset.distinct()

    def perform_create(self, serializer):
        task = serializer.save(owner=self.request.user)

        try:
            send_task_created_notification.apply_async(args=[task.id], retry=False)
        except Exception as exc:
            logger.error(
                "Failed to send task to Celery for task_id=%s: %s",
                task.id,
                exc,
            )

    @action(detail=False, methods=["get"], url_path="stats")
    def stats(self, request):
        user = request.user

        orm_stats = Task.objects.filter(owner=user).aggregate(
            total=models.Count("id"),
            completed_tasks=models.Count("id", filter=models.Q(completed=True)),
            active=models.Count("id", filter=models.Q(completed=False)),
        )

        raw_query = """
            SELECT
                COUNT(*) AS total,
                COUNT(*) FILTER (WHERE completed = TRUE) AS completed,
                COUNT(*) FILTER (WHERE completed = FALSE) AS active
            FROM tasks_task
            WHERE owner_id = %s;
        """

        with connection.cursor() as cursor:
            cursor.execute(raw_query, (user.id,))
            row = cursor.fetchone()
            raw_stats = {"total": row[0], "completed_tasks": row[1], "active": row[2]}

        return Response({"orm": orm_stats, "raw": raw_stats})

    ordering = ["-created_at"]
