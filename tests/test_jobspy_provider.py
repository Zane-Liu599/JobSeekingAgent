from jobseeking_agent.db.models import Job
from jobseeking_agent.search.ats_resolver import best_matching_company_job, merge_job
from jobseeking_agent.search.description_formatter import clean_job_description
from jobseeking_agent.search.jobspy_provider import normalize_jobspy_records


def test_normalize_jobspy_records_maps_core_fields() -> None:
    jobs = normalize_jobspy_records(
        [
            {
                "site": "linkedin",
                "title": "Software Engineer",
                "company": "Example Co",
                "city": "Sydney",
                "state": "NSW",
                "country": "Australia",
                "job_type": "fulltime",
                "interval": "yearly",
                "currency": "AUD",
                "min_amount": 100000,
                "max_amount": 130000,
                "job_url": "https://www.linkedin.com/jobs/view/123",
                "direct_url": "https://jobs.lever.co/example/software-engineer",
                "description": "About this job",
            }
        ],
        fallback_platform="linkedin",
        official_apply_only=True,
    )

    assert len(jobs) == 1
    assert jobs[0].company == "Example Co"
    assert jobs[0].location == "Sydney, NSW, Australia"
    assert jobs[0].employment_type == "fulltime"
    assert jobs[0].salary == "AUD 100000 - 130000 / yearly"
    assert jobs[0].official_apply_url == "https://jobs.lever.co/example/software-engineer"
    assert jobs[0].description == "### About this job"


def test_normalize_jobspy_records_reads_job_url_direct() -> None:
    jobs = normalize_jobspy_records(
        [
            {
                "site": "linkedin",
                "title": "Software Engineer",
                "company": "Example Co",
                "job_url": "https://www.linkedin.com/jobs/view/123",
                "job_url_direct": "https://boards.greenhouse.io/example/jobs/123",
            }
        ],
        fallback_platform="linkedin",
        official_apply_only=True,
    )

    assert len(jobs) == 1
    assert jobs[0].official_apply_url == "https://boards.greenhouse.io/example/jobs/123"


def test_clean_job_description_formats_noisy_raw_text() -> None:
    description = clean_job_description(
        """
        <div>Responsibilities:</div>
        <div>• Build APIs</div>
        <div>• Improve reliability</div>
        <div>Show more</div>
        <div>Requirements:</div>
        <div>Python experience</div>
        """
    )

    assert "### Responsibilities" in description
    assert "- Build APIs" in description
    assert "Show more" not in description
    assert "### Requirements" in description


def test_normalize_jobspy_records_can_skip_jobs_without_official_apply_url() -> None:
    jobs = normalize_jobspy_records(
        [
            {
                "site": "indeed",
                "title": "Software Engineer",
                "company": "Example Co",
                "job_url": "https://www.indeed.com/viewjob?jk=123",
            }
        ],
        fallback_platform="indeed",
        official_apply_only=True,
    )

    assert jobs == []


def test_normalize_jobspy_records_keeps_jobs_without_official_apply_url_for_enrichment() -> None:
    jobs = normalize_jobspy_records(
        [
            {
                "site": "indeed",
                "title": "Software Engineer",
                "company": "Example Co",
                "job_url": "https://www.indeed.com/viewjob?jk=123",
            }
        ],
        fallback_platform="indeed",
        official_apply_only=False,
    )

    assert len(jobs) == 1
    assert jobs[0].official_apply_url == ""


def test_best_matching_company_job_prefers_title_overlap() -> None:
    source_job = Job(title="Senior Backend Engineer", company="Example Co")
    company_job = best_matching_company_job(
        source_job,
        [
            Job(title="Marketing Manager", company="Example Co"),
            Job(
                title="Backend Software Engineer",
                company="Example Co",
                official_apply_url="https://jobs.lever.co/example/backend",
            ),
        ],
    )

    assert company_job is not None
    assert company_job.official_apply_url == "https://jobs.lever.co/example/backend"


def test_merge_job_preserves_board_fields_and_adds_official_url() -> None:
    merged = merge_job(
        Job(
            title="Software Engineer",
            company="Example Co",
            location="Sydney",
            platform="linkedin",
            job_url="https://www.linkedin.com/jobs/view/123",
            description="LinkedIn description",
        ),
        Job(
            title="Software Engineer",
            company="Example Co",
            location="Remote",
            official_apply_url="https://boards.greenhouse.io/example/jobs/123",
            description="Official description",
        ),
    )

    assert merged.location == "Sydney"
    assert merged.official_apply_url == "https://boards.greenhouse.io/example/jobs/123"
    assert merged.description == "LinkedIn description"
