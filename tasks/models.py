from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default="#1DB954")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tag")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [["name", "owner"]]

        def __str__(self):
            return f"{self.name}({self.owner.username})"


class Task(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="tasks",
        null=False,
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    priority = models.IntegerField(
        choices=[(1, "Low"), (2, "Medium"), (3, "High")],
        default=2,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="tasks")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created_at"]
