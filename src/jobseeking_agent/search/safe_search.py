import base64
import re
from collections.abc import Callable
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import parse_qs, quote_plus, unquote, urlencode, urlparse

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from jobseeking_agent.config import get_settings
from jobseeking_agent.database.models import Job
from jobseeking_agent.search.description_formatter import clean_job_description
from jobseeking_agent.search.keyword_search import SearchQuery
from jobseeking_agent.search.state import advance_search_page, next_search_page
from jobseeking_agent.utils.job_urls import canonical_job_url

BLOCKED_MARKERS = (
    "captcha",
    "verify you are human",
    "are you a human",
    "unusual traffic",
    "cloudflare",
    "access denied",
    "temporarily blocked",
    "too many requests",
)

NOISE_COMPANY_FRAGMENTS = (
    "save",
    "saved",
    "listed",
    "ago",
    "apply",
    "view",
    "job",
    "classification",
    "subclassification",
    "salary",
    "remote",
    "hybrid",
    "full time",
    "part time",
    "full-time",
    "part-time",
    "contract",
    "casual",
    "temporary",
    "internship",
    "seek",
    "be an early applicant",
    "promoted",
    "featured",
    "new",
)

OFFICIAL_APPLY_DOMAINS = (
    "greenhouse.io",
    "lever.co",
    "workdayjobs.com",
    "myworkdayjobs.com",
    "smartrecruiters.com",
    "ashbyhq.com",
    "bamboohr.com",
    "jobvite.com",
    "icims.com",
    "successfactors.com",
    "oraclecloud.com",
    "jobs.lever.co",
    "workable.com",
    "recruitee.com",
    "jobadder.com",
    "pinpointhq.com",
    "teamtailor.com",
    "amazon.jobs",
)

SEARCH_RESULT_BLOCKED_DOMAINS = (
    "linkedin.com",
    "seek.com",
    "seek.com.au",
    "seek.co.nz",
    "indeed.com",
    "glassdoor.com",
    "facebook.com",
    "x.com",
    "twitter.com",
)

OFFICIAL_DISCOVERY_CACHE: dict[tuple[str, str, str, str], str] = {}


@dataclass(frozen=True)
class SearchOutcome:
    jobs: list[Job]
    message: str
    blocked: bool = False


class SearchBlockedError(RuntimeError):
    pass


class BrowserNotInstalledError(RuntimeError):
    pass


def platform_search_url(query: SearchQuery, page_number: int = 1) -> str:
    keywords = quote_plus(query.keywords)
    location = quote_plus(query.location)
    page_number = max(1, page_number)

    match query.platform:
        case "seek":
            base = f"https://www.seek.com.au/{keywords}-jobs"
            url = f"{base}/in-{location}" if location else base
            return f"{url}?page={page_number}" if page_number > 1 else url
        case "linkedin":
            start = (page_number - 1) * 25
            url = (
                "https://www.linkedin.com/jobs/search/"
                f"?keywords={keywords}&location={location}"
            )
            return f"{url}&start={start}" if start else url
        case "indeed":
            start = (page_number - 1) * 10
            url = f"https://www.indeed.com/jobs?q={keywords}&l={location}"
            return f"{url}&start={start}" if start else url
        case _:
            return f"https://www.google.com/search?q={keywords}+{location}+jobs"


def looks_blocked(page_text: str) -> bool:
    text = page_text.lower()
    return any(marker in text for marker in BLOCKED_MARKERS)


def is_job_link(platform: str, href: str) -> bool:
    href_lower = href.lower()
    if platform == "seek":
        return "/job/" in href_lower
    if platform == "linkedin":
        return "/jobs/view" in href_lower
    if platform == "indeed":
        return "viewjob" in href_lower or "/rc/clk" in href_lower or "jk=" in href_lower
    return "job" in href_lower or "career" in href_lower


def company_site_search_url(job: Job) -> str:
    query_parts = [
        job.company,
        job.title,
        job.employment_type,
        job.salary,
        "careers official site",
    ]
    query = quote_plus(" ".join(part for part in query_parts if part))
    return f"https://www.google.com/search?q={query}"


