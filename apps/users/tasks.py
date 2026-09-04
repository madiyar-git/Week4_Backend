import logging

import requests
from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.cache import cache
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task(
    bind=True,
    autoretry_for=(RequestException,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=5,
    soft_time_limit=10,
    time_limit=15,
)
def send_task_created_notification(self, task_id: int):
    Task = apps.get_model("tasks", "Task")
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        logger.warning("Notification skipped: Task id=%s not found", task_id)
        return

    logger.info(
        "Task [%s] (Attempt %s/5): Sending notification for task_id=%s",
        self.request.id,
        self.request.retries + 1,
        task.id,
    )

    try:
        response = requests.post(
            "https://api.example.com/notify",
            json={"text": f"New task created: {task.title}"},
            timeout=5,
        )
        response.raise_for_status()
        logger.info("Notification for task id=%s successfully sent.", task.id)
    except SoftTimeLimitExceeded:
        logger.error(
            "Task [%s]: Time limit exceeded while notifying task_id=%s",
            self.request.id,
            task.id,
        )
        raise


@shared_task(bind=True, max_retries=3, soft_time_limit=10, time_limit=15)
def send_welcome_email_idempotent(self, user_id: int):
    request_id = self.request.id
    attempt = self.request.retries + 1

    # 1. Проверяем флаг идемпотентности в Redis
    cache_key = f"welcome_email_sent:{user_id}"
    if cache.get(cache_key):
        logger.info(
            "Task [%s]: Email already sent to User id=%s. Skipping (Idempotent).",
            request_id,
            user_id,
        )
        return True

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.warning(
            "Task [%s]: User id=%s not found. Skipping.", request_id, user_id
        )
        return False

    logger.info(
        "Task [%s] (Attempt %s/3): Sending welcome email to User id=%s...",
        request_id,
        attempt,
        user_id,
    )

    try:
        # 2. Фиксируем успешную отправку в кэш (например, на 24 часа)
        cache.set(cache_key, True, timeout=86400)

        logger.info(
            "Task [%s]: Email successfully sent to User id=%s", request_id, user_id
        )
        return True

    except RequestException as exc:
        # В случае ошибки удаляем ключ из кэша, чтобы ретрай мог попробовать снова
        cache.delete(cache_key)
        countdown = 2**self.request.retries
        logger.warning(
            "Task [%s]: Attempt %s failed (%s). Retrying in %ss...",
            request_id,
            attempt,
            exc,
            countdown,
        )
        raise self.retry(exc=exc, countdown=countdown)


@shared_task(
    bind=True,
    autoretry_for=(RequestException,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=5,
    soft_time_limit=10,
    time_limit=15,
)
def fetch_external_status_declarative(self):
    request_id = self.request.id
    retries = self.request.retries
    logger.info(
        "Task [%s] (Attempt %s/5): Calling unstable external API...",
        request_id,
        retries + 1,
    )

    response = requests.get("https://httpbin.org/status/500", timeout=3)
    response.raise_for_status()
    return response.status_code
