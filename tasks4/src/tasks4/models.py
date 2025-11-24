from dataclasses import dataclass, asdict, field
from typing import Optional
from datetime import datetime
try:
    # Python 3.14+ exposes timezone constants on datetime
    UTC = datetime.UTC
except AttributeError:
    from datetime import timezone as _tz
    UTC = _tz.utc
from .status import is_valid_status, ALLOWED_STATUSES


@dataclass
class Task:
    id: int
    title: str
    description: Optional[str] = ""
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    status: str = "todo"

    def to_dict(self):
        return asdict(self)

    def __post_init__(self):  # validate fields after init
        if not isinstance(self.id, int) or self.id < 1:
            raise ValueError("Task id must be a positive integer")
        if not isinstance(self.title, str) or not self.title.strip():
            raise ValueError("Task title cannot be blank")
        if not is_valid_status(self.status):
            raise ValueError(f"Invalid status '{self.status}'. Allowed: {', '.join(ALLOWED_STATUSES)}")
