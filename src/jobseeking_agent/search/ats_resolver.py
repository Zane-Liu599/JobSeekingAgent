from __future__ import annotations

from dataclasses import replace

from jobseeking_agent.db.models import Company, Job
from jobseeking_agent.search.company_careers import (
    discover_company_source,
    infer_ats_provider,
    scan_company_careers,
)
from jobseeking_agent.search.safe_search import (
    discover_official_apply_url,
    first_non_empty,
    looks_like_official_apply_url,
)


def resolve_official_apply_job(
    job: Job,
    keywords: str = "",
    location: str = "",
    allow_search_discovery: bool = False,
) -> Job:
    official_url = first_non_empty(job.official_apply_url)
    if official_url and looks_like_official_apply_url(official_url, "company"):
        return replace(job, official_apply_url=official_url)

    ats_job = resolve_from_company_ats(job, keywords, location)
    if ats_job:
        return merge_job(job, ats_job)

    if allow_search_discovery:
        discovered = discover_official_apply_url(
            job.title,
            job.company,
            job.location or location,
            job.platform,
        )
        if discovered:
            return replace(job, official_apply_url=discovered)

    return job


def resolve_from_company_ats(job: Job, keywords: str = "", location: str = "") -> Job | None:
    if not job.company:
        return None

    company = discover_company_source(job.company)
    if not company.careers_url:
        return None

    scan_result = scan_company_careers(
        Company(
            name=job.company,
            website_url=company.website_url,
            careers_url=company.careers_url,
            ats_provider=company.ats_provider or infer_ats_provider(company.careers_url),
            source=company.source,
        ),
        keywords=keywords or job.title,
        location=location or job.location,
        limit=25,
    )
    return best_matching_company_job(job, scan_result.jobs)


def best_matching_company_job(source_job: Job, company_jobs: list[Job]) -> Job | None:
    if not company_jobs:
        return None

    source_tokens = significant_tokens(source_job.title)
    if not source_tokens:
        return company_jobs[0]

    scored = [
        (len(source_tokens & significant_tokens(candidate.title)), candidate)
        for candidate in company_jobs
    ]
    scored.sort(key=lambda item: item[0], reverse=True)
    score, candidate = scored[0]
    return candidate if score > 0 else None


def significant_tokens(value: str) -> set[str]:
    normalized = "".join(
        character.lower() if character.isalnum() else " "
        for character in value
    )
    return {
        token
        for token in normalized.split()
        if len(token) > 2
    }


def merge_job(source_job: Job, resolved_job: Job) -> Job:
    return replace(
        source_job,
        company=first_non_empty(source_job.company, resolved_job.company),
        location=first_non_empty(source_job.location, resolved_job.location),
        employment_type=first_non_empty(source_job.employment_type, resolved_job.employment_type),
        salary=first_non_empty(source_job.salary, resolved_job.salary),
        official_apply_url=first_non_empty(
            resolved_job.official_apply_url,
            source_job.official_apply_url,
        ),
        description=first_non_empty(source_job.description, resolved_job.description),
    )
