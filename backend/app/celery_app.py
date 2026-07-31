from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery("keuringen", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_routes={
        "app.workers.ai_jobs.*": {"queue": "interactive"},
        "app.workers.reminders.*": {"queue": "batch"},
    },
    beat_schedule={
        "check-inspection-reminders": {
            "task": "app.workers.reminders.check_inspection_reminders",
            "schedule": 3600.0,
        },
    },
)

celery_app.autodiscover_tasks(["app.workers"])
