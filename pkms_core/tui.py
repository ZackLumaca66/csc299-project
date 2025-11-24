from __future__ import annotations
from typing import List
from rich.table import Table
from rich.console import Console
from rich.prompt import Prompt
from .models import Task

console = Console()

def _render_tasks(tasks: List[Task]):
    table = Table(title="Tasks")
    table.add_column("ID", width=4)
    table.add_column("Done", width=4)
    table.add_column("Text")
    table.add_column("Details")
    for t in tasks:
        details = "; ".join(getattr(t, 'details', [])[:3])
        table.add_row(str(t.id), '✔' if t.completed else '', t.text, details)
    console.print(table)

def run_tui(task_manager, doc_manager, agent):
    console.print("Welcome to PKMS TUI — available commands:", style="bold green")
    console.print("  add <text>               - Add a new task")
    console.print("  edit <id> <new text>     - Edit task text")
    console.print("  delete <id>              - Delete task (asks for confirmation)")
    console.print("  desc <id> <text>         - Add a bullet detail/description to task")
    console.print("  remove-detail <id> <i>   - Remove detail index i (0-based)")
    console.print("  advise                   - Show AI productivity advice for all tasks/docs")
    console.print("  exit                     - Quit TUI")
    while True:
        _render_tasks(task_manager.list())
        cmd = Prompt.ask("tui>")
        if not cmd: continue
        if cmd in {'exit','quit'}:
            break
        if cmd.startswith('add '):
            text = cmd[len('add '):].strip()
            if text:
                t = task_manager.add(text); console.print(f"added {t.id}")
            continue
        if cmd.startswith('edit '):
            try:
                rest = cmd.split(' ',2)
                tid = int(rest[1]); new = rest[2]; t = task_manager.edit(tid, new)
                console.print(f"edited {t.id}" if t else 'not found')
            except Exception:
                console.print('usage: edit <id> <new text>')
            continue
        if cmd.startswith('delete '):
            try:
                tid = int(cmd.split()[1])
                confirm = Prompt.ask(f"Confirm delete {tid}? (yes/no)")
                if confirm.lower().startswith('y'):
                    ok = task_manager.delete(tid); console.print('deleted' if ok else 'not found')
            except Exception:
                console.print('bad id')
            continue
        # 'toggle' removed from TUI commands per user request
        if cmd.startswith('desc '):
            try:
                parts = cmd.split(' ',2)
                tid = int(parts[1]); detail = parts[2]
                t = task_manager.add_detail(tid, detail); console.print('detail added' if t else 'not found')
            except Exception:
                console.print('usage: desc <id> <text>')
            continue
        if cmd.startswith('remove-detail '):
            try:
                parts = cmd.split(' ',2)
                tid = int(parts[1]); idx = int(parts[2])
                t = task_manager.remove_detail(tid, idx)
                console.print('detail removed' if t else 'not found or bad index')
            except Exception:
                console.print('usage: remove-detail <id> <index>')
            continue
        if cmd.startswith('advise'):
            for line in agent.productivity_advice(task_manager.list(), doc_manager.list()):
                console.print(line)
            continue
        console.print('unknown command')

__all__ = ['run_tui']
