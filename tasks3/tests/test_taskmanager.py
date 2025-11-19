from tasks2.core import TaskManager

def test_add_and_complete():
    tm = TaskManager()
    tm.add("Task A")
    tm.add("Task B")
    tm.complete("Task A")
    assert [t.title for t in tm.completed()] == ["Task A"]
    assert [t.title for t in tm.pending()] == ["Task B"]