def normalize_company(company: str) -> str:
    cleaned = " ".join(company.split())
    cleaned = re.sub(r"^(at|by|company)\s+", "", cleaned, flags=re.IGNORECASE)
    lowered = cleaned.lower()
    if (
        not cleaned
        or lowered in {"at", "by", "company"}
        or "$" in cleaned
        or infer_salary(cleaned)
        or infer_employment_type(cleaned)
        or looks_like_location_line(cleaned)
        or any(fragment in lowered for fragment in NOISE_COMPANY_FRAGMENTS)
    ):
        return ""
    return cleaned[:120]


def normalized_card_lines(card_text: str) -> list[str]:
    lines = [" ".join(line.split()) for line in card_text.splitlines()]
    return [line for line in lines if line]


def looks_like_location_line(text: str) -> bool:
    lowered = text.lower()
    location_markers = (
        "nsw",
        "vic",
        "qld",
        "wa",
        "sa",
        "tas",
        "act",
        "nt",
        "sydney",
        "melbourne",
        "brisbane",
        "perth",
        "adelaide",
        "canberra",
        "australia",
        "remote",
        "hybrid",
        "onsite",
        "on-site",
    )
    return any(marker in lowered for marker in location_markers)


def infer_company_from_card_text(title: str, card_text: str) -> str:
    title = " ".join(title.split())
    lines = normalized_card_lines(card_text)
    lines = [line for line in lines if line and line != title]

    for line in lines[:14]:
        company = normalize_company(line)
        if company:
            return company
    return ""


def infer_employment_type(text: str) -> str:
    lowered = text.lower()
    patterns = (
        ("Full-time", r"\bfull[-\s]?time\b"),
        ("Part-time", r"\bpart[-\s]?time\b"),
        ("Contract", r"\b(contract|contractor)\b"),
        ("Casual", r"\bcasual\b"),
        ("Temporary", r"\b(temp|temporary)\b"),
        ("Internship", r"\b(internship|intern)\b"),
    )
    for label, pattern in patterns:
        if re.search(pattern, lowered):
            return label
    return ""


def normalize_employment_type(employment_type: str) -> str:
    return infer_employment_type(employment_type) or " ".join(employment_type.split())


def infer_salary(text: str) -> str:
    compact_text = " ".join(text.split())
    patterns = (
        r"\b(?:AUD|USD|NZD|CAD|GBP|EUR)\s*[\d,.]+[kK]?"
        r"(?:\s*(?:-|–|to)\s*(?:(?:AUD|USD|NZD|CAD|GBP|EUR)\s*)?[\d,.]+[kK]?)?"
        r"(?:\s*(?:per|a|/)\s*(?:year|annum|hour|day))?",
        r"\$[\d,.]+[kK]?(?:\s*(?:-|–|to)\s*\$?[\d,.]+[kK]?)?"
        r"(?:\s*(?:per|a|/)\s*(?:year|annum|hour|day))?",
        r"\b\d{2,3}\s*[kK]\s*(?:-|–|to)\s*\d{2,3}\s*[kK]\b",
        r"\b\d{2,3}\s*[kK]\b",
    )
    for pattern in patterns:
        match = re.search(pattern, compact_text, re.IGNORECASE)
        if match:
            return match.group(0).strip()
    return ""


def normalize_salary(salary: str) -> str:
    return infer_salary(salary)


def first_non_empty(*values: str) -> str:
    for value in values:
        cleaned = " ".join(value.split())
        if cleaned:
            return cleaned
    return ""


def compact_description(*parts: str, limit: int = 5000) -> str:
    lines: list[str] = []
    seen: set[str] = set()
    for part in parts:
        for raw_line in str(part or "").splitlines():
            line = " ".join(raw_line.split())
            if not line or line.lower() in seen:
                continue
            seen.add(line.lower())
            lines.append(line)
    return clean_job_description("\n".join(lines), limit=limit)


def absolute_url(href: str, page_url: str) -> str:
    if href.startswith("http://") or href.startswith("https://"):
        return href

    parsed = urlparse(page_url)
    if href.startswith("/"):
        return f"{parsed.scheme}://{parsed.netloc}{href}"
    return href


