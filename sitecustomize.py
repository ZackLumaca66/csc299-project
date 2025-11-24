"""Ensure local project root is on sys.path for tests without editable install."""
import sys, os
root = os.path.dirname(__file__)
if root not in sys.path:
    sys.path.insert(0, root)