import sqlite3
from collections.abc import Iterable
from pathlib import Path

from jobseeking_agent.db.connection import connect, database_path
from jobseeking_agent.db.models import Company, Job, utc_now_iso
from jobseeking_agent.db.schema import SCHEMA
from jobseeking_agent.utils.job_urls import canonical_job_url


def ensure_job_columns(connection: sqlite3.Connection) -> None:
    existing_columns = {
        row["name"] for row in connection.execute("PRAGMA table_info(jobs)").fetchall()
    }
    migrations = {
        "employment_type": "ALTER TABLE jobs ADD COLUMN employment_type TEXT NOT NULL DEFAULT ''",
        "salary": "ALTER TABLE jobs ADD COLUMN salary TEXT NOT NULL DEFAULT ''",
        "official_apply_url": (
            "ALTER TABLE jobs ADD COLUMN official_apply_url TEXT NOT NULL DEFAULT ''"
        ),
    }
    for column, statement in migrations.items():
        if column not in existing_columns:
            connection.execute(statement)


def ensure_company_table(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            normalized_name TEXT NOT NULL,
            website_url TEXT NOT NULL DEFAULT '',
            careers_url TEXT NOT NULL DEFAULT '',
            ats_provider TEXT NOT NULL DEFAULT '',
            source TEXT NOT NULL DEFAULT 'manual',
            last_scanned_at TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            UNIQUE(normalized_name)
        )
        """
    )


def reset_job_sequence_if_empty(connection: sqlite3.Connection) -> None:
    row = connection.execute("SELECT COUNT(*) AS count FROM jobs").fetchone()
    if int(row["count"]) == 0:
        connection.execute("DELETE FROM sqlite_sequence WHERE name = 'jobs'")


def init_db(database_url: str | None = None) -> Path:
    path = database_path(database_url)
    with connect(database_url) as connection:
        connection.executescript(SCHEMA)
        ensure_job_columns(connection)
        ensure_company_table(connection)
    return path


def normalize_company_name(name: str) -> str:
    return " ".join(name.strip().lower().split())


def save_company(company: Company, database_url: str | None = None) -> int:
    normalized_name = normalize_company_name(company.name)
    created_at = company.created_at or utc_now_iso()
    if not normalized_name:
        return 0

    with connect(database_url) as connection:
        cursor = connection.execute(
            """
            INSERT INTO companies (
                name, normalized_name, website_url, careers_url, ats_provider,
                source, last_scanned_at, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(normalized_name)
            DO UPDATE SET
                name = excluded.name,
                website_url = COALESCE(NULLIF(excluded.website_url, ''), companies.website_url),
                careers_url = COALESCE(NULLIF(excluded.careers_url, ''), companies.careers_url),
                ats_provider = COALESCE(NULLIF(excluded.ats_provider, ''), companies.ats_provider),
                source = COALESCE(NULLIF(excluded.source, ''), companies.source),
                last_scanned_at = COALESCE(
                    NULLIF(excluded.last_scanned_at, ''),
                    companies.last_scanned_at
                )
            """,
            (
                company.name.strip(),
                normalized_name,
                company.website_url,
                company.careers_url,
                company.ats_provider,
                company.source,
                company.last_scanned_at,
                created_at,
            ),
        )
        if cursor.lastrowid:
            row_id = int(cursor.lastrowid)
        else:
            row = connection.execute(
                "SELECT id FROM companies WHERE normalized_name = ?",
                (normalized_name,),
            ).fetchone()
            row_id = int(row["id"]) if row else 0
    return row_id


def list_companies(database_url: str | None = None, limit: int = 100) -> list[Company]:
    with connect(database_url) as connection:
        rows = connection.execute(
            """
            SELECT id, name, website_url, careers_url, ats_provider, source,
                   last_scanned_at, created_at
            FROM companies
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [company_from_row(row) for row in rows]


def get_company_by_name(name: str, database_url: str | None = None) -> Company | None:
    with connect(database_url) as connection:
        row = connection.execute(
            """
            SELECT id, name, website_url, careers_url, ats_provider, source,
                   last_scanned_at, created_at
            FROM companies
            WHERE normalized_name = ?
            """,
            (normalize_company_name(name),),
        ).fetchone()
    return company_from_row(row) if row else None


def update_company_scan_time(name: str, database_url: str | None = None) -> bool:
    with connect(database_url) as connection:
        cursor = connection.execute(
            """
            UPDATE companies
            SET last_scanned_at = ?
            WHERE normalized_name = ?
            """,
            (utc_now_iso(), normalize_company_name(name)),
        )
    return cursor.rowcount > 0


def save_job(job: Job, database_url: str | None = None) -> int:
    created_at = job.created_at or utc_now_iso()
    job_url = canonical_job_url(job.platform, job.job_url) if job.job_url else ""
    with connect(database_url) as connection:
        cursor = connection.execute(
            """
            INSERT INTO jobs (
                title, company, location, employment_type, salary, platform, job_url,
                official_apply_url, description, status, match_score, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(platform, job_url) WHERE job_url != ''
            DO UPDATE SET
                title = excluded.title,
                company = excluded.company,
                location = excluded.location,
                employment_type = excluded.employment_type,
                salary = excluded.salary,
                official_apply_url = COALESCE(
                    NULLIF(excluded.official_apply_url, ''),
                    jobs.official_apply_url
                ),
                description = excluded.description,
                status = excluded.status,
                match_score = excluded.match_score
            """,
            (
                job.title,
                job.company,
                job.location,
                job.employment_type,
                job.salary,
                job.platform,
                job_url,
                job.official_apply_url,
                job.description,
                job.status,
                job.match_score,
                created_at,
            ),
        )
        if not job_url and cursor.lastrowid:
            return int(cursor.lastrowid)

        row = connection.execute(
            "SELECT id FROM jobs WHERE platform = ? AND job_url = ?",
            (job.platform, job_url),
        ).fetchone()
        if row is not None:
            return int(row["id"])
        return int(cursor.lastrowid)


def list_jobs(
    database_url: str | None = None,
    limit: int = 50,
    official_only: bool = False,
) -> list[Job]:
    where_clause = "WHERE official_apply_url != ''" if official_only else ""
    with connect(database_url) as connection:
        rows: Iterable[sqlite3.Row] = connection.execute(
            f"""
            SELECT id, title, company, location, platform, job_url, official_apply_url, description,
                   employment_type, salary, status, match_score, created_at
            FROM jobs
            {where_clause}
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [job_from_row(row) for row in rows]


def search_saved_jobs(
    keywords: str,
    location: str = "",
    platform: str = "",
    database_url: str | None = None,
    limit: int = 50,
    official_only: bool = False,
) -> list[Job]:
    keyword_parts = [part.strip().lower() for part in keywords.split() if part.strip()]
    conditions: list[str] = []
    parameters: list[str | int] = []

    if official_only:
        conditions.append("official_apply_url != ''")

    for part in keyword_parts:
        conditions.append(
            "(LOWER(title) LIKE ? OR LOWER(company) LIKE ? OR LOWER(description) LIKE ?)"
        )
        pattern = f"%{part}%"
        parameters.extend([pattern, pattern, pattern])

    if location.strip():
        conditions.append("LOWER(location) LIKE ?")
        parameters.append(f"%{location.strip().lower()}%")

    if platform.strip():
        conditions.append("LOWER(platform) = ?")
        parameters.append(platform.strip().lower())

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    parameters.append(limit)

    with connect(database_url) as connection:
        rows: Iterable[sqlite3.Row] = connection.execute(
            f"""
            SELECT id, title, company, location, platform, job_url, official_apply_url, description,
                   employment_type, salary, status, match_score, created_at
            FROM jobs
            {where_clause}
            ORDER BY id DESC
            LIMIT ?
            """,
            parameters,
        ).fetchall()

    return [job_from_row(row) for row in rows]


def get_job(job_id: int, database_url: str | None = None) -> Job | None:
    with connect(database_url) as connection:
        row = connection.execute(
            """
            SELECT id, title, company, location, platform, job_url, official_apply_url, description,
                   employment_type, salary, status, match_score, created_at
            FROM jobs
            WHERE id = ?
            """,
            (job_id,),
        ).fetchone()

    if row is None:
        return None
    return job_from_row(row)


def update_job_status(job_id: int, status: str, database_url: str | None = None) -> bool:
    with connect(database_url) as connection:
        cursor = connection.execute(
            "UPDATE jobs SET status = ? WHERE id = ?",
            (status, job_id),
        )
    return cursor.rowcount > 0


def update_job(job_id: int, job: Job, database_url: str | None = None) -> bool:
    job_url = canonical_job_url(job.platform, job.job_url) if job.job_url else ""
    with connect(database_url) as connection:
        cursor = connection.execute(
            """
            UPDATE jobs
            SET title = ?,
                company = ?,
                location = ?,
                employment_type = ?,
                salary = ?,
                platform = ?,
                job_url = ?,
                official_apply_url = ?,
                description = ?,
                status = ?,
                match_score = ?
            WHERE id = ?
            """,
            (
                job.title,
                job.company,
                job.location,
                job.employment_type,
                job.salary,
                job.platform,
                job_url,
                job.official_apply_url,
                job.description,
                job.status,
                job.match_score,
                job_id,
            ),
        )
    return cursor.rowcount > 0


def delete_jobs(job_ids: list[int], database_url: str | None = None) -> int:
    if not job_ids:
        return 0

    placeholders = ",".join("?" for _ in job_ids)
    with connect(database_url) as connection:
        cursor = connection.execute(
            f"DELETE FROM jobs WHERE id IN ({placeholders})",
            job_ids,
        )
        reset_job_sequence_if_empty(connection)
    return cursor.rowcount


def has_search_refresh(
    keywords: str,
    location: str,
    platform: str,
    search_date: str,
    database_url: str | None = None,
) -> bool:
    with connect(database_url) as connection:
        row = connection.execute(
            """
            SELECT id
            FROM job_search_refreshes
            WHERE keywords = ?
              AND location = ?
              AND platform = ?
              AND search_date = ?
            """,
            (
                normalize_search_value(keywords),
                normalize_search_value(location),
                normalize_search_value(platform),
                search_date,
            ),
        ).fetchone()
    return row is not None


def mark_search_refresh(
    keywords: str,
    location: str,
    platform: str,
    search_date: str,
    database_url: str | None = None,
) -> bool:
    with connect(database_url) as connection:
        cursor = connection.execute(
            """
            INSERT OR IGNORE INTO job_search_refreshes (
                keywords, location, platform, search_date, created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                normalize_search_value(keywords),
                normalize_search_value(location),
                normalize_search_value(platform),
                search_date,
                utc_now_iso(),
            ),
        )
    return cursor.rowcount > 0


def normalize_search_value(value: str) -> str:
    return " ".join(value.strip().lower().split())


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


def job_from_row(row: sqlite3.Row) -> Job:
    return Job(
        id=row["id"],
        title=row["title"],
        company=row["company"],
        location=row["location"],
        employment_type=row["employment_type"],
        salary=row["salary"],
        platform=row["platform"],
        job_url=row["job_url"],
        official_apply_url=row["official_apply_url"],
        description=row["description"],
        status=row["status"],
        match_score=row["match_score"],
        created_at=row["created_at"],
    )


def company_from_row(row: sqlite3.Row) -> Company:
    return Company(
        id=row["id"],
        name=row["name"],
        website_url=row["website_url"],
        careers_url=row["careers_url"],
        ats_provider=row["ats_provider"],
        source=row["source"],
        last_scanned_at=row["last_scanned_at"],
        created_at=row["created_at"],
    )
