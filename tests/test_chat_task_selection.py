from __future__ import annotations
import tempfile
from pkms_core.chat import ChatEngine, ChatHistory
from pkms_core.core import TaskManager, DocumentManager
from pkms_core.storage import JsonTaskStore, DocumentStore
from pkms_core.llm_mock import MockLLM
from pkms_core.agent import Agent


def test_chat_with_selected_task_uses_mock_llm():
    with tempfile.TemporaryDirectory() as td:
        task_path = td + '/tasks.json'
        doc_path = td + '/docs.json'
        tm = TaskManager(store=JsonTaskStore(task_path))
        dm = DocumentManager(store=DocumentStore(doc_path))
        # add a task
        t = tm.add('Write unit tests for chat selection and interactive flow')
        # attach mock llm
        mock = MockLLM()
        agent = Agent(llm=mock)
        history = ChatHistory()
        engine = ChatEngine(agent, tm, dm, history)
        ok = engine.select_task(t.id)
        assert ok
        resp = engine.handle_message('How should I break this down?')
        assert resp is not None and resp.startswith('[mock-llm]')


def test_chat_without_llm_returns_heuristic_summary():
    with tempfile.TemporaryDirectory() as td:
        task_path = td + '/tasks.json'
        doc_path = td + '/docs.json'
        tm = TaskManager(store=JsonTaskStore(task_path))
        dm = DocumentManager(store=DocumentStore(doc_path))
        t = tm.add('A very long task that probably needs to be split into multiple smaller subtasks to make progress')
        agent = Agent(llm=None)
        history = ChatHistory()
        engine = ChatEngine(agent, tm, dm, history)
        assert engine.select_task(t.id)
        resp = engine.handle_message('Give me advice')
        assert 'Selected task' in resp
        assert 'consider breaking' in resp or 'consider' in resp
