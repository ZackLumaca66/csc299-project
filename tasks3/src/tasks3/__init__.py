import json
import os
import sys
from typing import List, Dict, Any


def inc(n: int) -> int:
    return n + 1


# Simple wrapper to reuse tasks2-like JSON data if present.
DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "tasks2", "data", "tasks.json")


def list_tasks() -> List[Dict[str, Any]]:
    path = os.path.abspath(DATA_FILE)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main(argv=None):
    argv = argv or sys.argv[1:]
    if not argv or argv[0] in ("-h", "--help"):
        print("tasks3: use 'list' to show tasks or 'inc <n>' to test inc().")
        return 0
    if argv[0] == "list":
        tasks = list_tasks()
        if not tasks:
            print("No tasks from tasks2 data")
            return 0
        for t in tasks:
            print(f'{t.get("id")}: {t.get("title")}')
        return 0
    if argv[0] == "inc" and len(argv) > 1:
        try:
            n = int(argv[1])
        except ValueError:
            print("invalid integer")
            return 2
        print(inc(n))
        return 0
    print("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
