from jobseeking_agent.database.models import Job


def summarize_resume_match(job: Job, skills: list[str]) -> list[str]:
    description = job.description.lower()
    return [skill for skill in skills if skill.lower() in description]
