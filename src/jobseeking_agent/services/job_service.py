from jobseeking_agent.db import (
    Job,
    delete_jobs,
    get_job,
    init_db,
    job_status_counts,
    list_jobs,
    save_job,
    update_job_status,
)


def job_options(limit: int = 200) -> dict[str, int]:
    jobs = list_jobs(limit=limit)
    return {
        f"#{job.id} {job.title} - {job.company}": int(job.id)
        for job in jobs
        if job.id is not None
    }


def jobs_table_data(limit: int = 200) -> list[dict[str, str | int | float | None]]:
    return [
        {
            "ID": job.id,
            "Title": job.title,
            "Company": job.company,
            "Location": job.location,
            "Type": job.employment_type,
            "Salary": job.salary,
            "Platform": job.platform,
            "Official Apply URL": job.official_apply_url,
            "Status": job.status,
            "Score": job.match_score,
        }
        for job in list_jobs(limit=limit)
    ]


def save_manual_job(
    *,
    title: str,
    company: str,
    location: str = "",
    employment_type: str = "",
    salary: str = "",
    platform: str = "manual",
    url: str = "",
    official_apply_url: str = "",
    description: str = "",
) -> int:
    return save_job(
        Job(
            title=title,
            company=company,
            location=location,
            employment_type=employment_type,
            salary=salary,
            platform=platform,
            job_url=url,
            official_apply_url=official_apply_url,
            description=description,
        )
    )


__all__ = [
    "Job",
    "delete_jobs",
    "get_job",
    "init_db",
    "job_options",
    "job_status_counts",
    "jobs_table_data",
    "list_jobs",
    "save_job",
    "save_manual_job",
    "update_job_status",
]
