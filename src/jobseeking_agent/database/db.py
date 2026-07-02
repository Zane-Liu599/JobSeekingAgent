import sqlite3
from collections.abc import Iterable
from pathlib import Path

from jobseeking_agent.config import get_settings
from jobseeking_agent.database.models import Job, utc_now_iso

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT NOT NULL DEFAULT '',
    platform TEXT NOT NULL DEFAULT 'manual',
    job_url TEXT NOT NULL DEFAULT '',
    description TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'found',
    match_score REAL,
    created_at TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_jobs_unique_source
ON jobs(platform, job_url)
WHERE job_url != '';

CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER NOT NULL,
    resume_path TEXT NOT NULL DEFAULT '',
    cover_letter_path TEXT NOT NULL DEFAULT '',
    submitted_at TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'draft',
    notes TEXT NOT NULL DEFAULT '',
    FOREIGN KEY(job_id) REFERENCES jobs(id)
);
"""


def database_path(database_url: str | None = None) -> Path:
    url = database_url or get_settings().database_url
    if not url.startswith("sqlite:///"):
        msg = "Only sqlite:/// database URLs are supported in the local MVP."
        raise ValueError(msg)

    path = Path(url.removeprefix("sqlite:///"))
    if not path.is_absolute():
        path = Path.cwd() / path
    return path


def connect(database_url: str | None = None) -> sqlite3.Connection:
    path = database_path(database_url)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


def init_db(database_url: str | None = None) -> Path:
    path = database_path(database_url)
    with connect(database_url) as connection:
        connection.executescript(SCHEMA)
    return path


def save_job(job: Job, database_url: str | None = None) -> int:
    created_at = job.created_at or utc_now_iso()
    with connect(database_url) as connection:
        cursor = connection.execute(
            """
            INSERT INTO jobs (
                title, company, location, platform, job_url, description,
                status, match_score, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(platform, job_url) WHERE job_url != ''
            DO UPDATE SET
                title = excluded.title,
                company = excluded.company,
                location = excluded.location,
                description = excluded.description,
                status = excluded.status,
                match_score = excluded.match_score
            """,
            (
                job.title,
                job.company,
                job.location,
                job.platform,
                job.job_url,
                job.description,
                job.status,
                job.match_score,
                created_at,
            ),
        )
        if cursor.lastrowid:
            return int(cursor.lastrowid)

        row = connection.execute(
            "SELECT id FROM jobs WHERE platform = ? AND job_url = ?",
            (job.platform, job.job_url),
        ).fetchone()
        return int(row["id"])


def list_jobs(database_url: str | None = None, limit: int = 50) -> list[Job]:
    with connect(database_url) as connection:
        rows: Iterable[sqlite3.Row] = connection.execute(
            """
            SELECT id, title, company, location, platform, job_url, description,
                   status, match_score, created_at
            FROM jobs
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [
        Job(
            id=row["id"],
            title=row["title"],
            company=row["company"],
            location=row["location"],
            platform=row["platform"],
            job_url=row["job_url"],
            description=row["description"],
            status=row["status"],
            match_score=row["match_score"],
            created_at=row["created_at"],
        )
        for row in rows
    ]


def get_job(job_id: int, database_url: str | None = None) -> Job | None:
    with connect(database_url) as connection:
        row = connection.execute(
            """
            SELECT id, title, company, location, platform, job_url, description,
                   status, match_score, created_at
            FROM jobs
            WHERE id = ?
            """,
            (job_id,),
        ).fetchone()

    if row is None:
        return None

    return Job(
        id=row["id"],
        title=row["title"],
        company=row["company"],
        location=row["location"],
        platform=row["platform"],
        job_url=row["job_url"],
        description=row["description"],
        status=row["status"],
        match_score=row["match_score"],
        created_at=row["created_at"],
    )


def update_job_status(job_id: int, status: str, database_url: str | None = None) -> bool:
    with connect(database_url) as connection:
        cursor = connection.execute(
            "UPDATE jobs SET status = ? WHERE id = ?",
            (status, job_id),
        )
    return cursor.rowcount > 0


def job_status_counts(database_url: str | None = None) -> dict[str, int]:
    with connect(database_url) as connection:
        rows = connection.execute(
            """
            SELECT status, COUNT(*) AS count
            FROM jobs
            GROUP BY status
            ORDER BY status
            """
        ).fetchall()

    return {row["status"]: int(row["count"]) for row in rows}
