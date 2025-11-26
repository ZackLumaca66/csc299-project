Getting Started — Run & Use
===========================

Quick steps to run and use this project locally on Windows (bash or PowerShell).

Prerequisites
- Python 3.8+ installed and on your PATH
- Git (optional)

1) Create and activate a virtual environment

- Bash (Git Bash / "bash.exe"):
```bash
python -m venv .venv
source .venv/Scripts/activate
```

- PowerShell:
```powershell
python -m venv .venv
. .venv/Scripts/Activate.ps1
```

2) Install the project and test/demo deps

```bash
pip install --upgrade pip
pip install -e .
pip install pytest
pip install -r tasks3/requirements.txt || true
```

Notes:
- `pip install -e .` installs the package in editable mode and wires up the `pkms` console script.
- `|| true` prevents failure if `tasks3/requirements.txt` is absent.

3) Run the full test suite

```bash
.venv/Scripts/python.exe -m pytest -q
```

Expected: tests should pass (the repository's last run showed `60 passed`).

4) Run the CLI smoke script (exercises common flows)

```bash
.venv/Scripts/python.exe scripts/run_cli_smoke.py
```

This script runs `pkms add`, `pkms list`, `pkms advise`, `pkms notes add/list`, `pkms export`, and `pkms reset` in a temporary directory, and performs safe cleanup.

5) Run the demo used by `tasks3`

```bash
PYTHONPATH=./tasks3/src .venv/Scripts/python.exe tasks3/demo/run_demo.py
```

6) Use the CLI interactively

After `pip install -e .` you can run:
```bash
pkms --help
pkms add "Example task"
pkms list
```

Notes management (new `notes <n>` behavior)

The CLI supports viewing and managing individual notes by their list-number (1-based). Examples:

```bash
# Add a note
pkms notes add "Capture quick idea about tests"

# List notes
pkms notes list

# View a specific note by list-number (shows details)
pkms notes 1

# Add a detail to note 1
pkms notes 1 describe "A short detail"

# Delete a note
pkms notes 1 delete
```

Completing tasks (`complete <n>`)

Mark tasks complete using the list-number shown by `pkms list` (1-based):

```bash
# Mark task number 2 completed
pkms complete 2

# Confirm status
pkms list
```

7) Optional: enable LLM-backed advice

Set your environment variable for an OpenAI-style key (example):
```bash
export OPENAI_API_KEY="sk_..."
.venv/Scripts/python.exe scripts/run_cli_smoke.py
```

On PowerShell:
```powershell
$env:OPENAI_API_KEY = "sk_..."
.venv/Scripts/python.exe scripts/run_cli_smoke.py
```

Troubleshooting
- If `pkms` is not found, make sure the venv is activated, or run the CLI via `.venv/Scripts/python.exe -m pkms_core.cli`.
- If you see Windows PermissionError while removing tempdirs, ensure your shell is not `cd`'d inside the temp dir; `scripts/run_cli_smoke.py` restores the original working directory before cleanup.

Want help?
- I can add a short entry to `README.md` or a GitHub Actions workflow to run tests and the smoke script on CI. Tell me which.

First-run welcome
-----------------

When a new user runs `pkms` (or `python -m pkms_core.cli`) without any existing data, the CLI now displays the `PKMS Home — quick commands` welcome screen instead of the raw argparse help. This happens only when there are no tasks, documents, or notes present in the current working directory — it's intended to help newcomers discover common commands quickly.

Examples:

```bash
# In an empty directory
.venv/Scripts/python.exe -m pkms_core.cli
# -> prints the PKMS Home quick commands screen
```

If you prefer the traditional argparse help, run `pkms --help` or provide any subcommand.
