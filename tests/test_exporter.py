from pathlib import Path

from openpyxl import load_workbook

from jobseeking_agent.database.models import Job
from jobseeking_agent.utils.exporter import export_jobs_to_xlsx


def test_export_jobs_to_xlsx(tmp_path: Path) -> None:
    path = export_jobs_to_xlsx(
        [
            Job(
                id=7,
                title="Backend Engineer",
                company="Example Company",
                location="Sydney",
                employment_type="Full-time",
                salary="$120k - $150k",
                platform="seek",
                status="found",
            )
        ],
        tmp_path / "jobs.xlsx",
    )

    workbook = load_workbook(path)
    sheet = workbook["Jobs"]

    assert sheet["A1"].value == "ID"
    assert sheet["B2"].value == "Backend Engineer"
    assert sheet["C2"].value == "Example Company"
    assert sheet["E2"].value == "Full-time"
    assert sheet["F2"].value == "$120k - $150k"
