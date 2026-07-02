from jobseeking_agent.database.models import Job


def score_job_fit(job: Job, target_titles: list[str], target_locations: list[str]) -> float:
    score = 0.0
    title = job.title.lower()
    location = job.location.lower()

    if any(target.lower() in title for target in target_titles):
        score += 60.0
    if any(target.lower() in location for target in target_locations):
        score += 30.0
    if job.description:
        score += 10.0

    return min(score, 100.0)
