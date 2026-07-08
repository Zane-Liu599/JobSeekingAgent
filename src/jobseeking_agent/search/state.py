import json
from pathlib import Path

from jobseeking_agent.search.keyword_search import SearchQuery

SEARCH_STATE_PATH = Path("data/search_state.json")


def search_state_key(query: SearchQuery) -> str:
    return "|".join(
        [
            query.platform.strip().lower(),
            " ".join(query.keywords.lower().split()),
            " ".join(query.location.lower().split()),
        ]
    )


def load_search_state(path: Path = SEARCH_STATE_PATH) -> dict[str, int]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return {str(key): int(value) for key, value in data.items()}


def save_search_state(state: dict[str, int], path: Path = SEARCH_STATE_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")


def next_search_page(query: SearchQuery, path: Path = SEARCH_STATE_PATH) -> int:
    state = load_search_state(path)
    return max(1, state.get(search_state_key(query), 1))


def advance_search_page(query: SearchQuery, path: Path = SEARCH_STATE_PATH) -> int:
    state = load_search_state(path)
    key = search_state_key(query)
    next_page = max(1, state.get(key, 1)) + 1
    state[key] = next_page
    save_search_state(state, path)
    return next_page
