from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse
from platform_common import service_health
from pydantic import BaseModel, Field

from crawler_service.admin_ui import ADMIN_HTML
from crawler_service.settings import CrawlerSettings, split_csv
from jobseeking_agent.db import (
    Company,
    Job,
    delete_jobs,
    get_job,
    init_db,
    list_companies,
    list_jobs,
    save_company,
    save_job,
    update_company_scan_time,
    update_job,
)
from jobseeking_agent.search import build_search_query, search_jobs
from jobseeking_agent.search.ats_resolver import resolve_official_apply_job
from jobseeking_agent.search.company_careers import discover_company_source, scan_company_careers
from jobseeking_agent.search.jobspy_provider import (
    JobSpySearchOptions,
    is_jobspy_platform,
    search_jobs_with_jobspy,
)
from jobseeking_agent.utils.file_manager import ensure_local_directories

settings = CrawlerSettings()

app = FastAPI(
    title="JobSeekingAgent Crawler Service",
    version=settings.service_version,
)


class CrawlOnceRequest(BaseModel):
    keywords: str = Field(min_length=1)
    location: str = ""
    platform: str = "seek"


class CrawlRunRequest(BaseModel):
    keywords: list[str] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)
    platforms: list[str] = Field(default_factory=list)


class CrawlCompanyRequest(BaseModel):
    company_name: str = Field(min_length=1)
    careers_url: str = ""
    website_url: str = ""
    ats_provider: str = ""
    keywords: str = ""
    location: str = ""


class CrawlResult(BaseModel):
    keywords: str
    location: str
    platform: str
    message: str
    found_count: int
    saved_count: int
    blocked: bool


class CompanyResult(BaseModel):
    company: dict[str, str | int | None]
    message: str
    found_count: int
    saved_count: int


class JobUpdateRequest(BaseModel):
    title: str = Field(min_length=1)
    company: str = Field(min_length=1)
    location: str = ""
    employment_type: str = ""
    salary: str = ""
    platform: str = "manual"
    job_url: str = ""
    official_apply_url: str = ""
    description: str = ""
    status: str = "found"
    match_score: float | None = None


class DeleteJobsRequest(BaseModel):
    job_ids: list[int] = Field(min_length=1)


def require_admin(x_crawler_token: str = Header(default="")) -> None:
    if settings.admin_token and x_crawler_token != settings.admin_token:
        raise HTTPException(status_code=401, detail="Invalid crawler admin token")


def serialize_job(job: Job) -> dict[str, str | int | float | None]:
    return {
        "id": job.id,
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "employment_type": job.employment_type,
        "salary": job.salary,
        "platform": job.platform,
        "job_url": job.job_url,
        "official_apply_url": job.official_apply_url,
        "description": job.description,
        "status": job.status,
        "match_score": job.match_score,
        "created_at": job.created_at,
    }


def serialize_company(company: Company) -> dict[str, str | int | None]:
    return {
        "id": company.id,
        "name": company.name,
        "website_url": company.website_url,
        "careers_url": company.careers_url,
        "ats_provider": company.ats_provider,
        "source": company.source,
        "last_scanned_at": company.last_scanned_at,
        "created_at": company.created_at,
    }


@app.on_event("startup")
def bootstrap_crawler_service() -> None:
    ensure_local_directories()
    init_db(settings.database_url)


@app.get("/health")
def health():
    return service_health(settings.service_name, settings.service_version)


@app.get("/", response_class=HTMLResponse)
def admin_dashboard():
    return ADMIN_HTML


@app.get("/config")
def crawler_config(_: None = Depends(require_admin)):
    return {
        "default_keywords": split_csv(settings.default_keywords),
        "default_locations": split_csv(settings.default_locations),
        "default_platforms": split_csv(settings.default_platforms),
        "provider": settings.provider,
        "official_apply_only": settings.official_apply_only,
    }


@app.get("/jobs")
def crawler_jobs(limit: int = 50, _: None = Depends(require_admin)):
    return {"jobs": [serialize_job(job) for job in list_jobs(settings.database_url, limit=limit)]}


@app.get("/companies")
def crawler_companies(limit: int = 100, _: None = Depends(require_admin)):
    return {
        "companies": [
            serialize_company(company)
            for company in list_companies(settings.database_url, limit=limit)
        ]
    }


@app.post("/companies/discover")
def discover_company(
    payload: CrawlCompanyRequest,
    _: None = Depends(require_admin),
):
    company = discover_company_source(payload.company_name)
    company_id = save_company(company, settings.database_url)
    saved = Company(
        id=company_id,
        name=company.name,
        website_url=company.website_url,
        careers_url=company.careers_url,
        ats_provider=company.ats_provider,
        source=company.source,
        last_scanned_at=company.last_scanned_at,
        created_at=company.created_at,
    )
    return {"company": serialize_company(saved)}


@app.get("/jobs/{job_id}")
def crawler_job(job_id: int, _: None = Depends(require_admin)):
    job = get_job(job_id, settings.database_url)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return serialize_job(job)