def unwrap_redirect_url(url: str) -> str:
    current = url.strip()
    for _ in range(3):
        parsed = urlparse(current)
        query = parse_qs(parsed.query)
        next_url = first_non_empty(
            *(query.get("url", []) + query.get("u", [])),
            *(query.get("target", []) + query.get("destination", [])),
            *(query.get("redirect", []) + query.get("redirectUrl", [])),
            *(query.get("externalApplyUrl", []) + query.get("applyUrl", [])),
        )
        if not next_url:
            return current
        decoded = unquote(next_url)
        if decoded == current:
            return current
        current = decoded
    return current


def normalize_official_apply_url(url: str, page_url: str, platform: str) -> str:
    absolute = absolute_url(url.strip(), page_url)
    unwrapped = unwrap_redirect_url(absolute)
    if looks_like_official_apply_url(unwrapped, platform):
        return unwrapped
    return ""


def looks_like_official_apply_url(url: str, platform: str) -> bool:
    url = unwrap_redirect_url(url)
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    path = parsed.path.lower()
    if not host:
        return False

    platform_hosts = {
        "seek": ("seek.com", "seek.com.au", "seek.co.nz"),
        "linkedin": ("linkedin.com",),
        "indeed": ("indeed.com",),
    }
    if any(host.endswith(domain) for domain in platform_hosts.get(platform, ())):
        return False

    if any(domain in host for domain in OFFICIAL_APPLY_DOMAINS):
        return True
    return any(marker in path for marker in ("/careers", "/career", "/jobs", "/apply"))


def unwrap_search_result_url(url: str) -> str:
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    target = first_non_empty(
        *(query.get("uddg", []) + query.get("url", []) + query.get("u", []))
    )
    if not target:
        return url
    decoded = unquote(target)
    if decoded.startswith("a1"):
        with suppress(Exception):
            padded = decoded[2:] + "=" * (-len(decoded[2:]) % 4)
            bing_url = base64.urlsafe_b64decode(padded).decode("utf-8")
            if bing_url.startswith(("http://", "https://")):
                return bing_url
    return decoded


def extract_search_result_urls(html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    urls: list[str] = []
    seen: set[str] = set()
    for anchor in soup.select("a[href]"):
        href = unwrap_search_result_url(anchor.get("href", ""))
        if href.startswith("//"):
            href = f"https:{href}"
        if not href.startswith(("http://", "https://")):
            continue
        parsed = urlparse(href)
        host = parsed.netloc.lower()
        if "duckduckgo.com" in host:
            continue
        canonical = href.split("#", 1)[0]
        if canonical in seen:
            continue
        seen.add(canonical)
        urls.append(canonical)
    return urls


def company_tokens(company: str) -> set[str]:
    tokens = {
        token
        for token in re.findall(r"[a-z0-9]+", company.lower())
        if len(token) > 2 and token not in {"the", "pty", "ltd", "inc", "llc", "group"}
    }
    aliases = {
        "amazon": {"amazon", "aws"},
        "amazon web services": {"amazon", "aws"},
    }
    for marker, extra_tokens in aliases.items():
        if marker in company.lower():
            tokens.update(extra_tokens)
    return tokens


def select_official_apply_candidate(
    urls: list[str],
    title: str,
    company: str,
    platform: str,
) -> str:
    tokens = company_tokens(company)
    title_tokens = {
        token for token in re.findall(r"[a-z0-9]+", title.lower()) if len(token) > 3
    }
    scored: list[tuple[int, str]] = []

    for url in urls:
        normalized = normalize_official_apply_url(url, url, platform)
        if not normalized:
            continue
        parsed = urlparse(normalized)
        host = parsed.netloc.lower()
        path = parsed.path.lower()
        if any(domain in host for domain in SEARCH_RESULT_BLOCKED_DOMAINS):
            continue

        score = 0
        if any(domain in host for domain in OFFICIAL_APPLY_DOMAINS):
            score += 20
        if any(token in host for token in tokens):
            score += 12
        if any(token in path for token in tokens):
            score += 4
        if any(token in path for token in title_tokens):
            score += 4
        if any(marker in path for marker in ("/jobs/", "/job/", "/careers/", "/apply")):
            score += 3
        if score >= 12:
            scored.append((score, normalized))

    if not scored:
        return ""
    return sorted(scored, reverse=True)[0][1]


def discover_official_apply_url(title: str, company: str, location: str, platform: str) -> str:
    if not title or not company:
        return ""
    key = (title.lower().strip(), company.lower().strip(), location.lower().strip(), platform)
    if key in OFFICIAL_DISCOVERY_CACHE:
        return OFFICIAL_DISCOVERY_CACHE[key]

    queries = [
        " ".join(
            part
            for part in (
                f'"{title}"',
                f'"{company}"',
                location,
                "careers apply",
            )
            if part
        ),
        " ".join(
            part
            for part in (
                title,
                company,
                location,
                "official careers",
            )
            if part
        ),
    ]

    official_url = ""
    for query in queries:
        official_url = discover_official_apply_url_from_search(query, title, company, platform)
        if official_url:
            break
    if not official_url:
        official_url = known_company_careers_url(title, company, location)

    OFFICIAL_DISCOVERY_CACHE[key] = official_url
    return official_url


def discover_official_apply_url_from_search(
    query: str,
    title: str,
    company: str,
    platform: str,
) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129 Safari/537.36"
        )
    }
    search_sources = (
        ("https://html.duckduckgo.com/html/", {"q": query}),
        ("https://www.bing.com/search", {"q": query}),
    )
    for url, params in search_sources:
        try:
            response = requests.get(url, params=params, headers=headers, timeout=8)
            response.raise_for_status()
            urls = extract_search_result_urls(response.text)
            official_url = select_official_apply_candidate(urls[:12], title, company, platform)
            if official_url:
                return official_url
        except Exception:
            continue
    return ""


