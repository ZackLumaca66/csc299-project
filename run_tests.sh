#!/usr/bin/env bash
# Run focused tests using the project's virtual environment without requiring activation.
# If `.venv` does not exist the script will create it and install `pytest`.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
VENV_PY="$ROOT/.venv/bin/python"
if [ -x "$VENV_PY" ]; then
  echo "Using venv python: $VENV_PY"
else
  echo "Creating virtual environment .venv..."
  python -m venv "$ROOT/.venv"
  VENV_PY="$ROOT/.venv/bin/python"
fi
"$VENV_PY" -m pip install --upgrade pip
"$VENV_PY" -m pip install pytest
"$VENV_PY" -m pytest tests -q
