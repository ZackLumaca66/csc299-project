from pkms_core import storage as S


def test_notes_sqlite_basic(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    backend = 'sqlite'
    n = S.add_note(backend, str(tmp_path), "SQLite note")
    assert n.id == 1
    notes = S.list_notes(backend, str(tmp_path))
    assert len(notes) == 1 and notes[0].text == "SQLite note"
    S.describe_note(backend, str(tmp_path), 1, "sqlite detail")
    notes = S.list_notes(backend, str(tmp_path))
    assert len(notes[0].details) == 1
    res = S.search_notes(backend, str(tmp_path), "sqlite")
    assert len(res) == 1
    ok = S.delete_note(backend, str(tmp_path), 1)
    assert ok
    assert S.list_notes(backend, str(tmp_path)) == []
