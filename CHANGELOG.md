# Changelog

## Unreleased

- Remove full-dashboard UI: dashboard now always shows tasks and their details only. Documents, advice, and suggestions are no longer shown on the default dashboard.
- Removed the `--full` CLI dashboard flag and associated code paths.
- Added an explicit unit test `tests/test_dashboard_no_advice.py` to ensure the dashboard never contains advice or suggestions.
- Implemented best-effort automatic document migration into `app_data/docs.json` from common legacy locations and file names (`docs.json`, `documents.json`, `task_neko_data.json`, etc.).
- Updated tests to reflect the new dashboard behavior; full test suite passes (`33 passed`).

- Added executable launchers `pkms` (bash) and `pkms.ps1` (PowerShell) for running the CLI directly.
- CLI numeric ids are now strictly list numbers (1-based) for `edit`, `toggle`/`complete`, `delete`, `describe`, and chat `--task-id` selection; out-of-range numbers now return 'not found'.

Notes:
- Agent heuristics (advice/suggestions) remain available via `pkms advise`, chat commands, and demo scripts — they are intentionally not displayed on the dashboard per the user's directive.
# Changelog

All notable changes to this project should be documented in this file.

## [Unreleased]
- Add deliverables/ README and submission checklist.
- CI: ensure package is installed before running tests in workflows.

## 0.1.0 - 2025-11-24
- Prototype: initial pkms_core package with interactive chat, CLI, agent heuristics, and demo script.
