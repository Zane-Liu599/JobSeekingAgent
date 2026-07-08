from fastapi import FastAPI
from platform_common import service_health

from identity_service.settings import IdentitySettings

settings = IdentitySettings()

app = FastAPI(
    title="JobSeekingAgent Identity Service",
    version=settings.service_version,
)


@app.get("/health")
def health():
    return service_health(settings.service_name, settings.service_version)


@app.get("/identity/me")
def current_identity_placeholder():
    return {
        "authenticated": False,
        "service": settings.service_name,
        "message": "Authentication endpoints will live here.",
    }
