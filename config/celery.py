import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTING_MODULE", "config.settings")

app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.task(bind=True, ignore=True)
def debug_task(self):
    print(f"Celery debug task executed successfully! Request ID: {self.request.id}")


CELERY_BEAT_SCHEDULE = {
    "cleanup-expired-tasks-every-5-min": {
        "task": "apps.tasks.tasks.cleanup_expired_tasks",
        "schedule": 300.0,
    },
    "cleanup-expired-tasks-daily-nightly": {
        "task": "apps.tasks.tasks.cleanup_expired_tasks",
        "schedule": crontab(hour=3, minute=0),
    },
}
