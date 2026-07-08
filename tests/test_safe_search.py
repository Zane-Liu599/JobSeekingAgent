from playwright.sync_api import sync_playwright

from jobseeking_agent.search.keyword_search import build_search_query
from jobseeking_agent.search.safe_search import (
    browser_storage_state_path,
    canonical_job_url,
    extract_detail_fields_from_page,
    extract_jobs_from_links,
    extract_jobs_from_page,
    extract_jobs_from_records,
    extract_search_result_urls,
    infer_employment_type,
    infer_salary,
    known_company_careers_url,
    looks_blocked,
    normalize_official_apply_url,
    platform_search_url,
    record_needs_detail_enrichment,
    select_official_apply_candidate,
    try_capture_clicked_apply_url,
    unwrap_search_result_url,
)
from jobseeking_agent.search.state import advance_search_page, next_search_page


def test_platform_search_url_for_seek() -> None:
    query = build_search_query("backend engineer", "Sydney", "seek")

    assert platform_search_url(query) == "https://www.seek.com.au/backend+engineer-jobs/in-Sydney"


def test_platform_search_url_uses_platform_pagination() -> None:
    seek = build_search_query("backend engineer", "Sydney", "seek")
    linkedin = build_search_query("backend engineer", "Sydney", "linkedin")
    indeed = build_search_query("backend engineer", "Sydney", "indeed")

    assert platform_search_url(seek, page_number=2).endswith("/in-Sydney?page=2")
    assert platform_search_url(linkedin, page_number=2).endswith("&start=25")
    assert platform_search_url(indeed, page_number=3).endswith("&start=20")


def test_search_state_advances_per_query(tmp_path) -> None:
    query = build_search_query("backend engineer", "Sydney", "seek")
    path = tmp_path / "search_state.json"

    assert next_search_page(query, path) == 1
    assert advance_search_page(query, path) == 2
    assert next_search_page(query, path) == 2


def test_browser_storage_state_path_is_platform_specific(tmp_path) -> None:
    path = browser_storage_state_path("LinkedIn", str(tmp_path))

    assert path == tmp_path / "linkedin.json"


def test_looks_blocked_detects_human_verification() -> None:
    assert looks_blocked("Please verify you are human before continuing")


def test_looks_blocked_does_not_flag_normal_sign_in_link() -> None:
    assert not looks_blocked("Search jobs Sign in Profile Saved jobs")


def test_extract_jobs_from_links_deduplicates_and_limits() -> None:
    query = build_search_query("backend", "Remote", "seek")
    jobs = extract_jobs_from_links(
        [
            ("Backend Engineer", "https://www.seek.com.au/job/123"),
            ("Backend Engineer Duplicate", "https://www.seek.com.au/job/123"),
            ("Not a job", "https://www.seek.com.au/advice"),
            ("Platform Engineer", "https://www.seek.com.au/job/456"),
        ],
        query,
        limit=1,
    )

    assert len(jobs) == 1
    assert jobs[0].title == "Backend Engineer"


def test_canonical_job_url_removes_tracking_parameters() -> None:
    url = "https://au.seek.com/job/93076444?origin=cardTitle#sol=abc"

    assert canonical_job_url("seek", url) == "https://au.seek.com/job/93076444"


def test_canonical_job_url_supports_linkedin_and_indeed() -> None:
    assert (
        canonical_job_url("linkedin", "https://www.linkedin.com/jobs/view/123456/?trk=public_jobs")
        == "https://www.linkedin.com/jobs/view/123456"
    )
    assert (
        canonical_job_url("indeed", "https://www.indeed.com/rc/clk?jk=abc123&from=vj")
        == "https://www.indeed.com/viewjob?jk=abc123"
    )


def test_extract_jobs_from_links_deduplicates_tracking_urls() -> None:
    query = build_search_query("backend", "Remote", "seek")

    jobs = extract_jobs_from_links(
        [
            ("Backend Engineer", "https://au.seek.com/job/123?origin=cardTitle#sol=a"),
            ("Backend Engineer Duplicate", "https://au.seek.com/job/123?origin=jobCard#sol=b"),
        ],
        query,
        limit=10,
    )

    assert len(jobs) == 1
    assert jobs[0].job_url == "https://au.seek.com/job/123"


