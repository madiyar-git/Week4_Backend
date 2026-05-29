from rest_framework import viewsets
from .models import Task
from .serializers import TaskSerializer
from rest_framework import permissions


class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        qs = Task.objects.filter(owner=self.request.user)
        completed = self.request.query_params.get('completed')
        if completed is not None:
            qs = qs.filter(completed=completed.lower() == 'true')
        return qs
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    ordering = ['-created_at']