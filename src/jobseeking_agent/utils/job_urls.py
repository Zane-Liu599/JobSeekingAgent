import re
from urllib.parse import parse_qs, urlparse


def first_non_empty(*values: str) -> str:
    for value in values:
        cleaned = " ".join(value.split())
        if cleaned:
            return cleaned
    return ""


def canonical_job_url(platform: str, href: str) -> str:
    parsed = urlparse(href)
    path = parsed.path.rstrip("/")

    if platform == "seek":
        match = re.search(r"/job/(\d+)", path)
        if match:
            return f"{parsed.scheme}://{parsed.netloc}/job/{match.group(1)}"
    if platform == "linkedin":
        match = re.search(r"/jobs/view/(\d+)", path)
        if match:
            return f"{parsed.scheme}://{parsed.netloc}/jobs/view/{match.group(1)}"
    if platform == "indeed":
        query = parse_qs(parsed.query)
        job_key = first_non_empty(*(query.get("jk", []) + query.get("vjk", [])))
        if job_key:
            return f"{parsed.scheme}://{parsed.netloc}/viewjob?jk={job_key}"

    if parsed.scheme and parsed.netloc:
        return f"{parsed.scheme}://{parsed.netloc}{path}"
    return href.split("#", 1)[0].split("?", 1)[0]
