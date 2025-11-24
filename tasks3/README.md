# tasks3 — Dashboard & CLI

Quick notes for running the tasks3 CLI and Rich-based dashboard.

Run the interactive CLI:

```bash
python run_tasks3.py --cli
```

Run the Rich dashboard (MVP):

```bash
python run_tasks3.py --dashboard
```

Dependencies

Install requirements (recommended in a virtual environment):

```bash
python -m pip install -r tasks3/requirements.txt
```

Platform notes

- Windows + Git Bash (MinTTY): Git Bash's terminal is a MinTTY console and some interactive programs expect a Windows console. Use `winpty` to bridge them:

```bash
winpty python run_tasks3.py --dashboard
```

- PowerShell / cmd: run directly:

```powershell
python run_tasks3.py --dashboard
```

- macOS / Linux: run directly in your terminal:

```bash
python run_tasks3.py --dashboard
```

If you encounter invisible input characters, run `stty echo` (Git Bash / Linux / macOS) or reopen your terminal.
# tasks3 — Task manager with headless Neko

This package contains a terminal-first task manager integrated with a headless "neko" (virtual pet) that reacts when tasks are completed.

Quick start

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate   # on Windows: .venv\Scripts\activate
```

2. Run the CLI directly:

```bash
python -m tasks3_cli
```

3. Run tests:

```bash
python -m pytest tasks3/tests -q
```

Notes
- State is stored in the `data/` directory created in your current working directory. Tasks are saved to `data/tasks.json` and the neko state is saved to `data/neko.json`.
- The CLI commands include: `add`, `list`, `search`, `toggle`, `delete`, `export`, and `neko status|reset|file`.

Course layout
- This package is placed in `tasks3/src/tasks3_cli` to match the course requirements (package `tasks3`).
