from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "qalam",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    timezone="UTC",
    imports=("app.workers.tasks",),
)
