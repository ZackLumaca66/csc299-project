import sys
import os

# ensure local src is importable
ROOT = os.path.join(os.getcwd(), "tasks3", "src")
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tasks3_cli.agent import AgentStub
from tasks3_cli.core import TaskManager
from tasks3_cli.document import DocumentManager


def test_agent_lists_tasks_and_docs(tmp_path):
    tm_path = str(tmp_path / "tasks.json")
    dm_path = str(tmp_path / "docs.json")
    tm = TaskManager(path=tm_path)
    dm = DocumentManager(path=dm_path)

    tm.add("write unit tests")
    dm.add("Note", "Some detail", tags=["example"]) 

    agent = AgentStub()
    resp_tasks = agent.respond("show my tasks", task_manager=tm, doc_manager=dm)
    assert "write unit tests" in resp_tasks

    resp_docs = agent.respond("list documents", task_manager=tm, doc_manager=dm)
    assert "Note" in resp_docs

    resp_other = agent.respond("hello there", task_manager=tm, doc_manager=dm)
    assert "I can help with your tasks and documents" in resp_other
