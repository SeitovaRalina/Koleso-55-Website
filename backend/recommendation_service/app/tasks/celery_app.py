from celery import Celery
from kombu import Exchange, Queue
from app.core.config import get_settings
import logging

settings = get_settings()

celery_app = Celery(
    "recommender",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=1800,
    task_soft_time_limit=1500,

    task_default_retry_delay=60,
    task_max_retries=3,
    task_default_queue='recommender',
    task_default_exchange='recommender',
    task_default_routing_key='recommender',
    task_queues=(
        Queue('recommender', Exchange('recommender', type='direct'), routing_key='recommender'),
    ),
    task_routes={
        'app.tasks.training.*': {'queue': 'recommender', 'routing_key': 'recommender'},
    },
)

celery_app.autodiscover_tasks(["app.tasks"])
celery_app.conf.imports = ("app.tasks.training",)

logger = logging.getLogger(__name__)
logger.info("Celery app initialized with broker: %s and backend: %s", settings.CELERY_BROKER_URL, settings.CELERY_RESULT_BACKEND)
