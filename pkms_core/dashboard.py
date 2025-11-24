from __future__ import annotations
from typing import List
from .models import Task, Document
from .agent import Agent

def build_plain(tasks: List[Task], docs: List[Document], agent: Agent) -> str:
    lines = []
    lines.append("=== DASHBOARD ===")
    lines.append("Tasks:")
    for t in tasks[:10]:
        lines.append(f" [{'x' if t.completed else ' '}] {t.id}: {t.text}")
    if len(tasks) > 10:
        lines.append(f" ... ({len(tasks)-10} more)")
    lines.append("Documents:")
    for d in docs[:5]:
        lines.append(f" {d.id}: {d.title} (tags: {', '.join(d.tags)})")
    if len(docs) > 5:
        lines.append(f" ... ({len(docs)-5} more)")
    advice = agent.productivity_advice(tasks, docs)
    lines.append("Advice:")
    lines.extend(advice)
    suggestions = agent.suggest_tasks_from_documents(docs)[:5]
    if suggestions:
        lines.append("Suggestions:")
        for s in suggestions:
            lines.append(f" - {s}")
    return "\n".join(lines)

def show_dashboard(tasks: List[Task], docs: List[Document], agent: Agent) -> None:
    try:
        from rich.table import Table
        from rich.panel import Panel
        from rich.console import Console
        console = Console()
        task_table = Table(title="Tasks", show_header=True, header_style="bold magenta")
        task_table.add_column("ID", width=4)
        task_table.add_column("Done", width=4)
        task_table.add_column("Text")
        for t in tasks[:20]:
            task_table.add_row(str(t.id), '✔' if t.completed else '', t.text)
        doc_table = Table(title="Documents", show_header=True, header_style="bold cyan")
        doc_table.add_column("ID", width=4)
        doc_table.add_column("Title")
        doc_table.add_column("Tags")
        for d in docs[:10]:
            doc_table.add_row(str(d.id), d.title, ', '.join(d.tags))
        advice_lines = agent.productivity_advice(tasks, docs)
        advice_panel = Panel("\n".join(advice_lines), title="Advice", border_style="green")
        suggestions = agent.suggest_tasks_from_documents(docs)[:8]
        sugg_panel = Panel("\n".join(f"- {s}" for s in suggestions) or "(none)", title="Suggestions", border_style="yellow")
        console.print(task_table)
        console.print(doc_table)
        console.print(advice_panel)
        console.print(sugg_panel)
    except Exception:
        print(build_plain(tasks, docs, agent))

__all__ = ["show_dashboard"]