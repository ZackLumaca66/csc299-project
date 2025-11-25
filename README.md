[![Task-Neko tests](https://github.com/ZackLumaca66/csc299-project/actions/workflows/python-tests.yml/badge.svg)](https://github.com/ZackLumaca66/csc299-project/actions/workflows/python-tests.yml)

# PKMS Core

Lean task + personal knowledge management CLI with selectable storage (JSON or SQLite), a focused dashboard,
and a small chat/agent layer that can provide concise productivity advice.

## Features
- Tasks: add, list (dashboard), edit, describe (add detail), search, delete
- Storage: `--backend json` or `--backend sqlite` (select per-command or default in API)
- Focused dashboard: the CLI `list` / `dashboard` shows tasks only (no docs/suggestions by default)
- Chat/Agent: `chat` (interactive or single-message advise), `chat-history`, and `advise` for compact productivity tips
- Optional LLM adapter: enable via `OPENAI_API_KEY` or use `setup-llm` to store the key in your OS keyring
- Tests: see `tests/` and `tasks3/tests/` for coverage of core behaviors

pkms add "Plan agent architecture" --backend sqlite
## Quick Start

1) Create and activate a virtual environment (optional but recommended)

Bash (Git Bash / WSL / macOS):
```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

PowerShell (Windows):
```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -e .
```

2) Use the CLI (module mode shown; the repo includes `pkms.bat` for Windows)

Examples:
```bash
# List tasks (dashboard - tasks only)
python -m pkms_core.cli list

# Add a task (use the list-number in other commands; list numbers are 1-based)
python -m pkms_core.cli add "Write README"

# Edit a task (use the list-number shown by `list`)
python -m pkms_core.cli edit 1 "Updated text"

# Add a short detail/bullet to task 1
python -m pkms_core.cli describe 1 "Clarify scope and acceptance criteria"

# Search tasks
python -m pkms_core.cli search "readme"

# Delete a task
python -m pkms_core.cli delete 2

# Start interactive chat
python -m pkms_core.cli chat --interactive

# Single-message advise (non-interactive; only advise commands allowed)
python -m pkms_core.cli chat advise
python -m pkms_core.cli chat "advise selected 1"

# Show chat history
python -m pkms_core.cli chat-history

# Show compact productivity advice (heuristic + short doc-derived summary)
python -m pkms_core.cli advise

# Wipe all app data (destructive — removes app_data, data_pkms, demo_data, tasks/db/json files)
python -m pkms_core.cli reset --yes
```

Note: documents are used internally by the agent; document CLI export/import commands were removed to keep the CLI focused and terminal-first.

## Demo script

Run a small demo of the chat/agent (uses mock LLM when no API key found):

```bash
python scripts/demo_pkms_chat.py
```

This prints agent productivity advice, document-derived suggestion counts, and sample summaries.

## Notes (PKMS)

This project also supports a lightweight Notes model integrated into the CLI and chat. Notes are stored alongside tasks and can be persisted using either JSON or SQLite backends.

Commands (examples):

```bash
# Add a note
python -m pkms_core.cli notes add "Outline architecture for agent"

# List notes (1-based indices)
python -m pkms_core.cli notes list

# Add a detail bullet to note 1
python -m pkms_core.cli notes describe 1 "Include migration notes"

# Search notes
python -m pkms_core.cli notes search architecture

# Delete note by list-number
python -m pkms_core.cli notes delete 1

# Start chat with a note attached (use list-number)
python -m pkms_core.cli chat --note-id 1 advise
```

Notes are shown in the dashboard summary (recent snippets) and can be selected inside the interactive chat using `/select-note <n>` or `select note <n>` commands.

pkms list
pkms delete <id>
pkms chat <message>
pkms chat-history
## Commands (current)

The CLI exposes the following top-level commands. Most commands accept `--backend json|sqlite` where applicable.

- `add <text>` — create a new task
- `edit <n> <text>` — edit task by list-number (1-based)
- `describe <n> <detail>` — add a detail / bullet to the listed task
- `list` — show the tasks-only dashboard (same as `dashboard` without --interactive)
- `dashboard [--interactive]` — show dashboard; `--interactive` launches the TUI when available
- `search <query>` — find tasks matching the query
- `delete <n>` — delete task by list-number
- `chat [message] [--task-id <n>] [--interactive]` — chat with the agent; in single-message mode only `advise` commands are accepted
- `chat-history` — show saved chat history
- `advise` — print compact productivity advice summary
- `setup-llm [--show|--remove]` — store or remove OpenAI API key in OS keyring (recommended) or use env var (see below)
- `reset [--yes]` — destructive: removes app data, legacy stores, chat history, and clears in-process tasks
- `home` — brief quick command listing
- `instructions` — longer usage text and notes
- `shell` — interactive REPL-like shell for quick commands and chat
- `info` — print environment and data path information

Inside the interactive chat you can use:
- `select task <n>` or `/select <n>` — attach a task to the chat by list-number
- `clear selection` or `/clear` — clear the selection
- `advise all` or `advise selected <n>` — request productivity advice
- `exit` or `/exit` — leave the interactive chat

## Data locations

By default the project will create an `app_data/` and/or `data_pkms/` directory in the project root depending on backend and migration status.

- JSON stores (legacy/support): `data_pkms/tasks.json`, `data_pkms/docs.json`, or `app_data/tasks.json`
- SQLite DB (durable): `app_data/tasks.db` or `data_pkms/tasks.db`

The `reset` command removes these known locations (see `reset` docs above).

## Optional Extras
- Small experimental TUI available via `dashboard --interactive` when Textual is installed
- `tasks3/` contains older demos and experiments (kept as examples)

## Tests
Run all tests:
```bash
pytest -q tasks3/tests

# core + new chat/agent tests
pytest -q tests
```

If you prefer not to activate the virtual environment (or activation is blocked in PowerShell), use the included helper scripts:

Windows PowerShell (no activation required):
```powershell
.\run_tests.ps1
```

macOS / Linux:
```bash
./run_tests.sh
```

PowerShell activation notes (if you do want to activate):
- On Windows PowerShell run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
. .\.venv\Scripts\Activate.ps1
```
- Then install dev requirements:
```powershell
pip install -e . pytest
```

## Next Steps
- Consolidate extras into plugin-style modules
- Enhance agent advice (prioritization, focus suggestions)
- Real LLM integration behind adapter interface
- Package optional dependencies (rich/textual)

## Security & API Keys

To enable the real LLM adapter set `OPENAI_API_KEY` in your environment or use the CLI helper `setup-llm` to store the key in your OS keyring.

Bash:
```bash
export OPENAI_API_KEY="sk-..."
```

PowerShell:
```powershell
$env:OPENAI_API_KEY = "sk-..."
```

Or run:
```bash
python -m pkms_core.cli setup-llm
```

If no key is present the agent falls back to local heuristic logic. Never commit keys to source control.

Enjoy vibecoding your PKMS & task workflows!
