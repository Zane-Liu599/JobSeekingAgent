from pathlib import Path

from jobseeking_agent.profile import (
    CandidateProfile,
    copy_profile_file,
    load_profile,
    save_profile,
)


def test_save_and_load_profile(tmp_path: Path) -> None:
    path = tmp_path / "profile.json"
    save_profile(CandidateProfile(name="Zane", email="zane@example.com"), path)

    profile = load_profile(path)

    assert profile.name == "Zane"
    assert profile.email == "zane@example.com"


def test_copy_profile_file(tmp_path: Path) -> None:
    source = tmp_path / "resume.pdf"
    destination_dir = tmp_path / "resumes"
    source.write_text("resume", encoding="utf-8")

    copied = copy_profile_file(str(source), destination_dir)

    assert copied.exists()
    assert copied.read_text(encoding="utf-8") == "resume"
