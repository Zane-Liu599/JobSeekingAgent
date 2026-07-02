from pathlib import Path

from jobseeking_agent.config import get_settings
from jobseeking_agent.database.models import Job
from jobseeking_agent.profile import load_profile


def generate_cover_letter(job: Job, output_dir: str = "data/cover_letters") -> Path:
    settings = get_settings()
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    job_id = job.id or "draft"
    safe_company = "".join(
        ch for ch in job.company if ch.isalnum() or ch in (" ", "-", "_")
    ).strip()
    filename = f"{job_id}-{safe_company or 'company'}-cover-letter.md".replace(" ", "-")
    path = Path(output_dir) / filename

    profile = load_profile()
    candidate_name = profile.name or settings.candidate_name or "Candidate"
    body = f"""# Cover Letter Draft

Dear Hiring Team,

I am excited to apply for the {job.title} role at {job.company}. My background aligns
with the responsibilities described in this position, and I would welcome the
opportunity to contribute to your team.

This draft was generated locally as a safe MVP placeholder. Review and customize it
before submitting.

Best regards,

{candidate_name}
"""
    path.write_text(body, encoding="utf-8")
    return path
