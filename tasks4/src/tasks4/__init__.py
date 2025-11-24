"""Minimal tasks4 package providing a tiny Task model, JSON repository, and CLI helpers.

This module exposes a small API so `tasks4` can be imported for quick tests.
"""

from .models import Task
from .repository import JsonRepository
from .cli import create_task, list_tasks, search_tasks, format_tasks
from .status import ALLOWED_STATUSES, is_valid_status
from .cli_typer import main as typer_main

__all__ = [
	"Task",
	"JsonRepository",
	"create_task",
	"list_tasks",
	"search_tasks",
	"format_tasks",
	"main",
	"ALLOWED_STATUSES",
	"is_valid_status",
]

# Package entrypoint used by `uv run tasks4` (and pyproject script mapping).
def main(argv=None):
	return typer_main(argv)
