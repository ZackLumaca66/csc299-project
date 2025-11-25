import os
from pkms_core.cli import main
from pkms_core.core import TaskManager
from pkms_core.storage import add_note

def test_review_shows_today_items(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    # create a task and a note
    tm = TaskManager(backend='json')
    t = tm.add('Task added today for review')
    n = add_note('json', str(tmp_path), 'Note added today for review')
    # run CLI review command
    main(['review'])
    out = capsys.readouterr().out
    assert 'Tasks added today: 1' in out
    assert 'Notes added today: 1' in out
    assert 'Task added today for review' in out
    assert 'Note added today for review' in out
