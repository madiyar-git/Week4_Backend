from rest_framework import viewsets
from .models import Task, Tag
from .serializers import TaskSerializer, TagSerializer
from rest_framework import permissions

class TagViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TagSerializer

    def get_queryset(self):
        return Tag.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        qs = Task.objects.filter(owner=self.request.user)
        completed = self.request.query_params.get('completed')
        if completed is not None:
            qs = qs.filter(completed=completed.lower() == 'true')

        tag_id = self.request.query_params.get('tag')
        if tag_id:
            qs = qs.filter(tags__id=tag_id)
        return qs.distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)