def known_company_careers_url(title: str, company: str, location: str) -> str:
    lowered = company.lower()
    if "amazon" in lowered or "aws" in lowered:
        query = urlencode(
            {
                "base_query": title,
                "loc_query": location,
            }
        )
        return f"https://www.amazon.jobs/en/search?{query}"
    return ""


def is_quick_apply_label(label: str) -> bool:
    normalized = " ".join(label.lower().split())
    return any(marker in normalized for marker in ("quick apply", "easy apply"))


def record_needs_detail_enrichment(record: dict[str, str]) -> bool:
    return not (
        record.get("officialApplyUrl")
        and record.get("employmentType")
        and record.get("salary")
    )


def browser_storage_state_path(platform: str, storage_dir: str | None = None) -> Path:
    base_dir = Path(storage_dir or get_settings().browser_storage_dir).expanduser()
    return base_dir / f"{platform.lower().strip()}.json"


def existing_browser_storage_state(platform: str) -> str | None:
    platform_path = browser_storage_state_path(platform)
    shared_path = browser_storage_state_path("default")
    if platform_path.exists():
        return str(platform_path)
    if shared_path.exists():
        return str(shared_path)
    return None


def try_capture_clicked_apply_url(page, platform: str) -> str:
    candidates = page.locator(
        "a, button, [role='button'], [aria-label*='Apply' i], "
        "[data-control-name*='apply' i], [data-tracking-control-name*='apply' i]"
    )
    count = min(candidates.count(), 20)

    for index in range(count):
        candidate = candidates.nth(index)
        with suppress(Exception):
            label = first_non_empty(
                candidate.inner_text(timeout=500),
                candidate.get_attribute("aria-label") or "",
                candidate.get_attribute("title") or "",
            ).lower()
            if "apply" not in label or is_quick_apply_label(label):
                continue

            href = first_non_empty(
                candidate.get_attribute("href") or "",
                candidate.get_attribute("data-href") or "",
                candidate.get_attribute("data-url") or "",
                candidate.get_attribute("data-apply-url") or "",
            )
            apply_url = normalize_official_apply_url(href, page.url, platform)
            if apply_url:
                return apply_url

            context = page.context
            original_url = page.url
            clicked = False
            popup = None
            try:
                with context.expect_page(timeout=1500) as popup_info:
                    candidate.click(timeout=2500, no_wait_after=True)
                    clicked = True
                popup = popup_info.value
            except Exception:
                pass

            if popup is not None:
                popup.wait_for_load_state("domcontentloaded", timeout=5000)
                apply_url = normalize_official_apply_url(popup.url, page.url, platform)
                popup.close()
                if apply_url:
                    return apply_url

            if not clicked:
                with suppress(Exception):
                    candidate.click(timeout=2500, no_wait_after=True)
                    clicked = True

            if clicked:
                with suppress(Exception):
                    page.wait_for_load_state("domcontentloaded", timeout=4000)
                page.wait_for_timeout(1200)
                apply_url = normalize_official_apply_url(page.url, original_url, platform)
                if apply_url:
                    return apply_url
                if page.url != original_url:
                    with suppress(Exception):
                        page.goto(original_url, wait_until="domcontentloaded", timeout=5000)
    return ""