def test_extract_jobs_from_links_deduplicates_linkedin_tracking_urls() -> None:
    query = build_search_query("backend", "Remote", "linkedin")

    jobs = extract_jobs_from_links(
        [
            ("Backend Engineer", "https://www.linkedin.com/jobs/view/123456/?trk=public_jobs"),
            ("Backend Engineer Duplicate", "https://www.linkedin.com/jobs/view/123456/?refId=x"),
        ],
        query,
        limit=10,
    )

    assert len(jobs) == 1
    assert jobs[0].job_url == "https://www.linkedin.com/jobs/view/123456"


def test_extract_jobs_from_links_deduplicates_indeed_tracking_urls() -> None:
    query = build_search_query("backend", "Remote", "indeed")

    jobs = extract_jobs_from_links(
        [
            ("Backend Engineer", "https://www.indeed.com/rc/clk?jk=abc123&from=vj"),
            ("Backend Engineer Duplicate", "https://www.indeed.com/viewjob?jk=abc123&tk=1"),
        ],
        query,
        limit=10,
    )

    assert len(jobs) == 1
    assert jobs[0].job_url == "https://www.indeed.com/viewjob?jk=abc123"


def test_extract_jobs_from_links_calls_callback_for_each_job() -> None:
    query = build_search_query("backend", "Remote", "seek")
    found = []

    jobs = extract_jobs_from_links(
        [
            ("Backend Engineer", "https://www.seek.com.au/job/123"),
            ("Platform Engineer", "https://www.seek.com.au/job/456"),
        ],
        query,
        limit=10,
        on_job=found.append,
    )

    assert len(jobs) == 2
    assert [job.job_url for job in found] == [
        "https://www.seek.com.au/job/123",
        "https://www.seek.com.au/job/456",
    ]


def test_extract_jobs_from_records_includes_company_and_company_search() -> None:
    query = build_search_query("backend", "Remote", "seek")

    jobs = extract_jobs_from_records(
        [
            {
                "title": "Backend Engineer",
                "href": "https://www.seek.com.au/job/123",
                "cardText": (
                    "Backend Engineer\nExample Company\nSydney NSW\n"
                    "Full time\n$120k - $150k\nListed two days ago"
                ),
            }
        ],
        query,
        limit=10,
    )

    assert jobs[0].company == "Example Company"
    assert jobs[0].employment_type == "Full-time"
    assert jobs[0].salary == "$120k - $150k"
    assert "Company site search:" in jobs[0].description
    assert "Example+Company" in jobs[0].description
    assert "Full-time" in jobs[0].description


def test_extract_jobs_from_records_includes_official_apply_url() -> None:
    query = build_search_query("backend", "Remote", "seek")

    jobs = extract_jobs_from_records(
        [
            {
                "title": "Backend Engineer",
                "href": "https://www.seek.com.au/job/123",
                "company": "Example Company",
                "officialApplyUrl": "https://jobs.lever.co/example/backend-engineer",
            }
        ],
        query,
        limit=10,
    )

    assert jobs[0].official_apply_url == "https://jobs.lever.co/example/backend-engineer"


def test_normalize_linkedin_external_apply_url_unwraps_company_url() -> None:
    apply_url = normalize_official_apply_url(
        (
            "https://www.linkedin.com/jobs/view/externalApply/123456?"
            "url=https%3A%2F%2Fjobs.lever.co%2Fexample%2Fbackend-engineer"
        ),
        "https://www.linkedin.com/jobs/view/123456",
        "linkedin",
    )

    assert apply_url == "https://jobs.lever.co/example/backend-engineer"


def test_extract_detail_fields_reads_linkedin_apply_anchor() -> None:
    html = """
    <main>
      <a
        data-tracking-control-name="public_jobs_apply-link-offsite_sign-up-modal"
        href="https://www.linkedin.com/jobs/view/externalApply/123456?url=https%3A%2F%2Fboards.greenhouse.io%2Fexample%2Fjobs%2F123"
      >
        Apply
      </a>
    </main>
    """

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_content(html)
        detail = extract_detail_fields_from_page(page)
        browser.close()

    apply_url = normalize_official_apply_url(
        str(detail.get("applyUrl", "")),
        "https://www.linkedin.com/jobs/view/123456",
        "linkedin",
    )

    assert apply_url == "https://boards.greenhouse.io/example/jobs/123"


