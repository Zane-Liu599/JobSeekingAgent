from fastapi import FastAPI
from platform_common import service_health

from communication_service.settings import CommunicationSettings

settings = CommunicationSettings()

app = FastAPI(
    title="JobSeekingAgent Communication Service",
    version=settings.service_version,
)


@app.get("/health")
def health():
    return service_health(settings.service_name, settings.service_version)


@app.get("/communication/feed")
def feed_placeholder():
    return {
        "items": [],
        "service": settings.service_name,
        "message": "Forum posts and notifications will live here.",
    }
