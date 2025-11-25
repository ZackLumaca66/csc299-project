<!-- Copilot / AI coding assistant instructions for contributors -->

# Quick orientation

This repository implements a small PKMS-style toolkit with multiple example tasks and an internal, test-friendly agent pattern. When writing or modifying code, focus on the following quickly-discoverable facts rather than generic suggestions.

- **Core packages**: `pkms_core/` contains the main runtime pieces (`agent.py`, `cli.py`, `core.py`, `storage.py`). Treat `pkms_core` as the canonical library boundary.
- **Task examples**: `tasks3/` and `tasks5/` host demo apps and agent stubs (see `tasks3/src/tasks3_cli/agent.py` and `tasks3/demo/run_demo.py`). Use these files as patterns for adding new agent-backed features.

# Architecture & intent (big picture)

- The codebase uses small, testable agent implementations (e.g., `AgentStub`) for deterministic tests and offline development. Real LLM adapters live next to `llm_openai.py` / `llm.py` in `pkms_core/` but are guarded so tests can avoid network calls.
- Configuration and runtime commands are placed at repo root (`run.sh`, `run.ps1`, `run_tests.sh`, `run_tests.ps1`); scripts under `tasks5/.specify/` implement the agent-context generation workflow.

# Developer workflows and commands

- Run unit tests (POSIX):
  ```bash
  ./run_tests.sh
  # or
  python -m pytest -q
  ```
- Run tests on Windows PowerShell: `./run_tests.ps1`.
- Run small demos: `python tasks3/demo/run_demo.py` (shows `AgentStub` usage).
- Update agent context files (project-specific): run the updater under `.specify` (present in `tasks5`):
  ```bash
  tasks5/.specify/scripts/bash/update-agent-context.sh copilot
  ```
  The updater extracts fields from a feature `plan.md` and writes agent-specific context files (see `tasks5/.specify/scripts/bash/update-agent-context.sh`).

# Project-specific conventions and patterns

- Use `AgentStub`-style classes for deterministic behavior in tests (see `tasks3/src/tasks3_cli/agent.py`). When introducing real LLM calls, keep them behind adapters in `pkms_core/llm_*.py`.
- Auto-generated agent files are expected under `.github/agents/` (Copilot file path: `.github/agents/copilot-instructions.md`). Scripts will preserve manual additions — avoid editing inside generator-managed blocks if present.
- The `.specify/` system (under `tasks5/`) contains templates and scripts (`.specify/templates/agent-file-template.md`) used to create or refresh agent instruction files. Prefer using the scripts to keep formats consistent.

# Integration points & external dependencies

- LLM adapters: `pkms_core/llm_openai.py` and `pkms_core/llm_mock.py` — use `llm_mock` for tests and demos.
- Persistent storage variants are under `pkms_core/storage.py`; tests sometimes use SQLite (see `tests/test_storage_sqlite.py`).
- CI / automation: there is no top-level GitHub Actions in the repo; local scripts (`run_tests.sh` / `run_tests.ps1`) are the canonical entrypoints.

# Quick examples to copy-paste

- Create a test-friendly agent: follow `tasks3/src/tasks3_cli/agent.py` — small class, predictable outputs, dependency-injected into CLI/demo entrypoints.
- Update Copilot agent file (generator path):
  ```bash
  tasks5/.specify/scripts/bash/update-agent-context.sh copilot
  ```

# When in doubt

- Inspect `pkms_core/agent.py` and `tasks3/src/tasks3_cli/agent.py` for expected agent interfaces.
- If you need to change the agent context format, update the `.specify` template at `tasks5/.specify/templates/agent-file-template.md` and run the updater script.

Please review and tell me which areas you want expanded (CI details, secret handling, or additional file examples).
