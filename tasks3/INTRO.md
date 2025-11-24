# tasks3 — Introduction

Quick introduction for the terminal task manager (PKMS + TMS + Neko)

Start the interactive CLI or dashboard:

```bash
# interactive CLI
python run_tasks3.py --cli

# Rich-based dashboard (MVP)
python run_tasks3.py --dashboard
```

Basic commands

- `add <text>` — create a new task
- `list` — show all tasks
- `complete <id>` — mark a task completed
- `toggle <id>` — toggle completion state (legacy command)
- `delete <id>` — delete a task
- `export <path>` — export tasks to a JSON file

Documents (PKMS)

- `doc add <title> <text> [comma-tags]` — add a document
- `doc list` — list documents
- `doc search <query>` — search documents
- `doc view <id>` — view full document

- `dashboard` — show a one-shot task dashboard with Neko status (non-interactive)

Agent / Chat

- `chat <query>` — ask the local agent about tasks or documents, or `chat summarize documents` to get a short summary.

Pet / Neko

- `neko status` — show the neko's health and mood
- `neko reset` — reset neko

Notes

- State files are placed in `data/` in the current working directory: `tasks.json`, `docs.json`, `neko.json`.
- If you run into import issues, use the launcher `run_tasks3.py` which sets the correct import path.

Dashboard requirements

- Install dependencies (recommended in a venv):

```bash
python -m pip install -r tasks3/requirements.txt
```

Then run the dashboard with `python run_tasks3.py --dashboard`.
