from __future__ import annotations
from typing import List, Any

def map_display_index(items: List[Any], display_index: int):
    """Map a 1-based display index to an item's internal id.

    Items are expected to have an `id` attribute.
    Raises IndexError if out of range.
    """
    if display_index < 1 or display_index > len(items):
        raise IndexError("Display index out of range")
    return items[display_index - 1].id


def truncate(text: str, length: int = 120) -> str:
    if text is None:
        return ""
    return text if len(text) <= length else text[: length - 3] + "..."