def extract_detail_fields_from_page(page) -> dict[str, str]:
    return page.locator("body").evaluate(
        """
        () => {
            const text = element => (
                element?.innerText ||
                element?.textContent ||
                element?.getAttribute?.("aria-label") ||
                element?.getAttribute?.("title") ||
                ""
            ).trim();
            const href = element => element?.href || element?.getAttribute("href") || "";
            const matchesWorkType = value => {
                const normalized = (value || "").trim().toLowerCase();
                return [
                    "full-time",
                    "full time",
                    "part-time",
                    "part time",
                    "contract",
                    "contractor",
                    "temporary",
                    "casual",
                    "internship",
                    "intern"
                ].some(marker => normalized === marker || normalized.includes(marker));
            };
            const firstMatchingText = selectors => {
                for (const selector of selectors) {
                    for (const element of Array.from(document.querySelectorAll(selector))) {
                        const value = text(element);
                        if (value && matchesWorkType(value)) return value;
                    }
                }
                return "";
            };
            const firstText = selectors => {
                for (const selector of selectors) {
                    const value = text(document.querySelector(selector));
                    if (value) return value;
                }
                return "";
            };
            return {
                employmentType: firstMatchingText([
                    "[data-testid='job-details-jobs-unified-top-card__job-insight']",
                    "[class*='job-insight' i]",
                    "[class*='employment' i]",
                    "[class*='job-type' i]",
                    "a span span",
                    "a span",
                    "li span",
                    "span",
                    "div"
                ]),
                salary: firstText([
                    "[data-automation='jobSalary']",
                    "[data-testid='job-salary']",
                    "[data-testid='salary']",
                    "[class*='salary' i]",
                    "[aria-label*='salary' i]"
                ]),
                applyUrl: (() => {
                    const anchors = Array.from(document.querySelectorAll("a[href]"));
                    const ranked = anchors.map(anchor => ({
                        href: href(anchor),
                        label: text(anchor).toLowerCase()
                    })).filter(item => item.href && (
                        !item.label.includes("quick apply") &&
                        !item.label.includes("easy apply") &&
                        (
                            item.label.includes("apply") ||
                            item.label.includes("application") ||
                            item.href.toLowerCase().includes("greenhouse") ||
                            item.href.toLowerCase().includes("lever.co") ||
                            item.href.toLowerCase().includes("workday") ||
                            item.href.toLowerCase().includes("smartrecruiters") ||
                            item.href.toLowerCase().includes("ashbyhq") ||
                            item.href.toLowerCase().includes("bamboohr") ||
                            item.href.toLowerCase().includes("jobvite") ||
                            item.href.toLowerCase().includes("icims") ||
                            item.href.toLowerCase().includes("successfactors")
                        )
                    ));
                    return ranked[0]?.href || "";
                })(),
                bodyText: text(document.body)
            };
        }
        """
    )


