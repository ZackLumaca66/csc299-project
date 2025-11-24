import sys
import os

# Ensure local src path is importable
ROOT = os.path.join(os.getcwd(), "tasks3", "src")
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tasks3_cli.core import TaskManager
from tasks3_cli.neko import NekoManager


def test_neko_heal_on_toggle(tmp_path):
    data_dir = tmp_path
    # create a TaskManager pointing to temp file and a NekoManager with temp file
    tm_path = str(data_dir / "tasks.json")
    neko_path = str(data_dir / "neko.json")

    neko = NekoManager(path=neko_path, default_life=10)
    tm = TaskManager(path=tm_path, on_toggle=neko.on_task_toggled)

    t = tm.add("sample task")
    assert not t.completed
    before = neko.life
    # toggle to complete
    tm.toggle(t.id)
    assert neko.life > before
