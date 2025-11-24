import sys
import os

# Ensure the local src directory is on sys.path so tests can import tasks_cli
ROOT = os.path.join(os.getcwd(), "tasks_cli", "src")
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tasks_cli.core import TaskManager


def test_add_and_list(tmp_path, monkeypatch):
    # use a temporary file for tasks.json
    data_file = tmp_path / "tasks.json"
    tm = TaskManager(path=str(data_file))
    assert tm.list() == []
    t = tm.add("write tests")
    assert t.id == 1
    assert t.text == "write tests"
    tasks = tm.list()
    assert len(tasks) == 1


def test_search_and_toggle(tmp_path):
    data_file = tmp_path / "tasks.json"
    tm = TaskManager(path=str(data_file))
    tm.add("first task")
    tm.add("second task about python")
    results = tm.search("python")
    assert len(results) == 1
    t = results[0]
    assert not t.completed
    toggled = tm.toggle(t.id)
    assert toggled is not None and toggled.completed is True
