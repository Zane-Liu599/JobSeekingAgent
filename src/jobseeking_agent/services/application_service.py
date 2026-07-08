from jobseeking_agent.application.autofill import build_application_plan
from jobseeking_agent.db import Job


def application_review_plan(job: Job) -> list[str]:
    return build_application_plan(job)
