from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from jobseeking_agent.db.models import Job
from jobseeking_agent.search.company_careers import infer_ats_provider
from jobseeking_agent.search.description_formatter import clean_job_description
from jobseeking_agent.search.keyword_search import SearchQuery
from jobseeking_agent.search.safe_search import (
    first_non_empty,
    looks_like_official_apply_url,
    normalize_official_apply_url,
)

SUPPORTED_JOBSPY_PLATFORMS = {
    "indeed": "indeed",
    "linkedin": "linkedin",
    "glassdoor": "glassdoor",
    "google": "google",
    "zip_recruiter": "zip_recruiter",
    "ziprecruiter": "zip_recruiter",
}


@dataclass(frozen=True)
class JobSpySearchOptions:
    results_wanted: int = 25
    hours_old: int | None = 168
    country_indeed: str = "Australia"
    linkedin_fetch_description: bool = True
    description_format: str = "markdown"
    proxies: tuple[str, ...] = ()
    user_agent: str = ""


def is_jobspy_platform(platform: str) -> bool:
    return platform.lower().strip() in SUPPORTED_JOBSPY_PLATFORMS


def search_jobs_with_jobspy(
    query: SearchQuery,
    options: JobSpySearchOptions,
    official_apply_only: bool = True,
) -> list[Job]:
    try:
        from jobspy import scrape_jobs
    except ImportError as exc:
        raise RuntimeError(
            "JobSpy is not installed. Install dependencies with: pip install -r requirements.txt"
        ) from exc

    site_name = SUPPORTED_JOBSPY_PLATFORMS.get(query.platform.lower().strip())
    if not site_name:
        raise ValueError(f"JobSpy does not support platform: {query.platform}")

    kwargs: dict[str, Any] = {
        "site_name": [site_name],
        "search_term": query.keywords,
        "location": query.location,
        "results_wanted": options.results_wanted,
        "description_format": options.description_format,
        "verbose": 0,
    }
    if options.hours_old is not None:
        kwargs["hours_old"] = options.hours_old
    if site_name in {"indeed", "glassdoor"}:
        kwargs["country_indeed"] = options.country_indeed
    if site_name == "linkedin":
        kwargs["linkedin_fetch_description"] = options.linkedin_fetch_description
    if options.proxies:
        kwargs["proxies"] = list(options.proxies)
    if options.user_agent:
        kwargs["user_agent"] = options.user_agent
    if site_name == "google":
        kwargs["google_search_term"] = f"{query.keywords} jobs near {query.location}".strip()

    dataframe = scrape_jobs(**kwargs)
    records = dataframe.to_dict("records") if hasattr(dataframe, "to_dict") else list(dataframe)
    return normalize_jobspy_records(
        records,
        fallback_platform=site_name,
        official_apply_only=official_apply_only,
    )


def normalize_jobspy_records(
    records: list[dict[str, Any]],
    fallback_platform: str,
    official_apply_only: bool = True,
) -> list[Job]:
    jobs: list[Job] = []
    seen: set[str] = set()

    for record in records:
        title = normalize_text(record_value(record, "title"))
        job_url = normalize_text(record_value(record, "job_url"))
        if not title or not job_url or job_url in seen:
            continue

        platform = normalize_text(record_value(record, "site")) or fallback_platform
        official_apply_url = official_apply_from_record(record, platform)
        if official_apply_only and not official_apply_url:
            continue

        seen.add(job_url)
        jobs.append(
            Job(
                title=title[:140],
                company=normalize_text(record_value(record, "company")),
                location=normalize_location(record),
                employment_type=normalize_text(record_value(record, "job_type")),
                salary=normalize_salary(record),
                platform=platform,
                job_url=job_url,
                official_apply_url=official_apply_url,
                description=clean_job_description(record_value(record, "description")),
                status="found",
            )
        )
    return jobs


def official_apply_from_record(record: dict[str, Any], platform: str) -> str:
    candidate_keys = (
        "direct_url",
        "direct_apply_url",
        "external_url",
        "external_apply_url",
        "application_url",
        "apply_url",
        "company_url",
        "job_url_direct",
        "job_url_direct_apply",
        "redirect_url",
        "url_direct",
        "job_url",
    )
    for key in candidate_keys:
        value = normalize_text(record_value(record, key))
        if not value:
            continue
        normalized = normalize_official_apply_url(value, value, platform)
        if normalized:
            return normalized
        if looks_like_official_apply_url(value, "company"):
            return value
    return ""


def record_value(record: dict[str, Any], key: str) -> Any:
    value = record.get(key)
    if value is not None:
        return value
    lowered = key.lower()
    for record_key, record_value_item in record.items():
        if str(record_key).lower() == lowered:
            return record_value_item
    return ""


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value)
    if text.lower() in {"nan", "none", "nat"}:
        return ""
    return " ".join(text.split())


def normalize_location(record: dict[str, Any]) -> str:
    location = normalize_text(record_value(record, "location"))
    if location:
        return location
    parts = [
        normalize_text(record_value(record, "city")),
        normalize_text(record_value(record, "state")),
        normalize_text(record_value(record, "country")),
    ]
    return ", ".join(part for part in parts if part)


def normalize_salary(record: dict[str, Any]) -> str:
    interval = normalize_text(record_value(record, "interval"))
    currency = normalize_text(record_value(record, "currency"))
    min_amount = normalize_text(record_value(record, "min_amount"))
    max_amount = normalize_text(record_value(record, "max_amount"))
    amount = first_non_empty(
        " - ".join(part for part in (min_amount, max_amount) if part),
        min_amount,
        max_amount,
    )
    if not amount:
        return ""
    prefix = f"{currency} " if currency else ""
    suffix = f" / {interval}" if interval else ""
    return f"{prefix}{amount}{suffix}"


def ats_provider_from_job(job: Job) -> str:
    return infer_ats_provider(job.official_apply_url or job.job_url)
