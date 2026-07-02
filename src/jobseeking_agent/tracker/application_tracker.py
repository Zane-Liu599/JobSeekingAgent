from jobseeking_agent.database.models import Application


def create_draft_application(job_id: int, resume_path: str, cover_letter_path: str) -> Application:
    return Application(
        job_id=job_id,
        resume_path=resume_path,
        cover_letter_path=cover_letter_path,
        status="draft",
    )