def enrich_records_from_detail_pages(
    page,
    records: list[dict[str, str]],
    query: SearchQuery,
) -> None:
    settings = get_settings()
    detail_page = page.context.new_page()
    try:
        for record in records:
            if not record_needs_detail_enrichment(record):
                continue
            href = record.get("href", "")
            if not href or not is_job_link(query.platform, href):
                continue

            with suppress(Exception):
                detail_page.goto(
                    href,
                    wait_until="domcontentloaded",
                    timeout=get_settings().request_timeout_seconds * 1000,
                )
                detail_page.wait_for_timeout(800)
                detail = extract_detail_fields_from_page(detail_page)
                record["detailText"] = str(detail.get("bodyText", ""))
                apply_url = normalize_official_apply_url(
                    str(detail.get("applyUrl", "")),
                    detail_page.url,
                    query.platform,
                )
                if not apply_url:
                    apply_url = try_capture_clicked_apply_url(detail_page, query.platform)
                if not apply_url and settings.crawler_allow_search_discovery:
                    apply_url = discover_official_apply_url(
                        str(record.get("title", "")),
                        str(record.get("company", "")),
                        str(record.get("location", "")),
                        query.platform,
                    )
                if apply_url:
                    record["officialApplyUrl"] = apply_url
                if not record.get("employmentType"):
                    record["employmentType"] = first_non_empty(
                        str(detail.get("employmentType", "")),
                        infer_employment_type(record["detailText"]),
                    )
                if not record.get("salary"):
                    record["salary"] = first_non_empty(
                        str(detail.get("salary", "")),
                        infer_salary(record["detailText"]),
                    )
    finally:
        with suppress(Exception):
            detail_page.close()


def extract_jobs_from_links(
    links: list[tuple[str, str]],
    query: SearchQuery,
    limit: int,
    on_job: Callable[[Job], None] | None = None,
) -> list[Job]:
    jobs: list[Job] = []
    seen: set[str] = set()

    for title, href in links:
        title = " ".join(title.split())
        canonical_url = canonical_job_url(query.platform, href)
        if not title or not href or canonical_url in seen:
            continue
        if not is_job_link(query.platform, href):
            continue

        seen.add(canonical_url)
        job = Job(
            title=title[:140],
            company="",
            location=query.location,
            platform=query.platform,
            job_url=canonical_url,
            description="",
            status="found",
        )
        jobs.append(job)
        if on_job is not None:
            on_job(job)
        if len(jobs) >= limit:
            break

    return jobs


def extract_jobs_from_records(
    records: list[dict[str, str]],
    query: SearchQuery,
    limit: int,
    on_job: Callable[[Job], None] | None = None,
    official_apply_only: bool = False,
) -> list[Job]:
    jobs: list[Job] = []
    seen: set[str] = set()

    for record in records:
        title = " ".join(record.get("title", "").split())
        href = record.get("href", "")
        canonical_url = canonical_job_url(query.platform, href)
        if not title or not href or canonical_url in seen:
            continue
        if not is_job_link(query.platform, href):
            continue
        if official_apply_only and not record.get("officialApplyUrl"):
            continue

        seen.add(canonical_url)
        company = normalize_company(record.get("company", ""))
        if not company:
            company = infer_company_from_card_text(title, record.get("cardText", ""))
        card_text = first_non_empty(record.get("cardText", ""), record.get("detailText", ""))
        location = first_non_empty(record.get("location", ""), query.location)
        employment_type = first_non_empty(
            normalize_employment_type(record.get("employmentType", "")),
            infer_employment_type(card_text),
        )
        salary = first_non_empty(
            normalize_salary(record.get("salary", "")),
            infer_salary(card_text),
        )
        job = Job(
            title=title[:140],
            company=company,
            location=location,
            employment_type=employment_type,
            salary=salary,
            platform=query.platform,
            job_url=canonical_url,
            official_apply_url=record.get("officialApplyUrl", ""),
            description="",
            status="found",
        )
        description = compact_description(
            record.get("detailText", ""),
            record.get("cardText", ""),
            f"Company site search: {company_site_search_url(job)}",
        )
        job = Job(
            title=job.title,
            company=job.company,
            location=job.location,
            employment_type=job.employment_type,
            salary=job.salary,
            platform=job.platform,
            job_url=job.job_url,
            official_apply_url=job.official_apply_url,
            description=description,
            status=job.status,
        )
        jobs.append(job)
        if on_job is not None:
            on_job(job)
        if len(jobs) >= limit:
            break

    return jobs


