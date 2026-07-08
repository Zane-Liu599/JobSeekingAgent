from datetime import UTC, datetime

from pydantic import BaseModel


class HealthResponse(BaseModel):
    service: str
    status: str = "ok"
    version: str = "0.1.0"
    timestamp: str


def service_health(service_name: str, version: str = "0.1.0") -> HealthResponse:
    return HealthResponse(
        service=service_name,
        version=version,
        timestamp=datetime.now(UTC).isoformat(timespec="seconds"),
    )
