Deliverables
============

This folder describes what to include when preparing the final deliverable for the PKMS prototype and how to produce the submission artifacts.

Contents
- `SUBMISSION_CHECKLIST.md` — step-by-step checklist for producing artifacts.
- `commit-history.txt` — optional generated commit history (run `scripts/generate_commit_history.sh`).

Where the prototype code lives
- Main package: `pkms_core/`
- CLI: `pkms_core/cli.py`
- Demo script: `scripts/demo_pkms_chat.py`
- Focused tests: `tests/` and `tasks3/tests/`

Quick local reproduction

1. Create and activate a virtualenv (optional):

```bash
python -m venv .venv
source .venv/bin/activate    # on Windows (git-bash): .venv/Scripts/activate
```

2. Install the project in editable mode:

```bash
python -m pip install --upgrade pip
python -m pip install -e .
```

3. Run the demo:

```bash
python scripts/demo_pkms_chat.py
```

4. Run the focused tests (same subset CI runs):

```bash
python -m pytest -q tests tasks3/tests
```

Notes
- Do not include large binary database files in submissions; instead include small example data in `data/` or `data_pkms/` when necessary.
