from pathlib import Path

from jobseeking_agent.ai.cover_letter_generator import generate_cover_letter
from jobseeking_agent.database.models import Job


def test_generate_cover_letter(tmp_path: Path) -> None:
    path = generate_cover_letter(
        Job(id=1, title="Backend Engineer", company="Example Company"),
        output_dir=str(tmp_path),
    )

    assert path.exists()
    assert "Backend Engineer" in path.read_text(encoding="utf-8")
