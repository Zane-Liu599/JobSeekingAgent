from pathlib import Path

from jobseeking_agent.ai.gemini_cover_letter import (
    CoverLetterResult,
    generate_cover_letter_with_gemini,
)
from jobseeking_agent.database.models import Job


def cover_letter_path(job: Job, output_dir: str = "data/cover_letters") -> Path:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    job_id = job.id or "draft"
    safe_company = "".join(
        ch for ch in job.company if ch.isalnum() or ch in (" ", "-", "_")
    ).strip()
    filename = f"{job_id}-{safe_company or 'company'}-cover-letter.md".replace(" ", "-")
    return Path(output_dir) / filename


def generate_cover_letter(job: Job, output_dir: str = "data/cover_letters") -> Path:
    result = generate_cover_letter_with_gemini(job)
    path = cover_letter_path(job, output_dir)
    path.write_text(result.text, encoding="utf-8")
    return path


def generate_cover_letter_result(
    job: Job,
    output_dir: str = "data/cover_letters",
) -> tuple[Path, CoverLetterResult]:
    result = generate_cover_letter_with_gemini(job)
    path = cover_letter_path(job, output_dir)
    path.write_text(result.text, encoding="utf-8")
    return path, result
