from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from platform_common import service_health
from pydantic import BaseModel, Field

from ai_service.settings import AISettings
from jobseeking_agent.ai.cover_letter_generator import generate_cover_letter_result
from jobseeking_agent.application.autofill import build_application_plan
from jobseeking_agent.db import (
    Job,
    delete_jobs,
    get_job,
    init_db,
    job_status_counts,
    list_jobs,
    save_job,
    search_saved_jobs,
    update_job_status,
)
from jobseeking_agent.tracker.status_manager import VALID_STATUSES
from jobseeking_agent.utils.exporter import export_jobs_to_xlsx
from jobseeking_agent.utils.file_manager import ensure_local_directories

settings = AISettings()

app = FastAPI(
    title="JobSeekingAgent AI Service",
    version=settings.service_version,
)


class ChatRequest(BaseModel):
    message: str


class JobPayload(BaseModel):
    title: str = Field(min_length=1)
    company: str = Field(min_length=1)
    location: str = ""
    employment_type: str = ""
    salary: str = ""
    platform: str = "manual"
    job_url: str = ""
    description: str = ""
    status: str = "found"
    match_score: float | None = None


class SearchRequest(BaseModel):
    keywords: str = Field(min_length=1)
    location: str = ""
    platform: str = ""


class SearchResponse(BaseModel):
    message: str
    saved_count: int
    blocked: bool
    refreshed: bool
    refresh_message: str
    jobs: list[dict[str, str | int | float | None]]


class StatusUpdateRequest(BaseModel):
    job_ids: list[int]
    status: str


class DeleteJobsRequest(BaseModel):
    job_ids: list[int]


class CoverLetterRequest(BaseModel):
    job_id: int


class CoverLetterResponse(BaseModel):
    job_id: int
    path: str
    text: str
    provider: str
    model: str
    used_resume: bool
    used_template: bool
    error: str = ""


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


@app.on_event("startup")
def bootstrap_legacy_job_automation() -> None:
    ensure_local_directories()
    init_db()


@app.get("/health")
def health():
    return service_health(settings.service_name, settings.service_version)


@app.post("/ai/chat")
def chat_placeholder(request: ChatRequest):
    return {
        "reply": (
            "AI chat pipeline placeholder. Gemini, LangGraph, LangChain, "
            "and pgvector wire in here."
        ),
        "input": request.message,
        "model": settings.gemini_model,
    }


@app.get("/jobs")
def jobs(limit: int = 200):
    return {"jobs": [serialize_job(job) for job in list_jobs(limit=limit, official_only=True)]}


@app.get("/jobs/stats")
def jobs_stats():
    return {"counts": job_status_counts()}


@app.get("/jobs/export")
def export_jobs():
    path = export_jobs_to_xlsx(
        list_jobs(limit=1000, official_only=True),
        Path("data/exports/jobs.xlsx"),
    )
    return FileResponse(
        path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="jobs.xlsx",
    )


@app.get("/jobs/{job_id}")
def job_detail(job_id: int):
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return serialize_job(job)


@app.post("/jobs")
def create_job(payload: JobPayload):
    job_id = save_job(
        Job(
            title=payload.title,
            company=payload.company,
            location=payload.location,
            employment_type=payload.employment_type,
            salary=payload.salary,
            platform=payload.platform,
            job_url=payload.job_url,
            official_apply_url="",
            description=payload.description,
            status=payload.status,
            match_score=payload.match_score,
        )
    )
    job = get_job(job_id)
    return serialize_job(job) if job else {"id": job_id}


@app.post("/jobs/search", response_model=SearchResponse)
def search_job_board(payload: SearchRequest):
    jobs = search_saved_jobs(
        payload.keywords,
        location=payload.location,
        platform=payload.platform,
        limit=200,
        official_only=True,
    )

    message = f"Found {len(jobs)} saved role(s) with official apply links for {payload.keywords}."
    return SearchResponse(
        message=message,
        saved_count=0,
        blocked=False,
        refreshed=False,
        refresh_message="Using saved jobs from the database.",
        jobs=[serialize_job(job) for job in jobs],
    )


@app.patch("/jobs/status")
def update_jobs_status(payload: StatusUpdateRequest):
    if payload.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid status")
    updated = 0
    for job_id in payload.job_ids:
        if update_job_status(job_id, payload.status):
            updated += 1
    return {"updated": updated}


@app.delete("/jobs")
def remove_jobs(payload: DeleteJobsRequest):
    return {"deleted": delete_jobs(payload.job_ids)}


@app.post("/cover-letters/generate", response_model=CoverLetterResponse)
def generate_cover_letter(payload: CoverLetterRequest):
    job = get_job(payload.job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    path, result = generate_cover_letter_result(job)
    return CoverLetterResponse(
        job_id=payload.job_id,
        path=str(path),
        text=path.read_text(encoding="utf-8"),
        provider=result.provider,
        model=result.model,
        used_resume=result.used_resume,
        used_template=result.used_template,
        error=result.error,
    )


@app.get("/applications/plan/{job_id}")
def application_plan(job_id: int):
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"steps": build_application_plan(job)}
