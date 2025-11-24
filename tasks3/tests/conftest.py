import sys
import os

# Ensure local src path is importable for tests
SRC = os.path.join(os.getcwd(), "tasks3", "src")
PKG_ROOT = os.path.join(os.getcwd(), "tasks3")
PROJECT_ROOT = os.getcwd()
for p in (SRC, PKG_ROOT, PROJECT_ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)
