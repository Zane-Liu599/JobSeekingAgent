VALID_STATUSES = {
    "found",
    "draft",
    "reviewing",
    "submitted",
    "interviewing",
    "offer",
    "rejected",
    "closed",
}


def is_valid_status(status: str) -> bool:
    return status in VALID_STATUSES