def test_extract_detail_fields_ignores_quick_apply_anchor() -> None:
    html = """
    <main>
      <a href="https://jobs.lever.co/example/backend-engineer">Quick Apply</a>
      <a href="https://jobs.lever.co/example/frontend-engineer">Apply on company site</a>
    </main>
    """

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_content(html)
        detail = extract_detail_fields_from_page(page)
        browser.close()

    assert detail["applyUrl"] == "https://jobs.lever.co/example/frontend-engineer"


def test_extract_search_result_urls_unwraps_duckduckgo_links() -> None:
    html = """
    <a href="/l/?uddg=https%3A%2F%2Famazon.jobs%2Fen%2Fjobs%2F123%2Fengineer">AWS</a>
    <a href="https://www.linkedin.com/jobs/view/123">LinkedIn</a>
    """

    urls = extract_search_result_urls(html)

    assert urls[0] == "https://amazon.jobs/en/jobs/123/engineer"
    assert urls[1] == "https://www.linkedin.com/jobs/view/123"


def test_unwrap_search_result_url_decodes_bing_links() -> None:
    url = "https://www.bing.com/ck/a?u=a1aHR0cHM6Ly9hbWF6b24uam9icy9lbi9qb2JzLzEyMw"

    assert unwrap_search_result_url(url) == "https://amazon.jobs/en/jobs/123"


def test_select_official_apply_candidate_prefers_company_or_ats_url() -> None:
    candidate = select_official_apply_candidate(
        [
            "https://www.linkedin.com/jobs/view/123",
            "https://amazon.jobs/en/jobs/92875670/system-development-engineer",
        ],
        "System Development Engineer",
        "Amazon Web Services",
        "seek",
    )

    assert candidate == "https://amazon.jobs/en/jobs/92875670/system-development-engineer"


def test_known_company_careers_url_for_amazon() -> None:
    url = known_company_careers_url(
        "System Development Engineer",
        "Amazon Web Services",
        "Sydney NSW",
    )

    assert url.startswith("https://www.amazon.jobs/en/search?")
    assert "System+Development+Engineer" in url


def test_clicked_apply_url_handles_same_page_navigation() -> None:
    html = """
    <main>
      <button onclick="window.location.href='https://boards.greenhouse.io/example/jobs/123'">
        Apply
      </button>
    </main>
    """

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.route(
            "https://boards.greenhouse.io/example/jobs/123",
            lambda route: route.fulfill(status=200, body="<h1>Apply</h1>"),
        )
        page.set_content(html)
        apply_url = try_capture_clicked_apply_url(page, "linkedin")
        browser.close()

    assert apply_url == "https://boards.greenhouse.io/example/jobs/123"


def test_clicked_apply_url_ignores_quick_apply_button() -> None:
    html = """
    <main>
      <button onclick="window.location.href='https://boards.greenhouse.io/example/jobs/quick'">
        Quick Apply
      </button>
    </main>
    """

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.route(
            "https://boards.greenhouse.io/example/jobs/quick",
            lambda route: route.fulfill(status=200, body="<h1>Quick Apply</h1>"),
        )
        page.set_content(html)
        apply_url = try_capture_clicked_apply_url(page, "linkedin")
        browser.close()

    assert apply_url == ""


def test_record_without_official_apply_url_still_needs_detail_enrichment() -> None:
    assert record_needs_detail_enrichment(
        {
            "employmentType": "Full-time",
            "salary": "$120,000",
            "officialApplyUrl": "",
        }
    )
    assert not record_needs_detail_enrichment(
        {
            "employmentType": "Full-time",
            "salary": "$120,000",
            "officialApplyUrl": "https://jobs.lever.co/example/backend",
        }
    )


def test_extract_jobs_from_records_prefers_explicit_company_field() -> None:
    query = build_search_query("backend", "Remote", "seek")

    jobs = extract_jobs_from_records(
        [
            {
                "title": "Backend Engineer",
                "href": "https://www.seek.com.au/job/123",
                "company": "Explicit Company",
                "cardText": "Backend Engineer\nWrong Fallback Company",
            }
        ],
        query,
        limit=10,
    )

    assert jobs[0].company == "Explicit Company"


