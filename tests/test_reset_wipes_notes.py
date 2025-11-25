from pkms_core import storage as S
from pkms_core.cli import main as cli_main


def test_reset_wipes_notes(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    S.add_note('json', str(tmp_path), 'to be deleted')
    notes = S.list_notes('json', str(tmp_path))
    assert len(notes) == 1
    # run reset (non-interactive)
    cli_main(['reset','--yes'])
    notes = S.list_notes('json', str(tmp_path))
    assert notes == []
