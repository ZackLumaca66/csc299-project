"""Storage abstraction for tasks (initial version).

Provides two backends:
- JsonTaskStore (existing behavior)
- SqliteTaskStore (new durable backend)

The TaskManager will accept a `store` instance; default remains JSON so
existing usage and tests keep working.
"""
from __future__ import annotations

import json
import os
import sqlite3
from dataclasses import asdict
from typing import List, Optional

from dataclasses import dataclass


@dataclass
class Task:  # lightweight duplication to decouple circular import (fields must match core.Task)
    id: int
    text: str
    created: str
    completed: bool = False


class TaskStore:
    """Interface for task persistence backends."""

    def load(self) -> List[Task]:  # pragma: no cover - interface
        raise NotImplementedError

    def save_all(self, tasks: List[Task]) -> None:  # pragma: no cover
        raise NotImplementedError

    def add(self, task: Task) -> None:  # pragma: no cover
        raise NotImplementedError

    def update(self, task: Task) -> None:  # pragma: no cover
        raise NotImplementedError

    def delete(self, task_id: int) -> bool:  # pragma: no cover
        raise NotImplementedError


class JsonTaskStore(TaskStore):
    def __init__(self, path: str):
        self.path = path

    def load(self) -> List[Task]:
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                return [Task(**t) for t in data]
            except Exception:
                return []
        return []

    def save_all(self, tasks: List[Task]) -> None:
        with open(self.path, "w", encoding="utf-8") as fh:
            json.dump([asdict(t) for t in tasks], fh, indent=2)

    def add(self, task: Task) -> None:
        tasks = self.load()
        tasks.append(task)
        self.save_all(tasks)

    def update(self, task: Task) -> None:
        tasks = self.load()
        for i, t in enumerate(tasks):
            if t.id == task.id:
                tasks[i] = task
                break
        self.save_all(tasks)

    def delete(self, task_id: int) -> bool:
        tasks = self.load()
        for i, t in enumerate(tasks):
            if t.id == task_id:
                del tasks[i]
                self.save_all(tasks)
                return True
        return False


class SqliteTaskStore(TaskStore):
    def __init__(self, path: str):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self._ensure_schema()

    def _conn(self):
        return sqlite3.connect(self.path)

    def _ensure_schema(self):
        with self._conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                  id INTEGER PRIMARY KEY,
                  text TEXT NOT NULL,
                  created TEXT NOT NULL,
                  completed INTEGER NOT NULL
                )
                """
            )

    def load(self) -> List[Task]:
        with self._conn() as conn:
            rows = conn.execute("SELECT id, text, created, completed FROM tasks ORDER BY id ASC").fetchall()
        return [Task(id=r[0], text=r[1], created=r[2], completed=bool(r[3])) for r in rows]

    def save_all(self, tasks: List[Task]) -> None:
        with self._conn() as conn:
            conn.execute("DELETE FROM tasks")
            for t in tasks:
                conn.execute(
                    "INSERT INTO tasks(id, text, created, completed) VALUES(?,?,?,?)",
                    (t.id, t.text, t.created, int(t.completed)),
                )

    def add(self, task: Task) -> None:
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO tasks(id, text, created, completed) VALUES(?,?,?,?)",
                (task.id, task.text, task.created, int(task.completed)),
            )

    def update(self, task: Task) -> None:
        with self._conn() as conn:
            conn.execute(
                "UPDATE tasks SET text=?, created=?, completed=? WHERE id=?",
                (task.text, task.created, int(task.completed), task.id),
            )

    def delete(self, task_id: int) -> bool:
        with self._conn() as conn:
            cur = conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
            return cur.rowcount > 0


def make_store(kind: str, base_dir: str) -> TaskStore:
    """Factory for stores. kind: 'json' | 'sqlite'"""
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    if kind == "sqlite":
        return SqliteTaskStore(os.path.join(data_dir, "tasks.db"))
    return JsonTaskStore(os.path.join(data_dir, "tasks.json"))
