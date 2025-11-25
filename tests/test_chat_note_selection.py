from pkms_core.chat import ChatEngine, ChatHistory
from pkms_core.agent import Agent
from pkms_core.core import TaskManager, DocumentManager
from pkms_core import storage as S


def test_chat_note_selection(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    # create a note
    n = S.add_note('json', str(tmp_path), "Note for chat")
    tm = TaskManager(backend='json')
    dm = DocumentManager()
    history = ChatHistory([])
    engine = ChatEngine(Agent(), tm, dm, history)
    ok = engine.select_note(1)
    assert ok
    resp = engine.handle_message('advise')
    assert 'Note focus' in resp
