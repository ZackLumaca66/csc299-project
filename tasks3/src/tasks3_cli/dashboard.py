"""Simple Rich-based dashboard for tasks3_cli (MVP).

Features:
- Table of tasks (id, status, text)
- Neko status panel on the right
- Simple command prompt for `c <id>` (complete), `t <id>` (toggle), `q` quit
"""
from __future__ import annotations

from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.layout import Layout
from rich.align import Align
import time

from .core import TaskManager
from .neko import NekoManager


def make_tasks_table(tm: TaskManager) -> Table:
    table = Table(title="Tasks", expand=True)
    table.add_column("ID", width=6, style="cyan", justify="right")
    table.add_column("Done", width=6, style="green")
    table.add_column("Text", overflow="fold")
    for t in tm.list():
        status = "x" if t.completed else " "
        table.add_row(str(t.id), status, t.text)
    return table


def make_neko_panel(neko: NekoManager, width: int = 28) -> Panel:
    # Shorten the rendered bar for dashboard
    mood = neko.get_mood()
    cat = neko.render().splitlines()
    # reuse neko.render but crop long lines
    content = "\n".join(line[:width - 2] for line in cat)
    return Panel(Align.left(content), title="Neko", width=width)


def build_layout(tm: TaskManager, neko: NekoManager, status: str = "") -> Layout:
    layout = Layout()
    layout.split_row(
        Layout(name="left"),
        Layout(name="right", size=32),
    )
    # right side: neko panel on top, status below
    layout["right"].split_column(Layout(name="neko", size=8), Layout(name="status"))
    layout["left"].update(make_tasks_table(tm))
    layout["right"]["neko"].update(make_neko_panel(neko, width=32))
    layout["right"]["status"].update(Panel(status or "", title="Status", height=3))
    return layout


def run_dashboard(path: Optional[str] = None):
    console = Console()
    neko = NekoManager()
    tm = TaskManager(on_toggle=neko.on_task_toggled)

    status = "Type 'h' for help."
    with Live(build_layout(tm, neko, status=status), console=console, refresh_per_second=4, screen=True) as live:
        while True:
            # Stop live rendering while prompting for input to avoid redraw glitches
            try:
                live.stop()
            except Exception:
                # If Live doesn't support stop/start on this version, ignore and continue
                pass
            try:
                cmd = console.input("[bold yellow]dashboard> [/]").strip()
            except (EOFError, KeyboardInterrupt):
                cmd = "q"
            try:
                live.start()
            except Exception:
                pass

            if not cmd:
                live.update(build_layout(tm, neko, status=status))
                continue

            parts = cmd.split()
            op = parts[0].lower()
            if op in ("q", "quit", "exit"):
                break
            if op in ("h", "help"):
                status = "Commands: c <id> (complete), t <id> (toggle), a <text> (add), l (list), q (quit)"
                live.update(build_layout(tm, neko, status=status))
                continue

            if op == "c" and len(parts) > 1:
                try:
                    tid = int(parts[1])
                except ValueError:
                    status = "id must be a number"
                    live.update(build_layout(tm, neko, status=status))
                    continue
                t = tm.set_completed(tid, True)
                if not t:
                    status = "not found"
                else:
                    status = f"completed: {t.id} {t.text}"
                live.update(build_layout(tm, neko, status=status))
                continue

            if op == "t" and len(parts) > 1:
                try:
                    tid = int(parts[1])
                except ValueError:
                    status = "id must be a number"
                    live.update(build_layout(tm, neko, status=status))
                    continue
                t = tm.toggle(tid)
                if not t:
                    status = "not found"
                else:
                    status = f"toggled: {t.id} {t.text}"
                live.update(build_layout(tm, neko, status=status))
                continue

            if op == "a" and len(parts) > 1:
                text = " ".join(parts[1:])
                t = tm.add(text)
                status = f"added: {t.id} {t.text}"
                live.update(build_layout(tm, neko, status=status))
                continue

            if op in ("l", "list"):
                status = "refreshed"
                live.update(build_layout(tm, neko, status=status))
                continue

            status = "unknown command. type 'h' for help"
            live.update(build_layout(tm, neko, status=status))


if __name__ == "__main__":
    run_dashboard()
