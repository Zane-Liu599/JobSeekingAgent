from dataclasses import dataclass
from datetime import UTC, datetime


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


@dataclass(frozen=True)
class Job:
    title: str
    company: str
    location: str = ""
    platform: str = "manual"
    job_url: str = ""
    description: str = ""
    status: str = "found"
    match_score: float | None = None
    created_at: str = ""
    id: int | None = None


@dataclass(frozen=True)
class Application:
    job_id: int
    resume_path: str = ""
    cover_letter_path: str = ""
    submitted_at: str = ""
    status: str = "draft"
    notes: str = ""
    id: int | None = None
