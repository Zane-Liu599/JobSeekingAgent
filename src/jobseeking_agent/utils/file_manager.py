from pathlib import Path

LOCAL_DIRECTORIES = [
    Path("data"),
    Path("data/resumes"),
    Path("data/cover_letters"),
    Path("data/exports"),
    Path("logs"),
]


def ensure_local_directories() -> list[Path]:
    for directory in LOCAL_DIRECTORIES:
        directory.mkdir(parents=True, exist_ok=True)
    return LOCAL_DIRECTORIES
