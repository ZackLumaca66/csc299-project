from typing import Optional, List
import argparse
import json
from .models import Task
from .repository import JsonRepository


def _next_id(repo: JsonRepository) -> int:
    items = repo.list()
    if not items:
        return 1
    return max(t.id for t in items) + 1


def create_task(title: str, description: Optional[str] = "", status: str = "todo", repo_path: Optional[str] = None) -> Task:
    repo = JsonRepository(path=repo_path) if repo_path else JsonRepository()
    new_id = _next_id(repo)
    task = Task(id=new_id, title=title, description=description, status=status)
    repo.add(task)
    return task


def list_tasks(repo_path: Optional[str] = None) -> List[Task]:
    repo = JsonRepository(path=repo_path) if repo_path else JsonRepository()
    return repo.list()


def search_tasks(query: str, repo_path: Optional[str] = None) -> List[Task]:
    q = query.lower().strip()
    if not q:
        return []
    return [t for t in list_tasks(repo_path) if q in t.title.lower() or q in (t.description or "").lower()]


def format_tasks(tasks: List[Task], json_output: bool = False) -> str:
    if json_output:
        return json.dumps([t.to_dict() for t in tasks], indent=2)
    return "\n".join(f"#{t.id} [{t.status}] {t.title} - {t.description}" for t in tasks)


def main():  # console script entrypoint
    parser = argparse.ArgumentParser(prog="tasks4", description="Minimal tasks4 CLI")
    parser.add_argument("command", choices=["create", "list", "search"], help="Command to run")
    parser.add_argument("--title", help="Title for create")
    parser.add_argument("--description", help="Description for create", default="")
    parser.add_argument("--status", help="Status for create", default="todo")
    parser.add_argument("--query", help="Search query")
    parser.add_argument("--repo", help="Path to repo JSON file")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    if args.command == "create":
        if not args.title:
            parser.error("--title required for create")
        task = create_task(args.title, args.description, args.status, repo_path=args.repo)
        print(format_tasks([task], json_output=args.json))
    elif args.command == "list":
        tasks = list_tasks(args.repo)
        print(format_tasks(tasks, json_output=args.json))
    elif args.command == "search":
        if not args.query:
            parser.error("--query required for search")
        tasks = search_tasks(args.query, args.repo)
        print(format_tasks(tasks, json_output=args.json))


if __name__ == "__main__":
    main()
