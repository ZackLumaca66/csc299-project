# tasks_cli — Minimal terminal task manager

This is a minimal, terminal-first task manager intended as a fast prototype for the course project.

Features
- add, list, search, toggle (complete/uncomplete), delete, export
- JSON persistence at `data/tasks.json` by default
- simple REPL interface

Run locally

Create a virtual environment and install `pytest` (if you want to run tests):

```bash
python -m venv .venv
source .venv/bin/activate  # or `.venv\\Scripts\\activate` on Windows
pip install -r requirements.txt
```

Run the CLI:

```bash
python -m tasks_cli
```

Commands: `add <text>`, `list`, `search <query>`, `toggle <id>`, `delete <id>`, `export <path>`, `help`, `quit`

Run tests:

```bash
pytest tests
```
