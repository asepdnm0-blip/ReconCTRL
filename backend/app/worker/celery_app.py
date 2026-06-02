from celery import Celery
from app.config import settings

celery_app = Celery(
    "reconctrl",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    worker_prefetch_multiplier=1,
    task_default_queue="celery",
    task_routes={
        "worker.tasks.*": {"queue": "celery"},
    },
)

# Auto-discover tasks in the worker package
celery_app.autodiscover_tasks(["app.worker"], related_name="tasks")