@app.patch("/jobs/{job_id}")
def update_crawler_job(
    job_id: int,
    payload: JobUpdateRequest,
    _: None = Depends(require_admin),
):
    current = get_job(job_id, settings.database_url)
    if current is None:
        raise HTTPException(status_code=404, detail="Job not found")
    updated = update_job(
        job_id,
        Job(
            title=payload.title,
            company=payload.company,
            location=payload.location,
            employment_type=payload.employment_type,
            salary=payload.salary,
            platform=payload.platform,
            job_url=payload.job_url,
            official_apply_url=payload.official_apply_url,
            description=payload.description,
            status=payload.status,
            match_score=payload.match_score,
        ),
        settings.database_url,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Job not found")
    job = get_job(job_id, settings.database_url)
    return serialize_job(job) if job else {"updated": True}


@app.delete("/jobs/{job_id}")
def delete_crawler_job(job_id: int, _: None = Depends(require_admin)):
    return {"deleted": delete_jobs([job_id], settings.database_url)}


@app.delete("/jobs")
def delete_crawler_jobs(payload: DeleteJobsRequest, _: None = Depends(require_admin)):
    return {"deleted": delete_jobs(payload.job_ids, settings.database_url)}


def crawl_once(payload: CrawlOnceRequest) -> CrawlResult:
    query = build_search_query(payload.keywords, payload.location, payload.platform)
    saved_count = 0

    def save_found_job(job: Job) -> None:
        nonlocal saved_count
        save_job(job, settings.database_url)
        saved_count += 1

    if should_use_jobspy(query.platform):
        jobs = search_jobs_with_jobspy(
            query,
            jobspy_options(),
            official_apply_only=False,
        )
        resolved_jobs = [
            resolve_official_apply_job(
                job,
                keywords=query.keywords,
                location=query.location,
                allow_search_discovery=(
                    settings.allow_search_discovery or settings.official_apply_only
                ),
            )
            for job in jobs
        ]
        if settings.official_apply_only:
            resolved_jobs = [job for job in resolved_jobs if job.official_apply_url]
        for job in resolved_jobs:
            save_found_job(job)
        return CrawlResult(
            keywords=query.keywords,
            location=query.location,
            platform=query.platform,
            message=(
                f"Found {len(resolved_jobs)} jobs from JobSpy"
                f"{' with official apply links' if settings.official_apply_only else ''}."
            ),
            found_count=len(resolved_jobs),
            saved_count=saved_count,
            blocked=False,
        )

    outcome = search_jobs(
        query,
        on_job=save_found_job,
        allow_manual_verification=False,
        official_apply_only=settings.official_apply_only,
    )
    return CrawlResult(
        keywords=query.keywords,
        location=query.location,
        platform=query.platform,
        message=outcome.message,
        found_count=len(outcome.jobs),
        saved_count=saved_count,
        blocked=outcome.blocked,
    )


def should_use_jobspy(platform: str) -> bool:
    provider = settings.provider.lower().strip()
    if provider == "jobspy":
        return is_jobspy_platform(platform)
    if provider == "playwright":
        return False
    return is_jobspy_platform(platform)


def jobspy_options() -> JobSpySearchOptions:
    return JobSpySearchOptions(
        results_wanted=settings.jobspy_results_wanted,
        hours_old=settings.jobspy_hours_old,
        country_indeed=settings.jobspy_country_indeed,
        linkedin_fetch_description=settings.jobspy_linkedin_fetch_description,
        proxies=tuple(split_csv(settings.jobspy_proxies)),
        user_agent=settings.user_agent,
    )


def crawl_company(payload: CrawlCompanyRequest) -> CompanyResult:
    company = Company(
        name=payload.company_name,
        website_url=payload.website_url,
        careers_url=payload.careers_url,
        ats_provider=payload.ats_provider,
        source="manual" if payload.careers_url else "discover",
    )
    scan_result = scan_company_careers(
        company,
        keywords=payload.keywords,
        location=payload.location,
    )
    company_id = save_company(scan_result.company, settings.database_url)
    saved_count = 0
    for job in scan_result.jobs:
        save_job(job, settings.database_url)
        saved_count += 1
    update_company_scan_time(scan_result.company.name, settings.database_url)

    saved_company = Company(
        id=company_id,
        name=scan_result.company.name,
        website_url=scan_result.company.website_url,
        careers_url=scan_result.company.careers_url,
        ats_provider=scan_result.company.ats_provider,
        source=scan_result.company.source,
    )
    return CompanyResult(
        company=serialize_company(saved_company),
        message=scan_result.message,
        found_count=len(scan_result.jobs),
        saved_count=saved_count,
    )


@app.post("/crawl/once", response_model=CrawlResult)
def crawl_once_endpoint(
    payload: CrawlOnceRequest,
    _: None = Depends(require_admin),
):
    return crawl_once(payload)


@app.post("/crawl/company", response_model=CompanyResult)
def crawl_company_endpoint(
    payload: CrawlCompanyRequest,
    _: None = Depends(require_admin),
):
    return crawl_company(payload)


@app.post("/crawl/run", response_model=list[CrawlResult])
def crawl_run(
    payload: CrawlRunRequest,
    _: None = Depends(require_admin),
):
    keywords = payload.keywords or split_csv(settings.default_keywords)
    locations = payload.locations or split_csv(settings.default_locations)
    platforms = payload.platforms or split_csv(settings.default_platforms)

    results: list[CrawlResult] = []
    for platform in platforms:
        for keyword in keywords:
            for location in locations:
                results.append(
                    crawl_once(
                        CrawlOnceRequest(
                            keywords=keyword,
                            location=location,
                            platform=platform,
                        )
                    )
                )
    return results
