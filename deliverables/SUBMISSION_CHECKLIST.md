# Submission checklist

Follow these steps to produce a tidy submission package for the prototype.

1. Final software
   - Include the `pkms_core/` directory and any small helper scripts (for example `scripts/demo_pkms_chat.py`).

2. Fine-grained commit history
   - Generate a compact commit history file:

```bash
bash scripts/generate_commit_history.sh > deliverables/commit-history.txt
```

3. Tests & test output
   - Run focused tests and capture the output:

```bash
python -m pytest -q tests tasks3/tests --maxfail=1 --disable-warnings > pytest-output.txt
```

4. Documentation
   - Include `deliverables/README.md`, `docs/PROTOTYPE.md`, and `CHANGELOG.md`.

5. Prototypes
   - Include the demo script and any small sample data.

6. Final verification
   - Confirm the repository builds and tests pass locally in a fresh virtual environment.

If you want, I can create a ZIP of the above artifacts for submission.
