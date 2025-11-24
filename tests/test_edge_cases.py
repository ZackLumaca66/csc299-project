from pkms_core.core import TaskManager, DocumentManager
from pkms_core.agent import Agent
from pkms_core.dashboard import build_plain, show_dashboard


def test_empty_stores(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    tm = TaskManager()
    dm = DocumentManager()
    agent = Agent()
    # No tasks/docs
    advice = agent.productivity_advice(tm.list(), dm.list())
    assert any('No advice' in a or 'Tasks: 0' in a or 'Tasks:' in a for a in advice)
    # Dashboard should not raise and should contain headers
    show_dashboard(tm.list(), dm.list(), agent)
    out = capsys.readouterr().out
    assert 'Advice' in out or 'DASHBOARD' in out


def test_large_number_of_items(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    tm = TaskManager()
    dm = DocumentManager()
    # Add large number of tasks and documents
    for i in range(200):
        tm.add(f"Task number {i} for load testing")
    for j in range(120):
        dm.add(f"Doc {j}", f"Content with TODO: action {j}", tags=["load"]) 
    agent = Agent()
    # Advice should mention breaking down long tasks or present focus candidates
    advice = agent.productivity_advice(tm.list(), dm.list())
    assert isinstance(advice, list)
    # Dashboard render should complete without exception
    show_dashboard(tm.list(), dm.list(), agent)
    out = capsys.readouterr().out
    assert 'Tasks' in out or 'DASHBOARD' in out


def test_unicode_handling(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    tm = TaskManager()
    dm = DocumentManager()
    unicode_text = '研究✨ — 完成任务 🚀'
    tm.add(unicode_text)
    dm.add('国際化', f'内容: 包含 {unicode_text} 和 emoji 😊', tags=['国'])
    agent = Agent()
    # Search should find unicode substrings
    results = tm.search('完成任务')
    assert any('完成任务' in t.text for t in results)
    # Dashboard should render unicode without crashing
    show_dashboard(tm.list(), dm.list(), agent)
    out = capsys.readouterr().out
    assert '国際化' in out or '完成任务' in out
