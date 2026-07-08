from pathlib import Path

from jobseeking_agent.database.db import delete_jobs, init_db, list_jobs, save_job
from jobseeking_agent.database.models import Job
from jobseeking_agent.db import (
    has_search_refresh,
    mark_search_refresh,
    search_saved_jobs,
    update_job,
)


def test_save_and_list_jobs(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'agent.db'}"

    init_db(database_url)
    job_id = save_job(
        Job(
            title="Backend Engineer",
            company="Example Company",
            location="Remote",
            employment_type="Full-time",
            salary="$120k - $150k",
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
    assert jobs[0].employment_type == "Full-time"
    assert jobs[0].salary == "$120k - $150k"


def test_save_and_list_jobs_with_official_apply_url(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'agent.db'}"

    init_db(database_url)
    save_job(
        Job(
            title="Backend Engineer",
            company="Example Company",
            platform="seek",
            job_url="https://www.seek.com.au/job/123",
            official_apply_url="https://jobs.lever.co/example/backend-engineer",
        ),
        database_url,
    )

    jobs = list_jobs(database_url)

    assert jobs[0].official_apply_url == "https://jobs.lever.co/example/backend-engineer"


def test_save_job_preserves_existing_official_apply_url_when_new_value_is_empty(
    tmp_path: Path,
) -> None:
    database_url = f"sqlite:///{tmp_path / 'agent.db'}"

    init_db(database_url)
    save_job(
        Job(
            title="Backend Engineer",
            company="Example Company",
            platform="seek",
            job_url="https://www.seek.com.au/job/123",
            official_apply_url="https://jobs.lever.co/example/backend-engineer",
        ),
        database_url,
    )
    save_job(
        Job(
            title="Backend Engineer",
            company="Example Company",
            platform="seek",
            job_url="https://www.seek.com.au/job/123",
            official_apply_url="",
        ),
        database_url,
    )

    jobs = list_jobs(database_url)

    assert jobs[0].official_apply_url == "https://jobs.lever.co/example/backend-engineer"


def test_list_jobs_can_filter_to_official_apply_urls(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'agent.db'}"

    init_db(database_url)
    save_job(Job(title="No Official Link", company="Example"), database_url)
    save_job(
        Job(
            title="Official Link",
            company="Example",
            official_apply_url="https://boards.greenhouse.io/example/jobs/123",
        ),
        database_url,
    )

    jobs = list_jobs(database_url, official_only=True)

    assert len(jobs) == 1
    assert jobs[0].title == "Official Link"


def test_delete_jobs(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'agent.db'}"

    init_db(database_url)
    first_id = save_job(Job(title="One", company="Example"), database_url)
    second_id = save_job(Job(title="Two", company="Example"), database_url)

    assert delete_jobs([first_id], database_url) == 1

    jobs = list_jobs(database_url)
    assert [job.id for job in jobs] == [second_id]


def test_update_job(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'agent.db'}"

    init_db(database_url)
    job_id = save_job(Job(title="Old", company="Example"), database_url)

    assert update_job(
        job_id,
        Job(
            title="New",
            company="Updated Co",
            location="Sydney",
            employment_type="Contract",
            salary="$100k",
            platform="seek",
            job_url="https://au.seek.com/job/123?tracking=1",
            official_apply_url="https://jobs.lever.co/example/new",
            description="Updated",
            status="reviewing",
            match_score=0.8,
        ),
        database_url,
    )

    jobs = list_jobs(database_url)
    assert jobs[0].title == "New"
    assert jobs[0].company == "Updated Co"
    assert jobs[0].job_url == "https://au.seek.com/job/123"
    assert jobs[0].official_apply_url == "https://jobs.lever.co/example/new"
    assert jobs[0].status == "reviewing"


def test_delete_all_jobs_resets_id_sequence(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'agent.db'}"

    init_db(database_url)
    first_id = save_job(Job(title="One", company="Example"), database_url)
    second_id = save_job(Job(title="Two", company="Example"), database_url)

    assert delete_jobs([first_id, second_id], database_url) == 2
    new_id = save_job(Job(title="Three", company="Example"), database_url)

    assert new_id == 1


def test_save_job_deduplicates_canonical_source_url(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'agent.db'}"

    init_db(database_url)
    first_id = save_job(
        Job(
            title="Backend Engineer",
            company="Example",
            platform="seek",
            job_url="https://au.seek.com/job/123?origin=cardTitle#sol=a",
        ),
        database_url,
    )
    second_id = save_job(
        Job(
            title="Backend Engineer Updated",
            company="Example",
            platform="seek",
            job_url="https://au.seek.com/job/123?origin=jobCard#sol=b",
        ),
        database_url,
    )

    jobs = list_jobs(database_url)
    assert first_id == second_id
    assert len(jobs) == 1
    assert jobs[0].title == "Backend Engineer Updated"
    assert jobs[0].job_url == "https://au.seek.com/job/123"


def test_search_saved_jobs_filters_database_results(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'agent.db'}"

    init_db(database_url)
    save_job(
        Job(
            title="Software Engineer",
            company="Example",
            location="Sydney NSW",
            platform="seek",
        ),
        database_url,
    )
    save_job(
        Job(
            title="Product Manager",
            company="Example",
            location="Sydney NSW",
            platform="seek",
        ),
        database_url,
    )
    save_job(
        Job(
            title="Software Engineer",
            company="Example",
            location="Melbourne VIC",
            platform="linkedin",
        ),
        database_url,
    )

    jobs = search_saved_jobs("software engineer", "Sydney", "seek", database_url)

    assert len(jobs) == 1
    assert jobs[0].title == "Software Engineer"
    assert jobs[0].location == "Sydney NSW"
    assert jobs[0].platform == "seek"


def test_search_saved_jobs_can_filter_to_official_apply_urls(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'agent.db'}"

    init_db(database_url)
    save_job(
        Job(
            title="Software Engineer",
            company="Example",
            location="Sydney NSW",
            platform="seek",
        ),
        database_url,
    )
    save_job(
        Job(
            title="Software Engineer",
            company="Example",
            location="Sydney NSW",
            platform="seek",
            official_apply_url="https://jobs.lever.co/example/software-engineer",
        ),
        database_url,
    )

    jobs = search_saved_jobs(
        "software engineer",
        "Sydney",
        "seek",
        database_url,
        official_only=True,
    )

    assert len(jobs) == 1
    assert jobs[0].official_apply_url == "https://jobs.lever.co/example/software-engineer"


def test_search_refresh_tracking_is_once_per_day(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'agent.db'}"

    init_db(database_url)

    assert not has_search_refresh("Software Engineer", "Sydney", "seek", "2026-07-07", database_url)
    assert mark_search_refresh("Software Engineer", "Sydney", "seek", "2026-07-07", database_url)
    assert has_search_refresh("software   engineer", "sydney", "seek", "2026-07-07", database_url)
    assert not mark_search_refresh(
        "software engineer", "Sydney", "seek", "2026-07-07", database_url
    )
    assert mark_search_refresh("software engineer", "Sydney", "seek", "2026-07-08", database_url)
