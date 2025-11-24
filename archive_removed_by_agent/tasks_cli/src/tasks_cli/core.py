"""Core task manager logic: Task dataclass and TaskManager.
Stores tasks in a JSON file by default.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional, Callable


@dataclass
class Task:
    id: int
    text: str
    created: str
    completed: bool = False

    def to_dict(self):
        return asdict(self)


class TaskManager:
    def __init__(self, path: Optional[str] = None, on_toggle: Optional[Callable[["Task", bool], None]] = None):
        root = os.getcwd()
        data_dir = os.path.join(root, "data")
        os.makedirs(data_dir, exist_ok=True)
        self.path = path or os.path.join(data_dir, "tasks.json")
        self.tasks: List[Task] = []
        self._next_id = 1
        # optional callback(task, completed) invoked after toggling a task
        self.on_toggle = on_toggle
        self.load()

    def load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                self.tasks = [Task(**t) for t in data]
                if self.tasks:
                    self._next_id = max(t.id for t in self.tasks) + 1
                else:
                    self._next_id = 1
            except Exception:
                # If corrupted, start fresh but do not raise
                self.tasks = []
                self._next_id = 1
        else:
            self.tasks = []
            self._next_id = 1

    def save(self):
        with open(self.path, "w", encoding="utf-8") as fh:
            json.dump([t.to_dict() for t in self.tasks], fh, indent=2)

    def add(self, text: str) -> Task:
        t = Task(id=self._next_id, text=text, created=datetime.utcnow().isoformat(), completed=False)
        self._next_id += 1
        self.tasks.append(t)
        self.save()
        return t

    def list(self, include_completed: bool = True) -> List[Task]:
        if include_completed:
            return list(self.tasks)
        return [t for t in self.tasks if not t.completed]

    def search(self, query: str) -> List[Task]:
        q = query.lower()
        return [t for t in self.tasks if q in t.text.lower()]

    def toggle(self, task_id: int) -> Optional[Task]:
        for t in self.tasks:
            if t.id == task_id:
                t.completed = not t.completed
                self.save()
                # Notify optional hook
                try:
                    if self.on_toggle:
                        self.on_toggle(t, t.completed)
                except Exception:
                    pass
                return t
        return None

    def delete(self, task_id: int) -> bool:
        for i, t in enumerate(self.tasks):
            if t.id == task_id:
                del self.tasks[i]
                self.save()
                return True
        return False

    def export(self, out_path: str) -> None:
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump([t.to_dict() for t in self.tasks], fh, indent=2)
