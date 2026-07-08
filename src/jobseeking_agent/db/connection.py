import sqlite3
from pathlib import Path

from jobseeking_agent.config import get_settings


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
