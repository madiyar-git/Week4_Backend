import logging

import requests
from celery import shared_task
from django.apps import apps

logger = logging.getLogger(__name__)


@shared_task
def send_task_created_notification(task_id: int):
    Task = apps.get_model("tasks", "Task")
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        logger.warning("Failed to send notification: task id=%s not found", task_id)
        return

    try:
        response = requests.post(
            "https://api.example.com/notify",
            json={"text": f"New task created: {task.title}"},
            timeout=5,
        )
        if response.status_code == 200:
            logger.info("Notification for task id=%s successfully sent.", task.id)
        else:
            logger.error("Notification service error: status=%s", response.status_code)
    except Exception as exc:
        logger.error("Failed to send notification for task ID=%s: %s", task.id, exc)
