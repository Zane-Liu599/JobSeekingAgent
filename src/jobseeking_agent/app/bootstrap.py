from jobseeking_agent.db import init_db
from jobseeking_agent.utils.file_manager import ensure_local_directories


def bootstrap_app() -> None:
    ensure_local_directories()
    init_db()