def test_extract_jobs_from_records_can_keep_official_apply_only() -> None:
    query = build_search_query("backend", "Remote", "linkedin")

    jobs = extract_jobs_from_records(
        [
            {
                "title": "Backend Engineer",
                "href": "https://www.linkedin.com/jobs/view/123",
                "company": "Example",
                "location": "Remote",
                "employmentType": "Full-time",
                "salary": "",
                "officialApplyUrl": "",
                "cardText": "",
            },
            {
                "title": "Platform Engineer",
                "href": "https://www.linkedin.com/jobs/view/456",
                "company": "Example",
                "location": "Remote",
                "employmentType": "Full-time",
                "salary": "",
                "officialApplyUrl": "https://boards.greenhouse.io/example/jobs/456",
                "cardText": "",
            },
        ],
        query,
        limit=10,
        official_apply_only=True,
    )

    assert len(jobs) == 1
    assert jobs[0].title == "Platform Engineer"


def test_extract_jobs_from_records_skips_location_when_inferring_company() -> None:
    query = build_search_query("backend", "Sydney", "seek")

    jobs = extract_jobs_from_records(
        [
            {
                "title": "Backend Engineer",
                "href": "https://www.seek.com.au/job/123",
                "cardText": (
                    "Backend Engineer\nSydney NSW\nFull time\n"
                    "$130,000 - $150,000\nExample Company"
                ),
            }
        ],
        query,
        limit=10,
    )

    assert jobs[0].company == "Example Company"
    assert jobs[0].employment_type == "Full-time"
    assert jobs[0].salary == "$130,000 - $150,000"


def test_extract_jobs_from_records_reads_explicit_location_and_aud_salary() -> None:
    query = build_search_query("backend", "Sydney", "seek")

    jobs = extract_jobs_from_records(
        [
            {
                "title": "Software Engineer",
                "href": "https://www.seek.com.au/job/456",
                "company": "Example Company",
                "location": "Bella Vista",
                "cardText": (
                    "Software Engineer\nat\nExample Company\n"
                    "This is a Full time job\nBella Vista\n"
                    "AUD 120000 - 145000 per annum"
                ),
            }
        ],
        query,
        limit=10,
    )

    assert jobs[0].location == "Bella Vista"
    assert jobs[0].employment_type == "Full-time"
    assert jobs[0].salary == "AUD 120000 - 145000 per annum"


def test_extract_jobs_from_records_ignores_bad_company_and_salary_values() -> None:
    query = build_search_query("backend", "Sydney", "seek")

    jobs = extract_jobs_from_records(
        [
            {
                "title": "AI Engineer",
                "href": "https://www.seek.com.au/job/789",
                "company": "at",
                "salary": "Pty.",
                "cardText": "AI Engineer\nat\nAutomic Group Pty. Ltd.\nThis is a Full time job",
            }
        ],
        query,
        limit=10,
    )

    assert jobs[0].company == "Automic Group Pty. Ltd."
    assert jobs[0].employment_type == "Full-time"
    assert jobs[0].salary == ""


def test_extract_jobs_from_records_prefers_explicit_type_and_salary() -> None:
    query = build_search_query("backend", "Remote", "seek")

    jobs = extract_jobs_from_records(
        [
            {
                "title": "Backend Engineer",
                "href": "https://www.seek.com.au/job/123",
                "company": "Example Company",
                "employmentType": "Part-time",
                "salary": "$80/hour",
                "cardText": "Backend Engineer\nFull-time\n$100k",
            }
        ],
        query,
        limit=10,
    )

    assert jobs[0].employment_type == "Part-time"
    assert jobs[0].salary == "$80/hour"


def test_infer_employment_type_and_salary_from_card_text() -> None:
    text = "Senior Engineer\nExample Company\nPart time\n90k to 110k"

    assert infer_employment_type(text) == "Part-time"
    assert infer_salary(text) == "90k to 110k"


def test_extract_jobs_from_page_reads_linkedin_nested_type_text() -> None:
    query = build_search_query("backend", "Sydney", "linkedin")
    html = """
    <section class="base-card">
        <a class="base-card__full-link" href="https://www.linkedin.com/jobs/view/123456/">
            Backend Engineer
        </a>
        <h4 class="base-search-card__subtitle">Example Company</h4>
        <span class="job-search-card__location">Sydney NSW</span>
        <div>
            <a><span><span>Full-time</span></span></a>
        </div>
    </section>
    """

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_content(html)
        jobs = extract_jobs_from_page(query, page, limit=10, on_job=None)
        browser.close()

    assert jobs[0].company == "Example Company"
    assert jobs[0].location == "Sydney NSW"
    assert jobs[0].employment_type == "Full-time"
