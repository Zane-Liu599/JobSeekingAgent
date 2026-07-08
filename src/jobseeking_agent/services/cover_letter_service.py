from pathlib import Path

from jobseeking_agent.ai.cover_letter_generator import generate_cover_letter
from jobseeking_agent.db import Job


def generate_cover_letter_for_job(job: Job) -> Path:
    return generate_cover_letter(job)
