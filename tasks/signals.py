from django.db import transaction
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from services.cache import bump_user_tasks_version
from tasks.models import Task


@receiver([post_save, post_delete], sender=Task)
def invalidate_task_cache_on_change(sender, instance, **kwargs):
    user_id = getattr(instance, 'user_id', None) or getattr(instance, 'owner_id', None)
    if user_id:
        transaction.on_commit(lambda uid=user_id: bump_user_tasks_version(uid))