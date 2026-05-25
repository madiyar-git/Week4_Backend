from django.contrib import admin
from .models import Category, Task


@admin.action(description="Отметить выбранные как выполненные")
def make_completed(modeladmin, request, queryset):
    queryset.update(completed=True)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'completed', 'priority', 'category', 'created_at']

    list_filter = ['completed', 'priority', 'category']

    search_fields = ['title', 'description']

    list_editable = ['completed', 'priority']

    readonly_fields = ['created_at', 'updated_at']

    actions = [make_completed]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ['id', 'name', 'slug']