from jobseeking_agent.database.models import Job


def build_application_plan(job: Job) -> list[str]:
    return [
        f"Open job page: {job.job_url or 'missing URL'}",
        "Review job description and requirements",
        "Upload resume",
        "Upload or paste cover letter",
        "Review all answers manually",
        "Submit only after user confirmation",
    ]
