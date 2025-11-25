import os
from pkms_core.core import TaskManager
from pkms_core.storage import list_notes


def test_priority_and_tags_persist_json(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    tm = TaskManager(backend='json')
    t = tm.add('Task with tags', priority=5, tags=['alpha','beta'])
    # reload manager to ensure data persisted
    tm2 = TaskManager(backend='json')
    tasks = tm2.list()
    found = next((x for x in tasks if x.id == t.id), None)
    assert found is not None
    assert getattr(found, 'priority', None) == 5
    assert getattr(found, 'tags', []) == ['alpha','beta']


def test_priority_and_tags_persist_sqlite(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    tm = TaskManager(backend='sqlite')
    t = tm.add('DB task with tags', priority=4, tags=['x','y'])
    # reload manager to ensure data persisted
    tm2 = TaskManager(backend='sqlite')
    tasks = tm2.list()
    found = next((x for x in tasks if x.id == t.id), None)
    assert found is not None
    assert getattr(found, 'priority', None) == 4
    assert getattr(found, 'tags', []) == ['x','y']
