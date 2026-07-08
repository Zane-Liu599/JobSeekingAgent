import re
from dataclasses import dataclass
from urllib.parse import quote_plus, urlencode, urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from jobseeking_agent.db.models import Company, Job
from jobseeking_agent.search.safe_search import (
    discover_official_apply_url_from_search,
    extract_search_result_urls,
    first_non_empty,
    looks_like_official_apply_url,
)

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129 Safari/537.36"
    )
}


@dataclass(frozen=True)
class CompanyScanResult:
    company: Company
    jobs: list[Job]
    message: str


def infer_ats_provider(url: str) -> str:
    host = urlparse(url).netloc.lower()
    if "greenhouse.io" in host:
        return "greenhouse"
    if "lever.co" in host:
        return "lever"
    if "ashbyhq.com" in host:
        return "ashby"
    if "smartrecruiters.com" in host:
        return "smartrecruiters"
    if "workdayjobs.com" in host or "myworkdayjobs.com" in host:
        return "workday"
    if "amazon.jobs" in host:
        return "amazon"
    return "generic"


def known_company_careers_source(company_name: str) -> tuple[str, str, str]:
    lowered = company_name.lower()
    if "amazon" in lowered or "aws" in lowered:
        return (
            "https://www.amazon.jobs/en/search",
            "https://www.amazon.jobs",
            "amazon",
        )
    return "", "", ""


def discover_company_source(company_name: str) -> Company:
    careers_url, website_url, provider = known_company_careers_source(company_name)
    if careers_url:
        return Company(
            name=company_name,
            website_url=website_url,
            careers_url=careers_url,
            ats_provider=provider,
            source="known-company",
        )

    query = f'"{company_name}" careers jobs official site'
    careers_url = discover_official_apply_url_from_search(
        query,
        "careers jobs",
        company_name,
        "company",
    )
    if careers_url:
        parsed = urlparse(careers_url)
        return Company(
            name=company_name,
            website_url=f"{parsed.scheme}://{parsed.netloc}",
            careers_url=careers_url,
            ats_provider=infer_ats_provider(careers_url),
            source="search",
        )

    fallback_url = discover_company_careers_url_from_search(company_name)
    parsed = urlparse(fallback_url) if fallback_url else None
    return Company(
        name=company_name,
        website_url=f"{parsed.scheme}://{parsed.netloc}" if parsed else "",
        careers_url=fallback_url,
        ats_provider=infer_ats_provider(fallback_url) if fallback_url else "",
        source="search" if fallback_url else "job-board-lead",
    )


def discover_company_careers_url_from_search(company_name: str) -> str:
    try:
        response = requests.get(
            "https://www.bing.com/search",
            params={"q": f"{company_name} careers jobs official site"},
            headers=DEFAULT_HEADERS,
            timeout=8,
        )
        response.raise_for_status()
    except Exception:
        return ""

    for url in extract_search_result_urls(response.text)[:10]:
        parsed = urlparse(url)
        host = parsed.netloc.lower()
        path = parsed.path.lower()
        if any(blocked in host for blocked in ("linkedin.com", "seek.com", "indeed.com")):
            continue
        if "careers" in path or "jobs" in path or looks_like_official_apply_url(url, "company"):
            return url
    return ""


def scan_company_careers(
    company: Company,
    keywords: str = "",
    location: str = "",
    limit: int = 20,
) -> CompanyScanResult:
    if not company.careers_url:
        discovered = discover_company_source(company.name)
        company = Company(
            name=company.name,
            website_url=first_non_empty(company.website_url, discovered.website_url),
            careers_url=discovered.careers_url,
            ats_provider=first_non_empty(company.ats_provider, discovered.ats_provider),
            source=first_non_empty(company.source, discovered.source),
            last_scanned_at=company.last_scanned_at,
            created_at=company.created_at,
            id=company.id,
        )

    if not company.careers_url:
        return CompanyScanResult(company=company, jobs=[], message="No careers URL found.")

    provider = company.ats_provider or infer_ats_provider(company.careers_url)
    match provider:
        case "greenhouse":
            jobs = scan_greenhouse(company, keywords, location, limit)
        case "lever":
            jobs = scan_lever(company, keywords, location, limit)
        case "amazon":
            jobs = scan_amazon_jobs(company, keywords, location, limit)
        case _:
            jobs = scan_generic_careers_page(company, keywords, location, limit)

    return CompanyScanResult(
        company=Company(
            name=company.name,
            website_url=company.website_url,
            careers_url=company.careers_url,
            ats_provider=provider,
            source=company.source,
            last_scanned_at=company.last_scanned_at,
            created_at=company.created_at,
            id=company.id,
        ),
        jobs=jobs,
        message=f"Found {len(jobs)} official job(s) from {provider}.",
    )


