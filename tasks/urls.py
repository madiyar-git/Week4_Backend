from django.urls import path
from .views import TaskListAPIView, TaskDetailAPIView
from rest_framework.routers import  DefaultRouter
from .viewsets import TaskViewSet

router = DefaultRouter()
router.register('tasks-v2', TaskViewSet, basename='task')

urlpatterns = [
    path('tasks/', TaskListAPIView.as_view(), name='task-list'),
    path('tasks/<int:pk>/', TaskDetailAPIView.as_view(), name='task-detail'),
]

urlpatterns += router.urls