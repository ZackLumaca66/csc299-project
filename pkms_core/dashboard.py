from __future__ import annotations
from typing import List
from .models import Task, Document
from .agent import Agent
import os

def build_plain(tasks: List[Task], docs: List[Document], agent: Agent) -> str:
    lines = []
    lines.append("=== DASHBOARD ===")
    lines.append("Tasks:")
    for i, t in enumerate(tasks, start=1):
        lines.append(f" {i}. [{'x' if t.completed else ' '}] {t.text}")
        for d in getattr(t, 'details', [])[:10]:
            lines.append(f"    - {d}")
    # notes summary (best-effort)
    try:
        from .storage import list_notes
        notes = list_notes('json', os.getcwd())
        if notes:
            recent = '; '.join([n.text.replace('\n',' ')[:60] for n in notes[-2:]])
            lines.append(f"Notes: {len(notes)} (recent: {recent})")
        else:
            lines.append("Notes: 0")
    except Exception:
        pass
    return "\n".join(lines)

def show_dashboard(tasks: List[Task], docs: List[Document], agent: Agent, tasks_only: bool = False) -> None:
    try:
        from rich.table import Table
        from rich.console import Console
        console = Console()
        task_table = Table(title="Tasks", show_header=True, header_style="bold magenta")
        task_table.add_column("#", width=4)
        task_table.add_column("Done", width=4)
        task_table.add_column("Text")
        for i, t in enumerate(tasks, start=1):
            if tasks_only and i > 1000:
                break
            task_table.add_row(str(i), '✔' if t.completed else '', t.text)
            # include up to 3 detail bullets per task as a simple inline note
            details = getattr(t, 'details', [])
            if details:
                for d in details[:3]:
                    console.print(f"   • {d}")
        console.print(task_table)
        # Notes summary (best-effort using JSON backend in repo root)
        try:
            from .storage import list_notes
            notes = list_notes('json', os.getcwd())
            if notes:
                recent = '; '.join([n.text.replace('\n',' ')[:60] for n in notes[-2:]])
                console.print(f"Notes: {len(notes)} (recent: {recent})")
            else:
                console.print("Notes: 0")
        except Exception:
            pass
        return
    except Exception:
        print(build_plain(tasks, docs, agent))

__all__ = ["show_dashboard"]