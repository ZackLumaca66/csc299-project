from pkms_core.agent import Agent
from pkms_core.core import TaskManager, DocumentManager
from pkms_core.dashboard import build_plain

def test_productivity_advice_and_plain_dashboard(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    tm = TaskManager()
    dm = DocumentManager()
    # Add tasks
    tm.add("Short task")
    tm.add("This is a much longer task that should be broken down into smaller actionable subtasks for progress")
    # Add document with TODO and imperative
    dm.add("Plan", "TODO: create dashboard\nImplement advisor scoring soon", tags=["plan"])
    agent = Agent()
    advice = agent.productivity_advice(tm.list(), dm.list())
    assert any("Break down" in a for a in advice)
    assert any("Doc-derived" in a for a in advice)
    dash = build_plain(tm.list(), dm.list(), agent)
    assert "DASHBOARD" in dash
    assert "Advice:" in dash
    assert "Suggestions:" in dash