def extract_jobs_from_page(
    query: SearchQuery,
    page,
    limit: int,
    on_job,
    official_apply_only: bool = False,
) -> list[Job]:
    records = page.locator("body").evaluate(
        """
        () => {
            const text = element => (
                element?.innerText ||
                element?.textContent ||
                element?.getAttribute?.("aria-label") ||
                element?.getAttribute?.("title") ||
                ""
            ).trim();
            const href = element => element?.href || element?.getAttribute("href") || "";
            const matchesWorkType = value => {
                const normalized = (value || "").trim().toLowerCase();
                return [
                    "full-time",
                    "full time",
                    "part-time",
                    "part time",
                    "contract",
                    "contractor",
                    "temporary",
                    "casual",
                    "internship",
                    "intern"
                ].some(marker => normalized === marker || normalized.includes(marker));
            };
            const firstText = (root, selectors) => {
                if (!root) return "";
                for (const selector of selectors) {
                    const value = text(root.querySelector(selector));
                    if (value) return value;
                }
                return "";
            };
            const firstMatchingText = (root, selectors, predicate) => {
                if (!root) return "";
                for (const selector of selectors) {
                    for (const element of Array.from(root.querySelectorAll(selector))) {
                        const value = text(element);
                        if (value && predicate(value)) return value;
                    }
                }
                return "";
            };
            const titleElements = Array.from(document.querySelectorAll(
                [
                    "a[data-automation='jobTitle']",
                    "a.base-card__full-link",
                    "h2.jobTitle a",
                    "a[data-jk]",
                    "a[id^='job_']",
                    "a[data-testid='job-card-title']",
                    "a[data-testid='job-title']",
                    "a[href*='/job/'][id^='job-title']",
                    "a[href*='/jobs/view']",
                    "a[href*='viewjob']"
                ].join(",")
            ));

            const cardRecords = titleElements.map(titleElement => {
                const card = titleElement.closest(
                    [
                        "[data-search-sol-meta]",
                        ".base-card",
                        ".job-search-card",
                        ".job_seen_beacon",
                        "td.resultContent",
                        "[data-entity-urn*='jobPosting']",
                        "article[data-testid*='job']",
                        "article[data-automation*='job']",
                        "[data-testid='job-card']",
                        "[data-automation='job-card']",
                        "[data-automation='normalJob']",
                        "[data-automation='premiumJob']",
                        "li[data-testid*='job']",
                        "article"
                    ].join(",")
                );
                return {
                    title: text(titleElement),
                    href: href(titleElement),
                    company: firstText(card, [
                        "[data-automation='jobCompany']",
                        "[data-testid='company-name']",
                        "[data-testid='companyName']",
                        "[data-testid='job-company']",
                        "[data-testid='company-name']",
                        ".base-search-card__subtitle",
                        ".companyName",
                        "[data-company-name]",
                        "[data-automation*='company' i]",
                        "[data-type='company']",
                        "span.companyName",
                        "a[href*='/companies/']"
                    ]),
                    location: firstText(card, [
                        "[data-automation='jobLocation']",
                        "[data-automation='jobCardLocation']",
                        "[data-testid='job-location']",
                        "[data-testid='text-location']",
                        ".job-search-card__location",
                        ".companyLocation",
                        "[data-type='location']"
                    ]),
                    employmentType: firstText(card, [
                        "[data-automation='jobWorkType']",
                        "[data-testid='job-work-type']",
                        "[data-testid='work-type']",
                        "[data-testid='job-details-jobs-unified-top-card__job-insight']",
                        "[class*='job-insight' i]",
                        "[data-automation*='workType' i]",
                        "[data-automation*='jobType' i]",
                        "[aria-label*='work type' i]"
                    ]) || firstMatchingText(card, [
                        "a span span",
                        "a span",
                        "li span",
                        "span",
                        "div"
                    ], matchesWorkType),
                    salary: firstText(card, [
                        "[data-automation='jobSalary']",
                        "[data-testid='job-salary']",
                        "[data-testid='salary']",
                        "[data-automation*='salary' i]",
                        ".job-search-card__salary-info",
                        ".salary-snippet",
                        "[class*='salary' i]",
                        "[aria-label*='salary' i]"
                    ]),
                    cardText: text(card)
                };
            });

            if (cardRecords.some(record => record.title && record.href)) {
                return cardRecords;
            }

            return Array.from(document.querySelectorAll("a")).map(anchor => {
                const card = anchor.closest(
                    [
                        "[data-search-sol-meta]",
                        ".base-card",
                        ".job-search-card",
                        ".job_seen_beacon",
                        "td.resultContent",
                        "article",
                        "[data-testid*='job']",
                        "[data-automation*='job']",
                        "section",
                        "li",
                        "div"
                    ].join(",")
                );
                const companyElement = card?.querySelector?.(
                    [
                        "[data-automation='jobCompany']",
                        "[data-testid='company-name']",
                        "[data-testid='companyName']",
                        ".base-search-card__subtitle",
                        ".companyName"
                    ].join(",")
                );
                return {
                    title: text(anchor),
                    href: href(anchor),
                    company: text(companyElement),
                    location: "",
                    employmentType: "",
                    salary: "",
                    cardText: card ? text(card) : ""
                };
            });
        }
        """
    )
    normalized_records = [
        {
            "title": first_non_empty(str(record.get("title", ""))),
            "href": absolute_url(str(record.get("href", "")), page.url),
            "company": first_non_empty(str(record.get("company", ""))),
            "location": first_non_empty(str(record.get("location", ""))),
            "employmentType": first_non_empty(str(record.get("employmentType", ""))),
            "salary": first_non_empty(str(record.get("salary", ""))),
            "cardText": str(record.get("cardText", "")),
            "detailText": "",
            "officialApplyUrl": "",
        }
        for record in records
    ]
    if page.url.startswith(("http://", "https://")):
        enrich_records_from_detail_pages(page, normalized_records[:limit], query)
    return extract_jobs_from_records(
        normalized_records,
        query,
        limit,
        on_job,
        official_apply_only=official_apply_only,
    )


