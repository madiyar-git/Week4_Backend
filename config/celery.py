import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTING_MODULE", "config.settings")

app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Celery debug task executed successfully! Request ID: {self.request.id}")
