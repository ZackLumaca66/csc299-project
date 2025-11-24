from pkms_core.core import TaskManager, DocumentManager
from pkms_core.agent import Agent
from pkms_core.dashboard import show_dashboard
import io, sys


def test_show_dashboard_renders_plain(tmp_path, monkeypatch, capsys):
    # isolate data dir
    monkeypatch.chdir(tmp_path)
    tm = TaskManager(backend='json')
    dm = DocumentManager()
    tm.add('Task one')
    tm.add('Task two longer description that should be visible')
    dm.add('Doc A', 'TODO: action A\nNote line two', tags=['test'])
    agent = Agent()
    # call show_dashboard; it will use Rich if available, otherwise print plaintext
    show_dashboard(tm.list(), dm.list(), agent)
    captured = capsys.readouterr()
    output = captured.out + captured.err
    assert 'Tasks' in output or 'DASHBOARD' in output
    # Dashboard intentionally does not include advice panels
    assert 'Advice' not in output and 'Advice:' not in output
