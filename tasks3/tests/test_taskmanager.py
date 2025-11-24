from tasks3_cli.core import TaskManager

def test_add_and_complete():
    tm = TaskManager()
    existing_ids = {t.id for t in tm.list()}
    t_a = tm.add("Task A")
    t_b = tm.add("Task B")
    tm.set_completed(t_a.id, True)
    completed_new = [t.text for t in tm.list() if t.completed and t.id not in existing_ids]
    pending_new = [t.text for t in tm.list() if not t.completed and t.id not in existing_ids]
    assert completed_new == ["Task A"]
    assert pending_new == ["Task B"]