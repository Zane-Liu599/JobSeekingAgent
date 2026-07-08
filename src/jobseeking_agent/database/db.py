from jobseeking_agent.db.connection import connect, database_path
from jobseeking_agent.db.repository import (
    delete_jobs,
    ensure_job_columns,
    get_job,
    init_db,
    job_status_counts,
    list_jobs,
    reset_job_sequence_if_empty,
    save_job,
    update_job_status,
)

__all__ = [
    "connect",
    "database_path",
    "delete_jobs",
    "ensure_job_columns",
    "get_job",
    "init_db",
    "job_status_counts",
    "list_jobs",
    "reset_job_sequence_if_empty",
    "save_job",
    "update_job_status",
]
