import json
import os
from typing import List
from .models import Task


class JsonRepository:
    """Very small JSON-backed repository for Task objects.

    The file defaults to a `tasks4_repo.json` file in the current working directory
    if no path is provided.
    """

    def __init__(self, path: str = None):
        self.path = path or os.path.join(os.getcwd(), "tasks4_repo.json")
        if not os.path.exists(self.path):
            self._write([])

    def _read(self) -> List[dict]:
        with open(self.path, "r", encoding="utf-8") as fh:
            try:
                return json.load(fh)
            except json.JSONDecodeError:
                return []

    def _write(self, data: List[dict]):
        with open(self.path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)

    def list(self) -> List[Task]:
        return [Task(**item) for item in self._read()]

    def add(self, task: Task) -> Task:
        items = self._read()
        items.append(task.to_dict())
        self._write(items)
        return task