def scan_greenhouse(company: Company, keywords: str, location: str, limit: int) -> list[Job]:
    slug = greenhouse_slug(company.careers_url)
    if not slug:
        return scan_generic_careers_page(company, keywords, location, limit)
    try:
        response = requests.get(
            f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs",
            params={"content": "true"},
            headers=DEFAULT_HEADERS,
            timeout=10,
        )
        response.raise_for_status()
        records = response.json().get("jobs", [])
    except Exception:
        return []

    jobs: list[Job] = []
    for record in records:
        title = str(record.get("title", ""))
        absolute_url = str(record.get("absolute_url", ""))
        location = first_non_empty(record.get("location", {}).get("name", ""))
        if not job_matches(title, location, keywords, ""):
            continue
        jobs.append(
            Job(
                title=title,
                company=company.name,
                location=location,
                platform="company",
                job_url=absolute_url,
                official_apply_url=absolute_url,
                description=strip_html(str(record.get("content", "")))[:4000],
            )
        )
        if len(jobs) >= limit:
            break
    return jobs


def scan_lever(company: Company, keywords: str, location: str, limit: int) -> list[Job]:
    slug = lever_slug(company.careers_url)
    if not slug:
        return scan_generic_careers_page(company, keywords, location, limit)
    try:
        response = requests.get(
            f"https://api.lever.co/v0/postings/{slug}",
            params={"mode": "json"},
            headers=DEFAULT_HEADERS,
            timeout=10,
        )
        response.raise_for_status()
        records = response.json()
    except Exception:
        return []

    jobs: list[Job] = []
    for record in records:
        title = str(record.get("text", ""))
        hosted_url = str(record.get("hostedUrl", ""))
        categories = record.get("categories", {}) or {}
        location_value = first_non_empty(str(categories.get("location", "")))
        commitment = first_non_empty(str(categories.get("commitment", "")))
        if not job_matches(title, location_value, keywords, ""):
            continue
        jobs.append(
            Job(
                title=title,
                company=company.name,
                location=location_value,
                employment_type=commitment,
                platform="company",
                job_url=hosted_url,
                official_apply_url=hosted_url,
                description=strip_html(str(record.get("description", "")))[:4000],
            )
        )
        if len(jobs) >= limit:
            break
    return jobs


def scan_amazon_jobs(company: Company, keywords: str, location: str, limit: int) -> list[Job]:
    params = {
        "base_query": keywords,
        "loc_query": location,
    }
    search_url = f"https://www.amazon.jobs/en/search?{urlencode(params)}"
    return scan_generic_careers_page(
        Company(
            name=company.name,
            website_url=company.website_url,
            careers_url=search_url,
            ats_provider="amazon",
            source=company.source,
        ),
        keywords,
        location,
        limit,
    )


def scan_generic_careers_page(
    company: Company,
    keywords: str,
    location: str,
    limit: int,
) -> list[Job]:
    try:
        response = requests.get(company.careers_url, headers=DEFAULT_HEADERS, timeout=10)
        response.raise_for_status()
    except Exception:
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    jobs: list[Job] = []
    seen: set[str] = set()
    for anchor in soup.select("a[href]"):
        title = " ".join(anchor.get_text(" ", strip=True).split())
        href = urljoin(company.careers_url, anchor.get("href", ""))
        if not title or href in seen:
            continue
        if not looks_like_job_link(title, href):
            continue
        if not job_matches(title, "", keywords, location):
            continue
        if is_job_board_url(href):
            continue
        if not looks_like_official_apply_url(href, "company"):
            continue

        seen.add(href)
        jobs.append(
            Job(
                title=title[:140],
                company=company.name,
                location=location,
                platform="company",
                job_url=href,
                official_apply_url=href,
                description=f"Official company careers source: {company.careers_url}",
            )
        )
        if len(jobs) >= limit:
            break
    return jobs


def greenhouse_slug(url: str) -> str:
    parsed = urlparse(url)
    parts = [part for part in parsed.path.split("/") if part]
    if "boards.greenhouse.io" in parsed.netloc and parts:
        return parts[0]
    return ""


def lever_slug(url: str) -> str:
    parsed = urlparse(url)
    parts = [part for part in parsed.path.split("/") if part]
    if "jobs.lever.co" in parsed.netloc and parts:
        return parts[0]
    return ""


def job_matches(title: str, job_location: str, keywords: str, location: str) -> bool:
    text = f"{title} {job_location}".lower()
    keyword_parts = [part for part in re.findall(r"[a-z0-9]+", keywords.lower()) if len(part) > 2]
    location_parts = [part for part in re.findall(r"[a-z0-9]+", location.lower()) if len(part) > 2]
    if keyword_parts and not any(part in text for part in keyword_parts):
        return False
    return not (
        location_parts
        and job_location
        and not any(part in text for part in location_parts)
    )


def looks_like_job_link(title: str, href: str) -> bool:
    lowered = f"{title} {href}".lower()
    return any(
        marker in lowered
        for marker in ("engineer", "developer", "analyst", "manager", "jobs/", "job/", "apply")
    )


def is_job_board_url(url: str) -> bool:
    host = urlparse(url).netloc.lower()
    return any(
        blocked in host
        for blocked in ("linkedin.com", "seek.com", "indeed.com", "glassdoor.com")
    )


def strip_html(value: str) -> str:
    return BeautifulSoup(value, "html.parser").get_text(" ", strip=True)


def company_search_url(company_name: str, keywords: str = "", location: str = "") -> str:
    query = " ".join(part for part in (company_name, keywords, location, "careers jobs") if part)
    return f"https://www.google.com/search?q={quote_plus(query)}"
