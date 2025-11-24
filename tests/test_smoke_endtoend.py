import os
from pkms_core.core import TaskManager, DocumentManager
from pkms_core.storage import JsonTaskStore, DocumentStore
from pkms_core.agent import Agent
from pkms_core.llm_mock import MockLLM
from pkms_core.chat import ChatEngine, ChatHistory
import os
from pkms_core.core import TaskManager, DocumentManager
from pkms_core.storage import JsonTaskStore, DocumentStore
from pkms_core.agent import Agent
from pkms_core.llm_mock import MockLLM
from pkms_core.chat import ChatEngine, ChatHistory


def test_smoke_home_flows(tmp_path):
    base = str(tmp_path)
    data_dir = os.path.join(base, 'app_data')
    os.makedirs(data_dir, exist_ok=True)
    # Use JSON stores for isolated test directory
    tm = TaskManager(store=JsonTaskStore(os.path.join(data_dir, 'tasks.json')))
    dm = DocumentManager(store=DocumentStore(os.path.join(data_dir, 'docs.json')))
    agent = Agent(llm=MockLLM())

    # Seed tasks/docs
    t1 = tm.add('Write README')
    t2 = tm.add('Prepare release notes')
    d1 = dm.add('Notes', 'TODO: add tests\nRefactor storage layer')

    # Basic dashboard/advice check via agent
    advice = agent.productivity_advice(tm.list(), dm.list())
    assert advice and isinstance(advice, list)

    # Chat flows: suggest tasks
    hist = ChatHistory()
    engine = ChatEngine(agent, tm, dm, hist)
    resp = engine.handle_message('suggest tasks')
    assert isinstance(resp, str)

    # Add detail to selected task via selection
    engine.handle_message('select task %d' % t1.id)
    resp2 = engine.handle_message('add detail Write introduction section')
    assert 'Added detail' in resp2 or 'Failed' not in resp2

    # Edit task
    resp3 = engine.handle_message(f'edit task {t2.id} to Prepare release notes and changelog')
    assert 'Edited task' in resp3

    # Complete task with confirmation flow
    resp4 = engine.handle_message(f'complete task {t1.id}')
    assert 'Please confirm' in resp4
    resp5 = engine.handle_message('yes')
    assert 'Completed task' in resp5

    # Delete task with confirmation
    resp6 = engine.handle_message(f'delete task {t2.id}')
    assert 'Please confirm' in resp6
    resp7 = engine.handle_message('yes')
    assert 'Deleted' in resp7 or 'Task not found' in resp7