#!/usr/bin/env python3
"""Launcher for tasks3 CLI/demo that fixes sys.path so the package can be imported.

Usage:
  python run_tasks3.py --cli    # run interactive CLI
  python run_tasks3.py --demo   # run scripted demo and exit
"""
import sys
import os
import platform
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "tasks3" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def main(argv=None):
    argv = argv or sys.argv[1:]
    if not argv or argv[0] in ("--cli", "cli"):
        # run interactive CLI
        try:
            from tasks3_cli import cli
            cli.run()
        except Exception as e:
            print("Failed to start CLI:", e)
            raise
    elif argv[0] in ("--demo", "demo"):
        try:
            import tasks3.demo.run_demo as demo
            demo.main()
        except Exception as e:
            print("Failed to run demo:", e)
            raise
    elif argv[0] in ("--dashboard", "dashboard"):
        # Platform hint for Git Bash (MinTTY) on Windows: suggest using winpty
        try:
            if platform.system() == "Windows":
                # Git Bash sets MSYSTEM; MinTTY often uses TERM like 'xterm-256color'
                ms = os.environ.get("MSYSTEM")
                term = os.environ.get("TERM", "")
                winpty_path = shutil.which("winpty")
                if (ms or term.startswith("xterm")) and winpty_path:
                    print("[run_tasks3] Notice: You appear to be using Git Bash/MinTTY on Windows.")
                    print("If interactive input behaves oddly, run with: \n    winpty python run_tasks3.py --dashboard")

            from tasks3_cli import dashboard
            dashboard.run_dashboard()
        except Exception as e:
            print("Failed to start dashboard:", e)
            raise
    else:
        print("Usage: python run_tasks3.py (--cli|--demo)")


if __name__ == '__main__':
    main()
