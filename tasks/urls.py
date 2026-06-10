from django.urls import path, include
from rest_framework.routers import  DefaultRouter
from .viewsets import TaskViewSet, TagViewSet

router = DefaultRouter()
router.register('tasks', TaskViewSet, basename='task')
router.register('tags', TagViewSet, basename='tag')

urlpatterns = [
    path('', include(router.urls)),
]