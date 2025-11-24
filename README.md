[![Task-Neko tests](https://github.com/ZackLumaca66/csc299-project/actions/workflows/python-tests.yml/badge.svg)](https://github.com/ZackLumaca66/csc299-project/actions/workflows/python-tests.yml)

# PKMS Core Prototype

Lean task + personal knowledge management CLI with selectable storage (JSON or SQLite) and ranked document search.

## Features
- Tasks: add, list, search, toggle, delete, export
- Documents: add, list, search (ranked by token matches), view, delete
- Storage: `--backend json` (simple) or `--backend sqlite` (durable)
- Inverted index for faster, more relevant document search
- Chat interface: `chat <message>`, `chat-history`, `chat-suggest`
- Agent heuristics: summarize tasks/docs; extract TODO / imperative lines into suggestions
- Optional LLM adapter: auto-activates when `OPENAI_KEY` or `ANTHROPIC_KEY` is set (falls back to heuristics otherwise)
- Tested across managers, search logic, chat/agent (see `tests/` and `tasks3/tests/`)

## Quick Start
```bash
# (Optional) create venv
python -m venv .venv && . .venv/Scripts/activate  # Windows PowerShell
# or: source .venv/bin/activate  # macOS/Linux

# Install in editable mode
pip install -e .

# Add tasks
pkms add "Write README"
pkms add "Plan agent architecture" --backend sqlite
pkms list
pkms search plan

# Documents
pkms doc-add "Design" "Agent architecture draft" --tags design,agent
pkms doc-search agent architecture
pkms doc-view 1

# Export tasks
pkms export tasks.json
```

## Demo script
We include a small demo script that showcases the agent and a mocked LLM adapter when no API key is present:

```bash
python scripts/demo_pkms_chat.py
```

This prints agent productivity advice, document-derived suggestions, and mock LLM summaries suitable for a short demo video.

## Commands
```text
pkms add <text>
pkms list
pkms search <query>
pkms toggle <id>
pkms delete <id>
pkms export <path>
pkms doc-add <title> <text> [--tags tag1,tag2]
pkms doc-list
pkms doc-search <query>
pkms doc-view <id>
pkms doc-delete <id>
pkms chat <message>
pkms chat-history
pkms chat-suggest
```
Add `--backend sqlite` to task commands for SQLite storage.

## Data Locations
- JSON: `data_pkms/tasks.json`, `data_pkms/docs.json`
- SQLite: `data_pkms/tasks.db`

## Optional Extras
- Neko pet & experimental dashboard (still in `tasks3/src/tasks3_cli/`)
- Future Textual TUI planned as a plugin layer

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
Set one of these environment variables to enable enhanced (stubbed) LLM summaries (future: real API calls):

```
export OPENAI_KEY=sk-...
export ANTHROPIC_KEY=...
```

If neither is set the system uses local heuristic logic (fast, offline). Never commit keys—store them in your shell profile or a `.env` excluded by `.gitignore`. Replace `pkms_core/llm.py` with real provider calls as a drop-in upgrade.

Enjoy vibecoding your PKMS & task workflows!
