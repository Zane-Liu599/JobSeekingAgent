from pathlib import Path

from jobseeking_agent.ai.gemini_cover_letter import (
    build_cover_letter_prompt,
    generate_cover_letter_with_gemini,
    read_text_file,
)
from jobseeking_agent.database.models import Job
from jobseeking_agent.profile import CandidateProfile


def test_build_cover_letter_prompt_includes_resume_template_and_job() -> None:
    prompt = build_cover_letter_prompt(
        Job(title="Backend Engineer", company="Example Co", description="Build APIs"),
        CandidateProfile(name="Zane", target_titles="Backend Engineer"),
        resume_text="Python and API experience",
        template_text="Dear team template",
    )

    assert "Zane" in prompt
    assert "Python and API experience" in prompt
    assert "Dear team template" in prompt
    assert "Example Co" in prompt
    assert "Build APIs" in prompt


def test_read_text_file_ignores_missing_file() -> None:
    assert read_text_file("missing-file.md") == ""


def test_read_text_file_reads_markdown(tmp_path: Path) -> None:
    path = tmp_path / "resume.md"
    path.write_text("Resume content", encoding="utf-8")

    assert read_text_file(str(path)) == "Resume content"


def test_gemini_generation_falls_back_without_api_key(monkeypatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "")

    result = generate_cover_letter_with_gemini(
        Job(title="Backend Engineer", company="Example Co")
    )

    assert result.provider == "local-fallback"
    assert "GEMINI_API_KEY" in result.error
    assert "Backend Engineer" in result.text
