from dataclasses import dataclass


@dataclass(frozen=True)
class SearchQuery:
    keywords: str
    location: str = ""
    platform: str = "manual"


def build_search_query(keywords: str, location: str = "", platform: str = "manual") -> SearchQuery:
    return SearchQuery(
        keywords=" ".join(keywords.split()),
        location=" ".join(location.split()),
        platform=platform.lower().strip() or "manual",
    )
