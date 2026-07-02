from pathlib import Path

from jobseeking_agent.database.db import init_db, list_jobs, save_job
from jobseeking_agent.database.models import Job


def test_save_and_list_jobs(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'agent.db'}"

    init_db(database_url)
    job_id = save_job(
        Job(
            title="Backend Engineer",
            company="Example Company",
            location="Remote",
            platform="manual",
            job_url="https://example.com/job",
        ),
        database_url,
    )

    jobs = list_jobs(database_url)

    assert job_id > 0
    assert len(jobs) == 1
    assert jobs[0].title == "Backend Engineer"
    assert jobs[0].company == "Example Company"
