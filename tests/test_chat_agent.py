from pkms_core.core import TaskManager, DocumentManager
from pkms_core.agent import Agent
from pkms_core.chat import ChatHistory, ChatEngine

def test_agent_suggestions_and_chat_flow():
    tm = TaskManager()
    dm = DocumentManager()
    dm.add("Dev Plan", "TODO: implement chat\nRefactor core module\nAdd tests soon", tags=["plan"])
    agent = Agent()
    history = ChatHistory()
    chat = ChatEngine(agent, tm, dm, history)
    resp = chat.handle_message("suggest tasks")
    assert "implement chat" in resp.lower()
    assert "refactor core module" in resp.lower()
    resp2 = chat.handle_message("summarize doc 1")
    assert resp2.lower().startswith("dev plan:")
    t = tm.add("Write integration tests for chat")
    resp3 = chat.handle_message(f"summarize task {t.id}")
    assert "write integration tests" in resp3.lower()
    history.save()
    loaded = ChatHistory.load()
    assert len(loaded.entries) >= 3