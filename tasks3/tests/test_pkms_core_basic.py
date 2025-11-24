from pkms_core.core import TaskManager, DocumentManager

def test_pkms_task_and_doc_flow(tmp_path, monkeypatch):
    # isolate working directory
    monkeypatch.chdir(tmp_path)
    tm = TaskManager(backend='json')
    t = tm.add('Initial Task')
    assert t.id == 1 and t.text == 'Initial Task'
    tm.toggle(t.id)
    assert tm.list()[0].completed is True
    dm = DocumentManager()
    d = dm.add('Example Doc', 'This document explains the system', tags=['example','design'])
    results = dm.search('prototype design')
    assert results and results[0].id == d.id
