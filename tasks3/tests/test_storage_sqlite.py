from tasks3_cli.core import TaskManager


def test_sqlite_backend_add_list_toggle_delete(tmp_path):
    # Use a temporary directory so we do not interfere with existing data
    cwd = tmp_path / "work"
    cwd.mkdir()
    # Change working directory for TaskManager initialization
    import os
    old = os.getcwd()
    os.chdir(cwd)
    try:
        tm = TaskManager(backend="sqlite")
        t1 = tm.add("Alpha")
        t2 = tm.add("Beta")
        assert {t.text for t in tm.list()} >= {"Alpha", "Beta"}
        tm.toggle(t1.id)
        assert [t.text for t in tm.list() if t.completed] == ["Alpha"]
        tm.delete(t2.id)
        remaining = [t.text for t in tm.list()]
        assert "Beta" not in remaining
    finally:
        os.chdir(old)