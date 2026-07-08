import os

from celery import Celery

redis_url = os.getenv("REDIS_URL", "redis://redis:6379/1")

celery_app = Celery(
    "ai_service",
    broker=redis_url,
    backend=redis_url,
)


@celery_app.task(name="ai_service.ping")
def ping() -> str:
    return "pong"
