from django.db import models, connection
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Task, Tag
from .serializers import TaskSerializer, TagSerializer


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
    # queryset = Task.objects.all()

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
        serializer.save(owner=self.request.user)

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
    ordering = ['-created_at']
