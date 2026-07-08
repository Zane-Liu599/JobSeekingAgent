from __future__ import annotations

import html
import re

from bs4 import BeautifulSoup

NOISY_DESCRIPTION_MARKERS = (
    "show more",
    "show less",
    "easy apply",
    "quick apply",
    "save job",
    "sign in to create job alert",
    "get notified about new",
    "seniority level",
    "employment type",
    "job function",
    "industries",
)

SECTION_MARKERS = (
    "about the job",
    "about this job",
    "about the role",
    "responsibilities",
    "requirements",
    "qualifications",
    "what you will do",
    "what you'll do",
    "what you bring",
    "benefits",
    "salary",
)


def clean_job_description(value: object, limit: int = 5000) -> str:
    text = raw_text(value)
    if not text:
        return ""

    lines = []
    seen: set[str] = set()
    for line in split_description_lines(text):
        normalized = normalize_line(line)
        if not normalized:
            continue
        lowered = normalized.lower()
        if lowered in seen or is_noisy_line(lowered):
            continue
        seen.add(lowered)
        lines.append(format_line(normalized))

    return "\n".join(lines)[:limit].strip()


def raw_text(value: object) -> str:
    if value is None:
        return ""
    text = str(value)
    if text.lower() in {"nan", "none", "nat"}:
        return ""
    if "<" in text and ">" in text:
        text = BeautifulSoup(text, "html.parser").get_text("\n", strip=True)
    text = html.unescape(text)
    text = text.replace("\\n", "\n").replace("\\t", " ")
    return text


def split_description_lines(text: str) -> list[str]:
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(
        r"([.!?])\s+(?=(?:Responsibilities|Requirements|Qualifications|Benefits|About)\b)",
        r"\1\n",
        text,
    )
    text = re.sub(r"\s*[•●]\s*", "\n- ", text)
    return [part for part in text.splitlines() if part.strip()]


def normalize_line(line: str) -> str:
    line = re.sub(r"\s+", " ", line).strip()
    line = re.sub(r"^[-*]\s*", "- ", line)
    return line


def is_noisy_line(lowered: str) -> bool:
    if len(lowered) < 3:
        return True
    if any(marker in lowered for marker in NOISY_DESCRIPTION_MARKERS):
        return True
    return bool(re.fullmatch(r"\d+[dhwmy]?\s+ago", lowered))


def format_line(line: str) -> str:
    lowered = line.lower().rstrip(":")
    if lowered in SECTION_MARKERS:
        return f"### {line.rstrip(':')}"
    if re.match(r"^(responsibilities|requirements|qualifications|benefits|about)\b", lowered):
        return f"### {line.rstrip(':')}"
    if line.startswith("- "):
        return line
    if len(line) <= 120 and line.endswith(":"):
        return f"### {line.rstrip(':')}"
    return line
