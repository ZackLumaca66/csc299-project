import os
from pkms_core import storage as S


def test_notes_json_basic(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    backend = 'json'
    # add
    n = S.add_note(backend, str(tmp_path), "Research vector DBs")
    assert n.id == 1
    notes = S.list_notes(backend, str(tmp_path))
    assert len(notes) == 1 and notes[0].text == "Research vector DBs"
    # describe
    S.describe_note(backend, str(tmp_path), 1, "check FTS options")
    notes = S.list_notes(backend, str(tmp_path))
    assert len(notes[0].details) == 1
    # search
    res = S.search_notes(backend, str(tmp_path), "vector")
    assert len(res) == 1
    # delete
    ok = S.delete_note(backend, str(tmp_path), 1)
    assert ok
    assert S.list_notes(backend, str(tmp_path)) == []
