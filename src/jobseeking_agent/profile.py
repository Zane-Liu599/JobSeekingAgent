import json
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path

from jobseeking_agent.config import get_settings

PROFILE_PATH = Path("data/profile.json")
RESUME_DIR = Path("data/resumes")
COVER_LETTER_DIR = Path("data/cover_letters")


@dataclass
class CandidateProfile:
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    resume_path: str = ""
    cover_letter_template_path: str = ""
    target_titles: str = ""
    target_locations: str = ""
    min_salary: str = ""
    work_authorization: str = ""
    notes: str = ""


def default_profile() -> CandidateProfile:
    settings = get_settings()
    return CandidateProfile(
        name=settings.candidate_name,
        email=settings.candidate_email,
        phone=settings.candidate_phone,
        location=settings.candidate_location,
        resume_path=settings.resume_path,
        cover_letter_template_path=settings.cover_letter_template_path,
        target_titles=settings.target_titles,
        target_locations=settings.target_locations,
        min_salary=settings.min_salary,
        work_authorization=settings.work_authorization,
    )


def load_profile(path: Path = PROFILE_PATH) -> CandidateProfile:
    if not path.exists():
        return default_profile()

    data = json.loads(path.read_text(encoding="utf-8"))
    profile = default_profile()
    for key, value in data.items():
        if hasattr(profile, key):
            setattr(profile, key, str(value))
    return profile


def save_profile(profile: CandidateProfile, path: Path = PROFILE_PATH) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(asdict(profile), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return path


def copy_profile_file(source: str, destination_dir: Path) -> Path:
    source_path = Path(source).expanduser()
    if not source_path.exists():
        msg = f"File does not exist: {source_path}"
        raise FileNotFoundError(msg)

    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / source_path.name
    if source_path.resolve() != destination.resolve():
        shutil.copy2(source_path, destination)
    return destination


def copy_resume(source: str) -> Path:
    return copy_profile_file(source, RESUME_DIR)


def copy_cover_letter_template(source: str) -> Path:
    return copy_profile_file(source, COVER_LETTER_DIR)
