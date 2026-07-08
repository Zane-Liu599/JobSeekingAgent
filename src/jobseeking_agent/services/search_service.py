from dataclasses import dataclass

from jobseeking_agent.db import Job, save_job
from jobseeking_agent.search import build_search_query, search_jobs


@dataclass(frozen=True)
class SavedSearchResult:
    message: str
    saved_count: int
    blocked: bool = False


def search_and_save_jobs(keywords: str, location: str, platform: str) -> SavedSearchResult:
    query = build_search_query(keywords, location, platform)
    saved_count = 0

    def save_found_job(job: Job) -> None:
        nonlocal saved_count
        save_job(job)
        saved_count += 1

    outcome = search_jobs(
        query,
        on_job=save_found_job,
        allow_manual_verification=False,
    )
    return SavedSearchResult(
        message=outcome.message,
        saved_count=saved_count,
        blocked=outcome.blocked,
    )
