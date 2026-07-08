from pathlib import Path

from jobseeking_agent.db import Company, get_company_by_name, init_db, list_companies, save_company
from jobseeking_agent.search.company_careers import (
    greenhouse_slug,
    infer_ats_provider,
    known_company_careers_source,
    lever_slug,
    scan_amazon_jobs,
    scan_generic_careers_page,
)


class FakeResponse:
    def __init__(self, text: str, payload=None):
        self.text = text
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self):
        return self._payload


def test_save_and_list_companies(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'agent.db'}"

    init_db(database_url)
    company_id = save_company(
        Company(
            name="Example Co",
            website_url="https://example.com",
            careers_url="https://jobs.lever.co/example",
            ats_provider="lever",
            source="test",
        ),
        database_url,
    )

    companies = list_companies(database_url)
    company = get_company_by_name("example   co", database_url)

    assert company_id > 0
    assert len(companies) == 1
    assert company is not None
    assert company.careers_url == "https://jobs.lever.co/example"


def test_save_company_preserves_existing_careers_url(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'agent.db'}"

    init_db(database_url)
    save_company(
        Company(name="Example Co", careers_url="https://jobs.lever.co/example"),
        database_url,
    )
    save_company(Company(name="Example Co", website_url="https://example.com"), database_url)

    company = get_company_by_name("Example Co", database_url)

    assert company is not None
    assert company.website_url == "https://example.com"
    assert company.careers_url == "https://jobs.lever.co/example"


def test_infer_ats_provider() -> None:
    assert infer_ats_provider("https://boards.greenhouse.io/example") == "greenhouse"
    assert infer_ats_provider("https://jobs.lever.co/example") == "lever"
    assert infer_ats_provider("https://www.amazon.jobs/en/search") == "amazon"
    assert infer_ats_provider("https://example.com/careers") == "generic"


def test_ats_slug_helpers() -> None:
    assert greenhouse_slug("https://boards.greenhouse.io/example/jobs/123") == "example"
    assert lever_slug("https://jobs.lever.co/example/backend-engineer") == "example"


def test_known_company_careers_source_for_amazon() -> None:
    careers_url, website_url, provider = known_company_careers_source("Amazon Web Services")

    assert careers_url == "https://www.amazon.jobs/en/search"
    assert website_url == "https://www.amazon.jobs"
    assert provider == "amazon"


def test_scan_generic_careers_page_extracts_official_links(monkeypatch) -> None:
    html = """
    <html>
      <body>
        <a href="/careers/software-engineer">Software Engineer</a>
        <a href="https://www.linkedin.com/jobs/view/123">Software Engineer</a>
      </body>
    </html>
    """

    def fake_get(*args, **kwargs):
        return FakeResponse(html)

    monkeypatch.setattr("jobseeking_agent.search.company_careers.requests.get", fake_get)

    jobs = scan_generic_careers_page(
        Company(name="Example Co", careers_url="https://example.com/careers"),
        "software engineer",
        "",
        10,
    )

    assert len(jobs) == 1
    assert jobs[0].official_apply_url == "https://example.com/careers/software-engineer"


def test_scan_amazon_jobs_builds_search_url(monkeypatch) -> None:
    captured = {}

    def fake_get(url, *args, **kwargs):
        captured["url"] = url
        return FakeResponse(
            """
            <html>
              <body>
                <a href="/en/jobs/123/software-development-engineer">
                  Software Development Engineer
                </a>
              </body>
            </html>
            """
        )

    monkeypatch.setattr("jobseeking_agent.search.company_careers.requests.get", fake_get)

    jobs = scan_amazon_jobs(
        Company(name="Amazon Web Services", careers_url="https://www.amazon.jobs/en/search"),
        "software engineer",
        "Sydney",
        10,
    )

    assert "base_query=software+engineer" in captured["url"]
    assert len(jobs) == 1
    assert jobs[0].official_apply_url.startswith("https://www.amazon.jobs/en/jobs/123")
