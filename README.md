[![Task-Neko tests](https://github.com/ZackLumaca66/csc299-project/actions/workflows/python-tests.yml/badge.svg)](https://github.com/ZackLumaca66/csc299-project/actions/workflows/python-tests.yml)

# PKMS Core

Lean task + personal knowledge management CLI with selectable storage (JSON or SQLite), a focused dashboard,
and a small chat/agent layer that can provide concise productivity advice.

**Instructions (Quick Overview)**

- Purpose: PKMS is a small CLI tool for managing tasks, lightweight notes, and short agent-driven productivity advice. It supports JSON or SQLite stores and includes a minimal chat interface.
- Recommended workflow: create a Python virtual environment, install the package in editable mode, then use the CLI via `python -m pkms_core.cli` or the provided `./pkms` launcher.
- Git Bash on Windows: activate the venv then run `python -m pkms_core.cli <command>`; the repo includes a Python sed-compat helper so shell scripts should work cross-platform.
- Common commands: `add`, `list`, `describe`, `notes add`, `chat`, `advise`, `reset --yes` (see Quick Start below for examples).

If you prefer a single command to run the CLI in any shell, use the module form:
```
python -m pkms_core.cli list
```


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

# Clear tasks/notes/chat history (non-destructive — preserves documents and app files)
# The `reset` command empties persisted stores but does not remove directories or documents.
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
- `reset [--yes]` — clears tasks, notes, and chat history (non-destructive — does not delete app files or documents)
- `home` — brief quick command listing
- `instructions` — longer usage text and notes
- `shell` — interactive REPL-like shell for quick commands and chat
- `info` — print environment and data path information

## Priority & Tags

Tasks now support simple metadata to help prioritize and filter work:

- `priority` (int 1–5, default 3): higher numbers mean higher priority.
- `tags` (list of strings): free-form labels attached to a task (stored as a JSON array in SQLite).

Add a task with priority and tags:

```bash
python -m pkms_core.cli add "Draft sprint plan" --priority 5 --tags "planning,sprint"
```

Tags are stored as a JSON array (e.g. `["planning","sprint"]`) in the SQLite `tags` column and as a list in the JSON backend. This keeps the format explicit and easy to evolve.

## Daily Review

Use the `review` command to get a quick daily summary of items you added today:

```bash
python -m pkms_core.cli review
```

The command prints counts and short truncated text for tasks and notes added today.

## Export / Import (JSON)

You can export your tasks and notes to a single JSON file and import them later. The export format is a simple JSON object with `tasks` and `notes` arrays.

Export:

```bash
python -m pkms_core.cli export backup.json
```

Import (appends items, assigning new IDs locally):

```bash
python -m pkms_core.cli import backup.json
```

The importer appends tasks and notes into the active backend, preserving details. If you want the remote to match exactly, run `reset` first.

Inside the interactive chat you can use:
- `select task <n>` or `/select <n>` — attach a task to the chat by list-number
- `clear selection` or `/clear` — clear the selection
- `advise all` or `advise selected <n>` — request productivity advice
- `exit` or `/exit` — leave the interactive chat

## Data locations

By default the project will create an `app_data/` and/or `data_pkms/` directory in the project root depending on backend and migration status.

- JSON stores (legacy/support): `data_pkms/tasks.json`, `data_pkms/docs.json`, or `app_data/tasks.json`
- SQLite DB (durable): `app_data/tasks.db` or `data_pkms/tasks.db`

The `reset` command empties these known stores (see `reset` docs above); it does not delete app directories or documents.

## Optional Extras

## Full command examples

The following examples show common workflows and illustrate flags and modal usage.

- Add a task (default backend is JSON unless you pass `--backend sqlite`):

```bash
python -m pkms_core.cli add "Buy groceries"
python -m pkms_core.cli add "Finish report" --priority 5 --tags "work,urgent"
```

- List tasks (dashboard):

```bash
python -m pkms_core.cli list
python -m pkms_core.cli dashboard         # same, with optional --interactive
python -m pkms_core.cli dashboard --interactive
```

- Edit and complete tasks (use list-number shown by `list`):

```bash
python -m pkms_core.cli edit 1 "Updated task text"
python -m pkms_core.cli complete 1
```

- Describe (add a detail bullet) to a task:

```bash
python -m pkms_core.cli describe 1 "Research API rate-limits"
```

- Delete a task by list-number:

```bash
python -m pkms_core.cli delete 2
```

- Notes: add, list, view details, describe, search, delete

```bash
python -m pkms_core.cli notes add "Design ideas for landing page"
python -m pkms_core.cli notes list
python -m pkms_core.cli notes 1            # show details for note 1
python -m pkms_core.cli notes 1 describe "Add wireframe links"
python -m pkms_core.cli notes search landing
python -m pkms_core.cli notes 1 delete
```

- Chat / advise usage

```bash
# Single-message, non-interactive advise
python -m pkms_core.cli chat "advise"
python -m pkms_core.cli chat "advise selected 1"

# Interactive chat session (type: advise all | advise selected <n> | /exit)
python -m pkms_core.cli chat --interactive

# Start chat with a selected note or task (use list-number)
python -m pkms_core.cli chat --task-id 1 --interactive
python -m pkms_core.cli chat --note-id 1 advise
```

- Export / Import (create backups or migrate stores)

```bash
python -m pkms_core.cli export backup.json
python -m pkms_core.cli import backup.json
```

- Reset (non-destructive):

```bash
# Use --yes in scripts/CI to skip confirmation prompt
python -m pkms_core.cli reset --yes
```

- Review (daily summary):

```bash
python -m pkms_core.cli review
```

- Setup LLM API key (store/inspect/remove in OS keyring):

```bash
python -m pkms_core.cli setup-llm        # prompts for key (keyring required)
python -m pkms_core.cli setup-llm --show
python -m pkms_core.cli setup-llm --remove
```

- Interactive shell (quick REPL for commands + chat):

```bash
python -m pkms_core.cli shell
# Inside: try `add <text>`, `list`, `advise`, `/select <n>`, `/exit`
```

Notes:
- Prefer the module form `python -m pkms_core.cli` for portability across shells (Git Bash, PowerShell, cmd).
- The repository contains top-level launchers `./pkms`, `pkms.bat`, and `pkms.ps1`. Use them if you added the repo to your PATH or prefer the convenience wrapper.

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