def search_jobs(
    query: SearchQuery,
    on_job: Callable[[Job], None] | None = None,
    on_manual_verification: Callable[[], None] | None = None,
    allow_manual_verification: bool = False,
    official_apply_only: bool | None = None,
) -> SearchOutcome:
    settings = get_settings()
    limit = min(settings.max_search_results, settings.max_jobs_per_source)
    official_apply_only = (
        settings.crawler_official_apply_only
        if official_apply_only is None
        else official_apply_only
    )
    page_number = next_search_page(query)
    url = platform_search_url(query, page_number=page_number)

    browser = None
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                headless=settings.browser_headless,
                slow_mo=settings.browser_slow_mo_ms,
            )
            storage_state = existing_browser_storage_state(query.platform)
            context_kwargs = {"user_agent": settings.user_agent}
            if storage_state:
                context_kwargs["storage_state"] = storage_state
            context = browser.new_context(**context_kwargs)
            page = context.new_page()
            page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=settings.request_timeout_seconds * 1000,
            )
            page.wait_for_timeout(settings.crawl_delay_seconds * 1000)

            page_text = page.locator("body").inner_text(timeout=5000)
            if looks_blocked(page_text):
                if not allow_manual_verification:
                    raise SearchBlockedError(
                        "Search stopped because the platform requested login or human verification."
                    )
                if on_manual_verification is not None:
                    on_manual_verification()
                else:
                    input(
                        "Complete login or human verification in the browser, "
                        "then press Enter here..."
                    )
                page.wait_for_timeout(1000)

            jobs = extract_jobs_from_page(
                query,
                page,
                limit,
                on_job,
                official_apply_only=official_apply_only,
            )
            advance_search_page(query)
            browser.close()
            browser = None
        suffix = " with official apply links" if official_apply_only else ""
        return SearchOutcome(
            jobs=jobs,
            message=f"Found {len(jobs)} jobs{suffix} from {query.platform} page {page_number}.",
        )
    except SearchBlockedError as exc:
        return SearchOutcome(jobs=[], message=str(exc), blocked=True)
    except PlaywrightTimeoutError:
        return SearchOutcome(
            jobs=[],
            message="Search timed out. Try fewer keywords, another platform, or manual login.",
            blocked=True,
        )
    except Exception as exc:
        message = str(exc)
        if "Executable doesn't exist" in message or "playwright install" in message:
            return SearchOutcome(
                jobs=[],
                message=(
                    "Playwright browser is not installed. Run: "
                    "python -m playwright install chromium"
                ),
                blocked=True,
            )
        return SearchOutcome(jobs=[], message=f"Search failed: {message}", blocked=True)
    finally:
        if browser is not None:
            with suppress(Exception):
                browser.close()
