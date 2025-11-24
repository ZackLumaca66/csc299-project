PKMS — Personal Knowledge & Task Management (Draft README)
=========================================

This is a working draft of the final README for the PKMS terminal application. It is intended to be comprehensive and self-contained so users can install, configure, and use the software from a terminal.

1. Quick overview
------------------
- Purpose: A terminal-first Personal Knowledge Management and Task system. Add/edit/complete tasks, attach bullet details, store documents, and get AI-powered productivity advice focused on tasks and documents.
- UX: Numbered dashboard (1-based list numbers) is the primary navigation unit. Chat companion provides productivity advice either for all tasks or for a selected task.

2. Requirements
---------------
- Python 3.10+ (3.11 recommended)
- Optional: `keyring` package for secure OpenAI API key storage
- Optional: network access + OpenAI API key to enable the real LLM adapter

3. Installation (developer/local)
--------------------------------
1. Clone the repo:

```bash
git clone <repo-url>
cd csc299-project
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate   # on Windows PowerShell: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt    # if present; tests can run without optional deps
```

3. Optional: install `keyring` for secure key storage:

```bash
pip install keyring
```

4. Quick start (recommended)
---------------------------
- Show concise usage and guidance:

```bash
python -m pkms_core.cli instructions
python -m pkms_core.cli list
python -m pkms_core.cli add "Buy milk"
python -m pkms_core.cli complete 1
python -m pkms_core.cli chat "advise"
```

5. LLM configuration (recommended: secure)
-----------------------------------------
We support two convenient ways to supply your OpenAI API key:

- Recommended (secure): `keyring` integration
  - Install `keyring` and run:
    ```bash
    python -m pkms_core.cli setup-llm
    ```
    Paste your OpenAI API key (input hidden). The key is stored securely in the OS credential store.
  - To remove the key: `python -m pkms_core.cli setup-llm --remove`
  - To check whether a key is stored (masked): `python -m pkms_core.cli setup-llm --show`

- Alternative (CI/dev): set environment variable `OPENAI_API_KEY`:
  ```bash
  export OPENAI_API_KEY="sk-..."
  ```

6. Data location and migration
------------------------------
- Data directory: `./app_data/` by default. Tasks are persisted in `tasks.db` (SQLite) and documents in `docs.json`.
- Automatic migration: on first run the app attempts a best-effort migration of legacy `tasks.json` files from common legacy locations (`data_pkms`, `demo_data`, `task_neko`, repository root) into the SQLite DB. Documents migration is similar and normalizes common shapes.
- Manual migration helper: see `scripts/migrate_data.py`.

7. CLI reference (high-level)
----------------------------
- `pkms add "text"` — add a task
- `pkms list` or `pkms ls` — show numbered dashboard (tasks only)
- `pkms edit <n> "new text"` — edit the task at list-number `<n>`
- `pkms complete <n>` — mark task `<n>` complete (alias for `toggle`)
- `pkms delete <n>` — delete task `<n>`
- `pkms describe <n> "detail text"` — add a bullet detail to task `<n>`
- `pkms chat "advise"` — get productivity advice for all tasks
- `pkms chat "advise selected <n>"` — get advice for task `<n>` (can enter follow-up interactive mode)
- `pkms setup-llm` — store OpenAI API key securely in OS keyring
- `pkms instructions` — show detailed help and examples

Notes:
- Commands expect list-number indexes (1-based). Internal DB IDs are intentionally not exposed to users.

8. Chat companion behavior
--------------------------
- Two exposed chat flows for users:
  - `advise` / `advise all` — a productivity summary for all tasks and doc-derived suggestions.
  - `advise selected <n>` — summaries and targeted advice for a selected task (1-based list number). Optionally enters a short interactive follow-up session so you can ask clarifying questions.
- Programmatic ChatEngine still supports task CRUD and advanced commands for internal scripts and tests; the user-facing CLI intentionally limits the commands to the two advise forms for clarity and safety.

9. TUI
------
- A terminal TUI is available via `pkms dashboard --interactive` if built and supported on your platform. The default dashboard is a simple task list; the TUI provides additional navigation and shortcuts.

10. Tests and development
-------------------------
- Run unit and integration tests with `pytest`.
- Developer notes:
  - Tests use a deterministic Mock LLM when no API key is present.
  - Core logic is in `pkms_core/` and includes `core.py`, `storage.py`, `chat.py`, `agent.py`, and adapters.

11. Security & privacy
----------------------
- Keys are user-supplied. The repo never contains a bundled API key.
- Use `setup-llm` to store keys securely in the OS keyring; `OPENAI_API_KEY` remains supported for CI.
- Be mindful of what you send to an external LLM — docs and task text may be included in prompts.

12. Troubleshooting
-------------------
- If `pkms chat` reports "LLM adapter inactive (no key found)": run `python -m pkms_core.cli setup-llm` or set `OPENAI_API_KEY`.
- If dashboard shows no tasks: run `pkms add "Task text"` and then `pkms list`.
- If launching `./pkms` fails on Unix: `chmod +x pkms` may be required.

13. Contributing & roadmap
--------------------------
- Contribution guidelines: open issues and PRs. Include tests for new features.
- Roadmap items (candidate): improved document migration, secure multi-user data dir config, richer LLM agents, packaging and homebrew/scoop installers.

14. License
-----------
- Add license text here (TBD by project owner).

----

This is a draft. When you confirm the final feature set I will convert this to `README.md` and polish wording and examples.
