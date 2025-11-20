"""Allowed task statuses and validation helpers for tasks4."""

ALLOWED_STATUSES = ("todo", "in-progress", "done")

def is_valid_status(value: str) -> bool:
    return isinstance(value, str) and value in ALLOWED_STATUSES
