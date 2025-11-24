"""Simple REPL CLI for the task manager.
Commands:
  add <text>
  list
  search <query>
  toggle <id>
  delete <id>
  export <path>
  help
  quit
"""
from __future__ import annotations

import shlex
from typing import List

from .core import TaskManager
from .neko import NekoManager


def print_task(t):
    status = "x" if t.completed else " "
    print(f"[{status}] {t.id}: {t.text} (created: {t.created})")


def run():
    # Initialize a small neko manager and pass its hook to TaskManager
    neko = NekoManager()
    tm = TaskManager(on_toggle=neko.on_task_toggled)
    print("tasks_cli — simple task manager (type 'help' for commands)")
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbye")
            break

        if not raw:
            continue

        parts: List[str] = shlex.split(raw)
        cmd = parts[0].lower()
        args = parts[1:]

        if cmd in ("q", "quit", "exit"):
            print("bye")
            break
        if cmd in ("h", "help"):
            print("commands: add <text> | list | search <query> | toggle <id> | delete <id> | export <path> | quit")
            continue

        if cmd == "add":
            if not args:
                print("Usage: add <task text>")
                continue
            text = " ".join(args)
            t = tm.add(text)
            print("added:")
            print_task(t)
            continue

        if cmd == "list":
            tasks = tm.list()
            if not tasks:
                print("no tasks")
            for t in tasks:
                print_task(t)
            continue

        if cmd == "search":
            if not args:
                print("Usage: search <query>")
                continue
            q = " ".join(args)
            results = tm.search(q)
            if not results:
                print("no results")
            for t in results:
                print_task(t)
            continue

        if cmd == "toggle":
            if not args:
                print("Usage: toggle <id>")
                continue
            try:
                tid = int(args[0])
            except ValueError:
                print("id must be a number")
                continue
            t = tm.toggle(tid)
            if not t:
                print("not found")
            else:
                print("toggled:")
                print_task(t)
            continue

        if cmd == "delete":
            if not args:
                print("Usage: delete <id>")
                continue
            try:
                tid = int(args[0])
            except ValueError:
                print("id must be a number")
                continue
            ok = tm.delete(tid)
            print("deleted" if ok else "not found")
            continue

        if cmd == "export":
            if not args:
                print("Usage: export <path>")
                continue
            out = args[0]
            try:
                tm.export(out)
                print(f"exported to {out}")
            except Exception as e:
                print(f"export failed: {e}")
            continue

        if cmd == "neko":
            # neko commands: neko status | neko reset | neko file
            sub = args[0] if args else "status"
            if sub == "status":
                print(neko.render())
            elif sub == "reset":
                neko.reset()
                print("neko reset")
            elif sub == "file":
                print(f"neko state file: {neko.path}")
            else:
                print("neko commands: status | reset | file")
            continue

        print(f"unknown command: {cmd}. Type 'help' for commands.")


if __name__ == "__main__":
    run()
