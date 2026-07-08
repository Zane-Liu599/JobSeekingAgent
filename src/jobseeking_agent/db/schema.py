SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT NOT NULL DEFAULT '',
    employment_type TEXT NOT NULL DEFAULT '',
    salary TEXT NOT NULL DEFAULT '',
    platform TEXT NOT NULL DEFAULT 'manual',
    job_url TEXT NOT NULL DEFAULT '',
    official_apply_url TEXT NOT NULL DEFAULT '',
    description TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'found',
    match_score REAL,
    created_at TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_jobs_unique_source
ON jobs(platform, job_url)
WHERE job_url != '';

CREATE TABLE IF NOT EXISTS job_search_refreshes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keywords TEXT NOT NULL,
    location TEXT NOT NULL DEFAULT '',
    platform TEXT NOT NULL DEFAULT 'seek',
    search_date TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(keywords, location, platform, search_date)
);

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
);

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
