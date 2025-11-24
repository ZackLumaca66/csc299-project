import os
from pathlib import Path

from rich.console import Console

from tasks3_cli.core import TaskManager
from tasks3_cli.neko import NekoManager
from tasks3_cli.dashboard import make_tasks_table, make_neko_panel, build_layout


def test_dashboard_renders(tmp_path: Path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    tasks_path = str(data_dir / "tasks.json")
    neko_path = str(data_dir / "neko.json")

    tm = TaskManager(path=tasks_path)
    nm = NekoManager(path=neko_path)

    # seed some tasks
    tm.add("write tests")
    tm.add("fix bug")

    table = make_tasks_table(tm)
    panel = make_neko_panel(nm)
    layout = build_layout(tm, nm, status="smoke")

    console = Console(record=True)
    console.print(table)
    console.print(panel)
    console.print(layout)
    out = console.export_text()

    assert "Tasks" in out
    assert "Neko" in out
    assert "write tests" in out
