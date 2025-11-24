"""Demo script: lightweight interactive demo of pkms chat/advise using a mock LLM when none provided.

Run:
  python scripts/demo_pkms_chat.py

This will create an in-memory small store, add example tasks and documents, then show agent suggestions
and a mock LLM summary for demonstration.
"""
import sys
import os

# Ensure repo root is on sys.path when running the script directly
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from pkms_core.agent import Agent
from pkms_core.llm import LLMAdapter
from pkms_core.llm_mock import MockLLM
from pkms_core.models import Task, Document
from pkms_core.storage import make_task_store, make_document_store
import os


def demo():
    base = os.getcwd()
    # choose mock if no key present
    adapter = LLMAdapter()
    if not adapter.available():
        print("No real LLM key found — using MockLLM for demo.")
        llm = MockLLM()
    else:
        print("LLM key detected — running with real adapter (calls will be provider-dependent).")
        llm = adapter

    agent = Agent(llm=llm)

    # small example dataset
    tasks = [
        Task(id=1, text="Write README for project", created="2025-01-01T00:00:00+00:00", completed=False),
        Task(id=2, text="Refactor storage layer to use sqlite by default", created="2025-01-02T00:00:00+00:00", completed=False),
    ]
    docs = [
        Document(id=1, title="Notes", text="TODO: add unit tests for storage\nCreate demo script to show chat/advise", tags=[], links=[], created="", updated=""),
    ]

    print("\n--- Agent Productivity Advice ---")
    advice = agent.productivity_advice(tasks, docs)
    for line in advice:
        print(line)

    print("\n--- Agent Suggestions from Documents ---")
    suggestions = agent.suggest_tasks_from_documents(docs)
    for s in suggestions:
        print("- ", s)

    print("\n--- LLM Summaries (demo) ---")
    for d in docs:
        s = llm.summarize(d.text)
        print(f"{d.title}: {s}")


if __name__ == '__main__':
    demo()
