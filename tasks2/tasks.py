#!/usr/bin/env python3
import argparse
import json
import os
from typing import List, Dict, Any

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)
DATA_FILE = os.path.join(DATA_DIR, "tasks.json")


def load_tasks() -> List[Dict[str, Any]]:
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_tasks(tasks: List[Dict[str, Any]]):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2)


def add_task(title: str, notes: str = "", tags: str = "", due: str = ""):
    tasks = load_tasks()
    next_id = max((t["id"] for t in tasks), default=0) + 1
    task = {
        "id": next_id,
        "title": title,
        "notes": notes,
        "tags": [t.strip() for t in tags.split(",")] if tags else [],
        "due": due,
        "done": False,
    }
    tasks.append(task)
    save_tasks(tasks)
    print(f"Added task id={next_id}")


def list_tasks():
    tasks = load_tasks()
    if not tasks:
        print("No tasks.")
        return
    for t in tasks:
        print(f'{t["id"]}: {"[x]" if t.get("done") else "[ ]"} {t["title"]} (tags: {", ".join(t.get("tags", []))})')


def search_tasks(q: str):
    tasks = load_tasks()
    q_lower = q.lower()
    results = [t for t in tasks if q_lower in t.get("title", "").lower() or q_lower in t.get("notes", "").lower()]
    if not results:
        print("No matches.")
        return
    for t in results:
        print(f'{t["id"]}: {"[x]" if t.get("done") else "[ ]"} {t["title"]}')


def mark_done(task_id: int):
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            t["done"] = True
            save_tasks(tasks)
            print(f"Marked {task_id} done.")
            return
    print("Task not found.")


def main():
    parser = argparse.ArgumentParser(prog="tasks2")
    sub = parser.add_subparsers(dest="cmd")
    p_add = sub.add_parser("add")
    p_add.add_argument("title")
    p_add.add_argument("--notes", default="")
    p_add.add_argument("--tags", default="")
    p_add.add_argument("--due", default="")

    p_list = sub.add_parser("list")
    p_search = sub.add_parser("search")
    p_search.add_argument("q")
    p_done = sub.add_parser("done")
    p_done.add_argument("id", type=int)

    args = parser.parse_args()
    if args.cmd == "add":
        add_task(args.title, args.notes, args.tags, args.due)
    elif args.cmd == "list":
        list_tasks()
    elif args.cmd == "search":
        search_tasks(args.q)
    elif args.cmd == "done":
        mark_done(args.id)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
