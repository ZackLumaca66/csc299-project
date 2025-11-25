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
try:
    from pkms_core.llm_openai import OpenAIAdapter  # type: ignore
except Exception:
    OpenAIAdapter = None  # type: ignore
from pkms_core.models import Task, Document
from pkms_core.storage import JsonTaskStore, DocumentStore
from pkms_core.chat import ChatEngine, ChatHistory
from pkms_core.core import TaskManager, DocumentManager
import os


def demo():
    base = os.getcwd()
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--llm", choices=["auto", "openai", "mock"], default="auto", help="Force LLM adapter selection: openai|mock|auto (default).")
    args, _ = parser.parse_known_args()

    # choose adapter according to flag or auto-detect
    if args.llm == "openai":
        if OpenAIAdapter is None:
            print("OpenAI adapter not available in this environment; falling back to MockLLM.")
            llm = MockLLM()
        else:
            oa = OpenAIAdapter()
            if oa.available():
                print("Using OpenAIAdapter as requested.")
                llm = oa
            else:
                print("OpenAIAdapter not configured (missing key) — using MockLLM.")
                llm = MockLLM()
    elif args.llm == "mock":
        print("Using MockLLM as requested.")
        llm = MockLLM()
    else:
        # auto-detect
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

    # Demo interactive chat backed by simple local stores
    demo_dir = os.path.join(base, 'app_data')
    os.makedirs(demo_dir, exist_ok=True)
    tm = TaskManager(store=JsonTaskStore(os.path.join(demo_dir, 'tasks.json')))
    dm = DocumentManager(store=DocumentStore(os.path.join(demo_dir, 'docs.json')))
    # seed demo stores (if empty)
    if not tm.tasks:
        for t in tasks: tm.add(t.text)
    if not dm.docs:
        for d in docs: dm.add(d.title, d.text, tags=d.tags)

    history = ChatHistory.load()
    engine = ChatEngine(agent, tm, dm, history)
    print('\n--- Interactive Chat Demo ---')
    print("Type '/select <id>' to choose a task, or just type questions after selecting a task. Ctrl-C or '/exit' to quit.")
    while True:
        try:
            line = input('chat> ').strip()
        except (EOFError, KeyboardInterrupt):
            print(); break
        if not line: continue
        if line in {'/exit','exit','quit'}: break
        if line.startswith('/select '):
            try:
                tid = int(line.split()[1]); ok = engine.select_task(tid)
                print(f"selected {tid}" if ok else 'not found')
            except Exception:
                print('bad id')
            continue
        if line.startswith('/help'):
            print("Commands: /select <id>, /clear, /exit. After selecting a task, ask about the task or type 'suggest tasks'.")
            continue
        if line.startswith('/clear'):
            engine.clear_selection(); print('selection cleared'); continue
        # allow leading slash for convenience (e.g. '/advise')
        to_engine = line[1:] if line.startswith('/') else line
        resp = engine.handle_message(to_engine)
        print(resp)
        history.save()


def demo_notes_snippet():
    """Small non-interactive snippet demonstrating notes usage in demo."""
    base = os.getcwd()
    demo_dir = os.path.join(base, 'app_data')
    os.makedirs(demo_dir, exist_ok=True)
    print('\n--- Notes Demo Snippet ---')
    # create a simple mock LLM agent for the snippet
    from pkms_core.llm_mock import MockLLM
    from pkms_core.agent import Agent
    from pkms_core.storage import add_note, list_notes
    from pkms_core.core import TaskManager, DocumentManager

    llm = MockLLM()
    agent_local = Agent(llm=llm)
    n = add_note('json', base, 'Capture demo note: prioritize tests')
    print(f'Created note {n.id}: {n.text}')
    notes = list_notes('json', base)
    print(f'Notes count: {len(notes)}; recent: {notes[-1].text[:80] if notes else ""}')
    # show advise with note context by starting chat engine briefly
    tm = TaskManager(store=JsonTaskStore(os.path.join(demo_dir, 'tasks.json')))
    dm = DocumentManager(store=DocumentStore(os.path.join(demo_dir, 'docs.json')))
    history = ChatHistory.load()
    engine = ChatEngine(agent_local, tm, dm, history)
    try:
        engine.select_note(n.id)
        resp = engine.handle_message('advise')
        print('\nAdvise output (with note context):')
        print(resp)
    except Exception as e:
        print('Notes demo failed:', e)


if __name__ == '__main__':
    demo()
    try:
        demo_notes_snippet()
    except Exception:
        pass
