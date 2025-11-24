from pkms_core.core import TaskManager, DocumentManager
from pkms_core.agent import Agent
from pkms_core.dashboard import show_dashboard


def test_dashboard_never_shows_advice_or_suggestions(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    tm = TaskManager()
    dm = DocumentManager()
    # add a task and a document to simulate non-empty state
    tm.add('Sample task for dashboard')
    dm.add('Sample doc', 'TODO: something to do', tags=['test'])
    agent = Agent()
    # render dashboard (rich may be present). Ensure output does not include Advice or Suggestions headings
    show_dashboard(tm.list(), dm.list(), agent)
    out = capsys.readouterr().out
    assert 'Advice' not in out and 'Suggestions' not in out
