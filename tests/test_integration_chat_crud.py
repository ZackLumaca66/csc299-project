import pytest

from pkms_core.chat import ChatEngine, ChatHistory
from pkms_core.core import TaskManager
from pkms_core.llm_mock import MockLLM
from pkms_core.agent import Agent
from pkms_core.models import Task


def test_chat_crud_end_to_end(tmp_path):
    # setup managers with json store in temp dir
    tm = TaskManager(store=None)
    dm = type('D', (), {'list': lambda self: []})()
    # use mock LLM to avoid network
    agent = Agent(llm=MockLLM())
    history = ChatHistory([])
    engine = ChatEngine(agent, tm, dm, history)

    # add a task via chat
    resp = engine.handle_message('add task Write tests')
    assert 'Added task' in resp or 'added task' in resp or 'Added' in resp
    # find the new task id
    tasks = tm.list()
    assert any('Write tests' in t.text for t in tasks)
    tid = tasks[-1].id

    # edit the task via chat
    resp = engine.handle_message(f'edit task {tid} to Write better tests')
    assert 'Edited task' in resp or 'Edited' in resp or 'edited' in resp
    t = next((x for x in tm.list() if x.id == tid), None)
    assert t and 'better' in t.text.lower()

    # add a detail to the selected task (select then add detail)
    engine.handle_message(f'select task {tid}')
    resp = engine.handle_message('add detail Add unit tests for module X')
    assert 'Added detail' in resp or 'detail added' in resp or 'Added detail' in resp
    t = next((x for x in tm.list() if x.id == tid), None)
    assert t and any('unit tests' in d.lower() for d in t.details)

    # complete with confirmation flow
    resp = engine.handle_message(f'complete task {tid}')
    assert 'Please confirm' in resp
    resp = engine.handle_message('yes')
    assert 'Completed task' in resp or 'Completed' in resp
    t = next((x for x in tm.list() if x.id == tid), None)
    assert t and t.completed

    # delete with confirmation
    resp = engine.handle_message(f'delete task {tid}')
    assert 'Please confirm' in resp
    resp = engine.handle_message('yes')
    assert 'Deleted' in resp
    assert not any(x.id == tid for x in tm.list())
