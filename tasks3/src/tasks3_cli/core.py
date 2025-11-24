"""Core task manager logic for tasks3_cli (copied/adapted from tasks_cli).
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional, Callable

from .storage import TaskStore, make_store, JsonTaskStore, Task as StoreTask


@dataclass
class Task:
    id: int
    text: str
    created: str
    completed: bool = False

    def to_dict(self):
        return asdict(self)


class TaskManager:
    def __init__(self, path: Optional[str] = None, on_toggle: Optional[Callable[["Task", bool], None]] = None, store: Optional[TaskStore] = None, backend: str = "json"):
        """TaskManager optionally accepts a TaskStore.

        Args:
            path: legacy JSON path override (ignored if store provided or backend == 'sqlite').
            on_toggle: callback invoked when a task transitions to completed.
            store: explicit TaskStore instance (JSON or SQLite). If not provided, one is created.
            backend: 'json' or 'sqlite' to select default store if store not passed.
        """
        root = os.getcwd()
        data_dir = os.path.join(root, "data")
        os.makedirs(data_dir, exist_ok=True)
        if store is not None:
            self.store = store
        else:
            if backend == "json" and path:
                self.store = JsonTaskStore(path)
            else:
                self.store = make_store(backend, root)
        # Retain path for backward compatibility (JSON path if json backend)
        if isinstance(self.store, JsonTaskStore):
            self.path = self.store.path
        else:
            self.path = os.path.join(data_dir, "tasks.json")  # unused for sqlite, kept for compatibility
        self.tasks: List[Task] = []
        self._next_id = 1
        self.on_toggle = on_toggle
        self.load()

    def load(self):
        try:
            self.tasks = self.store.load()
            if self.tasks:
                self._next_id = max(t.id for t in self.tasks) + 1
            else:
                self._next_id = 1
        except Exception:
            self.tasks = []
            self._next_id = 1

    def save(self):
        try:
            self.store.save_all(self.tasks)
        except Exception:
            pass

    def add(self, text: str) -> Task:
        t = Task(id=self._next_id, text=text, created=datetime.utcnow().isoformat(), completed=False)
        self._next_id += 1
        self.tasks.append(t)
        try:
            self.store.add(t)
        except Exception:
            self.save()  # fallback bulk save
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
                try:
                    self.store.update(t)
                except Exception:
                    self.save()
                try:
                    if self.on_toggle:
                        self.on_toggle(t, t.completed)
                except Exception:
                    pass
                return t
        return None

    def set_completed(self, task_id: int, completed: bool) -> Optional[Task]:
        """Set a task to completed/uncompleted and notify hook if present."""
        for t in self.tasks:
            if t.id == task_id:
                was = t.completed
                t.completed = bool(completed)
                try:
                    self.store.update(t)
                except Exception:
                    self.save()
                # Only notify if changed to completed
                try:
                    if self.on_toggle and (not was and t.completed):
                        self.on_toggle(t, t.completed)
                except Exception:
                    pass
                return t
        return None

    def delete(self, task_id: int) -> bool:
        for i, t in enumerate(self.tasks):
            if t.id == task_id:
                del self.tasks[i]
                try:
                    if not self.store.delete(t.id):
                        self.save()
                except Exception:
                    self.save()
                return True
        return False

    def export(self, out_path: str) -> None:
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump([t.to_dict() for t in self.tasks], fh, indent=2)
