import logging

from django.core.cache import cache
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, permissions, status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from apps.users.tasks import send_task_created_notification
from services.cache import (generate_tasks_cache_key, get_jittered_ttl, )
from .models import Tag, Task
from .serializers import TagSerializer, TaskSerializer

logger = logging.getLogger(__name__)


class TaskPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class TagViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TagSerializer
    queryset = Tag.objects.all()

    def get_queryset( self ):
        return Tag.objects.filter(owner=self.request.user)

    def perform_create( self, serializer ):
        serializer.save(owner=self.request.user)


@extend_schema_view(
    list=extend_schema(summary="List tasks", description="Get a list of tasks for the authenticated user."),
    retrieve=extend_schema(summary="Get task by ID", description="Retrieve a specific task by its ID."),
    create=extend_schema(summary="Create task", description="Create a new task."),
    update=extend_schema(summary="Update task", description="Update an existing task."),
    partial_update=extend_schema(summary="Partial update task", description="Partially update a task."),
    destroy=extend_schema(summary="Delete task", description="Delete a task."), )
class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TaskSerializer
    pagination_class = TaskPagination
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ["created_at", "priority", "completed", "title"]
    ordering = ["-created_at"]
    search_fields = ["title", "description"]
    lookup_field = "pk"
    lookup_value_regex = r"\d+"

    def get_queryset( self ):
        queryset = (
            Task.objects.filter(owner=self.request.user).select_related("owner", "category").prefetch_related("tags"))

        completed = self.request.query_params.get("completed")
        if completed is not None:
            queryset = queryset.filter(completed=completed.lower() == "true")

        tag_id = self.request.query_params.get("tag")
        if tag_id:
            queryset = queryset.filter(tags__id=tag_id)
        return queryset.distinct()

    def send_task_created_notification( self, task ):
        try:
            send_task_created_notification.apply_async(args=[task.id], retry=False)
        except Exception as exc:
            logger.warning("Failed to send task notification: %s", exc)
            raise

    def perform_create( self, serializer ):
        task = serializer.save(owner=self.request.user)

        logger.info(
            "New task created: tasks ID =%s, users ID =%s", task.id, task.owner_id, )

        try:
            self.send_task_created_notification(task)
        except Exception:
            pass

    def perform_update( self, serializer ):
        serializer.save()

    def perform_destroy( self, instance ):
        instance.delete()

    def list( self, request, *args, **kwargs ):
        user = request.user
        cache_key = generate_tasks_cache_key(user.id, request.query_params)

        cached_data = None
        try:
            cached_data = cache.get(cache_key)
        except Exception as exc:
            logger.warning("Error reading from the Redis cache: %s", exc)

        if cached_data is not None:
            response = Response(cached_data, status=status.HTTP_200_OK)
            response["X-Cache"] = "HIT"
            return response

        response = super().list(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            try:
                data_to_cache = (dict(response.data) if isinstance(response.data, dict) else list(response.data))
                ttl = get_jittered_ttl(60, 10)
                cache.set(cache_key, data_to_cache, timeout=ttl)
            except Exception as exc:
                logger.warning("Error writing to the Redis cache: %s", exc)

        response["X-Cache"] = "MISS"
        return response
