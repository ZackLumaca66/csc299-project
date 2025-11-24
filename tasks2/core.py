from dataclasses import dataclass, field
from datetime import datetime
try:
    UTC = datetime.UTC
except AttributeError:
    from datetime import timezone as _tz
    UTC = _tz.utc
from typing import List

@dataclass
class Task:
    title: str
    description: str = ""
    done: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def mark_done(self):
        self.done = True

    def __repr__(self):
        status = "\u2713" if self.done else "\u2717"
        return f"<Task {self.title!r} {status}>"

class TaskManager:
    def __init__(self):
        self._tasks: List[Task] = []

    def add(self, title: str, description: str = "") -> Task:
        t = Task(title=title, description=description)
        self._tasks.append(t)
        return t

    def list(self) -> List[Task]:
        return list(self._tasks)

    def complete(self, title: str) -> bool:
        for t in self._tasks:
            if t.title == title:
                t.mark_done()
                return True
        return False

    def pending(self) -> List[Task]:
        return [t for t in self._tasks if not t.done]

    def completed(self) -> List[Task]:
        return [t for t in self._tasks if t.done]