import os
from pkms_core.storage import make_task_store
from pkms_core.models import Task


def make_tasks():
    return [
        Task(id=1, text="First task", created="t1", completed=False),
        Task(id=2, text="Second task", created="t2", completed=True),
    ]


def run_sequence_on_store(store_factory, base_dir):
    store = store_factory(base_dir)
    tasks = make_tasks()
    # add
    for t in tasks:
        store.add(t)
    loaded = store.load()
    assert [ (t.id,t.text,t.completed) for t in loaded ] == [ (t.id,t.text,t.completed) for t in tasks ]

    # update
    t = tasks[0]
    t.text = "First task - updated"
    store.update(t)
    loaded = store.load()
    assert any(l.text == "First task - updated" for l in loaded)

    # delete
    assert store.delete(2) is True
    loaded = store.load()
    assert all(l.id != 2 for l in loaded)


def test_json_and_sqlite_parity(tmp_path):
    base = str(tmp_path)
    # json
    run_sequence_on_store(lambda bd: make_task_store('json', bd), base)
    # sqlite
    run_sequence_on_store(lambda bd: make_task_store('sqlite', bd), base)
