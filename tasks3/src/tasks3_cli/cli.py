"""CLI for tasks3_cli — integrates TaskManager and NekoManager."""
from __future__ import annotations

import shlex
from typing import List

from .core import TaskManager
from .neko import NekoManager
from .document import DocumentManager
from .agent import AgentStub
from .dashboard import build_layout
from rich.console import Console


def print_task(t):
    status = "x" if t.completed else " "
    print(f"[{status}] {t.id}: {t.text} (created: {t.created})")


def run():
    neko = NekoManager()
    docs = DocumentManager()
    agent = AgentStub()
    tm = TaskManager(on_toggle=neko.on_task_toggled)
    print("tasks3_cli — task manager with neko (type 'help' for commands)")
    print("Type 'intro' for a short usage guide or 'help' for commands.")
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
            print("commands: add <text> | list | search <query> | toggle <id> | complete <id> | delete <id> | export <path> | doc ... | chat <query> | neko status|reset|file | dashboard | intro | quit")
            continue

        if cmd == "intro":
            print("""
Intro — Quick usage
- add <text>                Add a new task
- list                      Show all tasks
- complete <id>             Mark task <id> completed
- toggle <id>               Toggle completion
- delete <id>               Delete a task
- export <path>             Export tasks JSON to path
- doc add|list|search|view  Document (PKMS) commands
- chat <query>              Use local agent to ask about tasks/docs
- neko status               Show neko (pet) status
Type 'doc list' and 'chat summarize documents' for more examples.
""")
            continue

        if cmd == "add":
            if not args:
                print("Usage: add <task text>")
                continue
            text = " ".join(args)
            t = tm.add(text)
            print("added:")
            print_task(t)
            # Auto-show dashboard snapshot after adding a task
            console = Console()
            layout = build_layout(tm, neko, status="auto-snapshot after add")
            console.print(layout)
            continue

        if cmd == "list":
            tasks = tm.list()
            if not tasks:
                print("no tasks")
            for t in tasks:
                print_task(t)
            # Auto-show dashboard snapshot after listing tasks
            console = Console()
            layout = build_layout(tm, neko, status="auto-snapshot after list")
            console.print(layout)
            continue

        if cmd in ("dashboard", "dash", "view"):
            # Print a one-shot snapshot of the dashboard (non-interactive) so CLI stays primary
            console = Console()
            layout = build_layout(tm, neko, status="dashboard snapshot")
            console.print(layout)
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

        if cmd == "doc":
            # doc add <title> --text "..." --tags tag1,tag2 | doc list | doc search <q> | doc view <id> | doc delete <id>
            if not args:
                print("doc commands: add | list | search | view | delete")
                continue
            sub = args[0]
            if sub == "add":
                # naive parsing: doc add "Title" "text" tag1,tag2
                if len(args) < 3:
                    print("Usage: doc add <title> <text> [comma-separated-tags]")
                    continue
                title = args[1]
                text = args[2]
                tags = []
                if len(args) > 3:
                    tags = [t.strip() for t in args[3].split(",") if t.strip()]
                d = docs.add(title, text, tags)
                print(f"added doc {d.id}: {d.title}")
                continue
            if sub == "list":
                for d in docs.list():
                    print(f"{d.id}: {d.title} [tags: {', '.join(d.tags)}]")
                continue
            if sub == "search":
                if len(args) < 2:
                    print("Usage: doc search <query>")
                    continue
                q = " ".join(args[1:])
                res = docs.search(q)
                if not res:
                    print("no results")
                for d in res:
                    print(f"{d.id}: {d.title} [tags: {', '.join(d.tags)}]")
                continue
            if sub == "view":
                if len(args) < 2:
                    print("Usage: doc view <id>")
                    continue
                try:
                    did = int(args[1])
                except ValueError:
                    print("id must be a number")
                    continue
                dd = docs.get(did)
                if not dd:
                    print("not found")
                else:
                    print(f"{dd.id}: {dd.title}\n----\n{dd.text}\n----\ntags: {', '.join(dd.tags)}")
                continue
            if sub == "delete":
                if len(args) < 2:
                    print("Usage: doc delete <id>")
                    continue
                try:
                    did = int(args[1])
                except ValueError:
                    print("id must be a number")
                    continue
                ok = docs.delete(did)
                print("deleted" if ok else "not found")
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

        if cmd == "complete":
            if not args:
                print("Usage: complete <id>")
                continue
            try:
                tid = int(args[0])
            except ValueError:
                print("id must be a number")
                continue
            t = tm.set_completed(tid, True)
            if not t:
                print("not found")
            else:
                print("completed:")
                print_task(t)
            continue

        # Note: the explicit `incomplete` command was removed — use `toggle` or `complete <id>` instead.

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

        if cmd == "chat" or cmd == "agent":
            if not args:
                print("Usage: chat <question>")
                continue
            q = " ".join(args)
            resp = agent.respond(q, task_manager=tm, doc_manager=docs)
            print(resp)
            continue

        print(f"unknown command: {cmd}. Type 'help' for commands.")


if __name__ == "__main__":
    run()
