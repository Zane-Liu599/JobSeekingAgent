from dataclasses import dataclass
from pathlib import Path

from google import genai

from jobseeking_agent.config import get_settings
from jobseeking_agent.database.models import Job
from jobseeking_agent.profile import CandidateProfile, load_profile

MAX_CONTEXT_CHARS = 12000


@dataclass(frozen=True)
class CoverLetterResult:
    text: str
    provider: str
    model: str
    used_resume: bool
    used_template: bool
    error: str = ""


def read_text_file(path: str) -> str:
    if not path:
        return ""

    file_path = Path(path).expanduser()
    if not file_path.exists() or not file_path.is_file():
        return ""

    suffix = file_path.suffix.lower()
    if suffix not in {".txt", ".md", ".text"}:
        return f"[Uploaded file: {file_path.name}. Text extraction for this format is pending.]"

    return file_path.read_text(encoding="utf-8", errors="ignore")[:MAX_CONTEXT_CHARS]


def fallback_cover_letter(job: Job, profile: CandidateProfile) -> str:
    candidate_name = profile.name or "Candidate"
    return f"""# Cover Letter Draft

Dear Hiring Team,

I am excited to apply for the {job.title} role at {job.company}. My background aligns
with the responsibilities described in this position, and I would welcome the
opportunity to contribute to your team.

This draft was generated locally because Gemini is not configured or unavailable.
Review and customize it before submitting.

Best regards,

{candidate_name}
"""


def build_cover_letter_prompt(
    job: Job,
    profile: CandidateProfile,
    resume_text: str,
    template_text: str,
) -> str:
    return f"""
You are an expert career assistant. Write a tailored cover letter for a real job application.

Rules:
- Use a professional, direct, human tone.
- Do not invent experience, employers, degrees, certifications, or metrics.
- Use the resume/profile facts only when supported by the provided content.
- If a cover letter template is provided, preserve its broad style and structure where useful.
- Tailor the letter to the company, role, and job description.
- Keep it concise: about 250-400 words.
- Return only the cover letter body in Markdown. Do not include analysis.

Candidate profile:
Name: {profile.name}
Email: {profile.email}
Phone: {profile.phone}
Location: {profile.location}
Work authorization: {profile.work_authorization}
Target titles: {profile.target_titles}
Target locations: {profile.target_locations}
Minimum salary: {profile.min_salary}
Notes: {profile.notes}

Resume content:
{resume_text or "[No readable resume text provided.]"}

Optional cover letter template:
{template_text or "[No template provided.]"}

Job:
Title: {job.title}
Company: {job.company}
Location: {job.location}
Platform: {job.platform}
URL: {job.job_url}
Description:
{job.description or "[No job description provided.]"}
""".strip()


def generate_cover_letter_with_gemini(job: Job) -> CoverLetterResult:
    settings = get_settings()
    profile = load_profile()
    resume_text = read_text_file(profile.resume_path)
    template_text = read_text_file(profile.cover_letter_template_path)

    if not settings.gemini_api_key:
        return CoverLetterResult(
            text=fallback_cover_letter(job, profile),
            provider="local-fallback",
            model="none",
            used_resume=bool(resume_text),
            used_template=bool(template_text),
            error="GEMINI_API_KEY is not configured.",
        )

    try:
        client = genai.Client(api_key=settings.gemini_api_key)
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=build_cover_letter_prompt(job, profile, resume_text, template_text),
        )
        text = (response.text or "").strip()
        if not text:
            raise RuntimeError("Gemini returned an empty response.")

        return CoverLetterResult(
            text=text,
            provider="gemini",
            model=settings.gemini_model,
            used_resume=bool(resume_text),
            used_template=bool(template_text),
        )
    except Exception as exc:
        return CoverLetterResult(
            text=fallback_cover_letter(job, profile),
            provider="local-fallback",
            model=settings.gemini_model,
            used_resume=bool(resume_text),
            used_template=bool(template_text),
            error=str(exc),
        )
