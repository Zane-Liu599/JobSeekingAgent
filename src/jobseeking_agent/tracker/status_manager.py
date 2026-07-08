VALID_STATUSES = {
    "found",
    "saved",
    "ignored",
    "ai_applying",
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
