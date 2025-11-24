#!/usr/bin/env bash
set -euo pipefail

# Simple launcher for Task-Neko (Windows Git Bash / Linux)
# - Creates a local venv at .venv if missing
# - Installs runtime deps (textual)
# - Optionally installs dev deps with --dev
# - Supports scripted test mode via --test-actions and --data-file

ROOTDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$ROOTDIR/.venv"

echo "Task-Neko launcher: root=$ROOTDIR"

# Find a system python to create the venv if needed
if command -v python >/dev/null 2>&1; then
  SYS_PY=python
elif command -v python3 >/dev/null 2>&1; then
  SYS_PY=python3
else
  echo "No python executable found in PATH. Install Python and re-run." >&2
  exit 1
fi

# Choose venv python path depending on platform
if [[ "${MSYSTEM-}" != "" ]] || [[ "$OSTYPE" == msys* ]] || [[ "$OSTYPE" == cygwin* ]] || [[ "$OSTYPE" == win32* ]]; then
  VENV_PY="$VENV/Scripts/python.exe"
else
  VENV_PY="$VENV/bin/python"
fi

if [ ! -d "$VENV" ]; then
  echo "Creating virtual environment at $VENV..."
  "$SYS_PY" -m venv "$VENV"
fi

# Prefer the venv python if it exists, otherwise fall back to system python
if [ -x "$VENV_PY" ]; then
  PY="$VENV_PY"
else
  echo "Warning: venv python not found at $VENV_PY, falling back to $SYS_PY"
  PY="$SYS_PY"
fi

echo "Upgrading pip and installing runtime dependencies..."
"$PY" -m pip install --upgrade pip
"$PY" -m pip install textual

# Parse arguments
TEST_ACTIONS=""
DATA_FILE=""
INSTALL_DEV=0

while [[ $# -gt 0 ]]; do
  case $1 in
    --test-actions)
      TEST_ACTIONS="$2"; shift 2;;
    --data-file)
      DATA_FILE="$2"; shift 2;;
    --dev)
      INSTALL_DEV=1; shift;;
    --help|-h)
      echo "Usage: run.sh [--test-actions '<json>'] [--data-file path] [--dev]";
      exit 0;;
    *)
      echo "Unknown arg: $1"; exit 1;;
  esac
done

if [ "$INSTALL_DEV" -eq 1 ]; then
  echo "Installing development dependencies..."
  "$PY" -m pip install pytest >/dev/null
fi

MAIN="$ROOTDIR/task-neko/main.py"

echo "Launching Task-Neko..."

# Export test/data envs if provided so subshells inherit them
if [ -n "$TEST_ACTIONS" ]; then
  export TASK_NEKO_TEST_ACTIONS="$TEST_ACTIONS"
fi
if [ -n "$DATA_FILE" ]; then
  export TASK_NEKO_DATA_FILE="$DATA_FILE"
fi

# Helper to launch python with winpty when appropriate
launch_with_tty() {
  local python_cmd="$1"
  local main_py="$2"
  # Detect MSYS / MinTTY environments that need winpty
  if [ -n "${MSYSTEM-}" ] || [[ "${TERM-}" == *"mintty"* ]] || [[ "${TERM-}" == "msys" ]]; then
    echo "Detected MSYS/MINGW terminal. Adjusting environment for Textual..."
    export TERM=${TERM:-xterm-256color}
    export COLORTERM=${COLORTERM:-truecolor}
    if command -v winpty >/dev/null 2>&1; then
      echo "Using winpty for better TTY support"
      winpty "$python_cmd" "$main_py"
      return $?
    else
      echo "winpty not found — attempting to launch using native Windows console"
      # Convert paths to Windows form if cygpath is available
      if command -v cygpath >/dev/null 2>&1; then
        WIN_PY="$(cygpath -w "$python_cmd")"
        WIN_MAIN="$(cygpath -w "$main_py")"
      else
        WIN_PY="$python_cmd"
        WIN_MAIN="$main_py"
      fi
      cmd.exe /c start "Task-Neko" /wait "${WIN_PY}" "${WIN_MAIN}"
      return $?
    fi
  else
    # Not MSYS; try winpty if available (harmless on many systems), otherwise call directly
    if command -v winpty >/dev/null 2>&1; then
      winpty "$python_cmd" "$main_py"
    else
      "$python_cmd" "$main_py"
    fi
    return $?
  fi
}

# Final launcher invocation
launch_with_tty "$PY" "$MAIN"
