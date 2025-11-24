"""PKMS Home launcher: simple interactive home screen to access Dashboard, TUI, Chat Companion, CLI.

Run:
  python scripts/pkms_home.py

This script uses the existing TaskManager/DocumentManager and Agent/chat components to
provide a navigable home screen for the user.
"""
from __future__ import annotations
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from pkms_core.core import TaskManager, DocumentManager
from pkms_core.storage import JsonTaskStore, DocumentStore
from pkms_core.agent import Agent
from pkms_core.llm_mock import MockLLM
from pkms_core.chat import ChatEngine, ChatHistory
from pkms_core.dashboard import show_dashboard
from pkms_core.tui import run_tui


def clear_screen():
    try:
        os.system('cls' if os.name == 'nt' else 'clear')
    except Exception:
        pass


def build_managers(base_dir: str):
    demo_dir = os.path.join(base_dir, 'app_data')
    os.makedirs(demo_dir, exist_ok=True)
    tm = TaskManager(store=JsonTaskStore(os.path.join(demo_dir, 'tasks.json')))
    dm = DocumentManager(store=DocumentStore(os.path.join(demo_dir, 'docs.json')))
    return tm, dm


def chat_companion(agent: Agent, tm: TaskManager, dm: DocumentManager):
    history = ChatHistory.load()
    engine = ChatEngine(agent, tm, dm, history)
    print("\nChat companion — type '/help' for commands, '/exit' to return to home.")
    while True:
        try:
            line = input('chat> ').strip()
        except (EOFError, KeyboardInterrupt):
            print(); break
        if not line: continue
        if line in {'/exit','exit','quit'}:
            break
        if line.startswith('/help'):
            print("Commands: /select <id>, /clear, /advise, suggest tasks, summarize task <id>, summarize doc <id>, add task <text>, edit task <id> to <text>, add detail <text>, complete/delete task <id>")
            continue
        if line.startswith('/select '):
            try:
                tid = int(line.split()[1]); ok = engine.select_task(tid)
                print(f"selected {tid}" if ok else 'not found')
            except Exception:
                print('bad id')
            continue
        if line.startswith('/clear'):
            engine.clear_selection(); print('selection cleared'); continue
        # allow users to prefix commands with '/' (e.g. '/advise') — strip leading slash
        to_engine = line[1:] if line.startswith('/') else line
        resp = engine.handle_message(to_engine)
        print(resp)
        history.save()


def home():
    base = os.getcwd()
    tm, dm = build_managers(base)
    # Use MockLLM by default for local runs; if user configures a real LLM adapter, replace this.
    agent = Agent(llm=MockLLM())

    while True:
        clear_screen()
        print('*** PKMS Home ***')
        print('1) Show dashboard')
        print('2) Run TUI (quick commands)')
        print('3) Chat companion (AI assistant)')
        print('4) Run CLI (subcommands)')
        print('5) Show commands and examples')
        print('5) Exit')
        print('\nAvailable commands: add/edit/delete/complete/toggle/add detail via TUI or CLI; chat supports /advise and selection-based help.')
        choice = input('\nChoose an option [1-5]: ').strip()
        if choice == '1':
            clear_screen(); show_dashboard(tm.list(), dm.list(), agent, tasks_only=True); input('\nPress Enter to return...')
        elif choice == '2':
            clear_screen(); run_tui(tm, dm, agent)
        elif choice == '3':
            clear_screen(); chat_companion(agent, tm, dm)
        elif choice == '4':
            clear_screen(); print('CLI entrypoint: run `python -m src.cli.main` from tasks5 package or use packaged CLI.'); input('\nPress Enter to return...')
        elif choice == '5':
            clear_screen()
            print('Command reference and examples:\n')
            print('TUI examples:')
            print('  add Buy milk')
            print('  edit 2 Refactor storage layer to use sqlite by default')
            print('  desc 2 Break task into: step A; step B')
            print('  remove-detail 2 0')
            print('  toggle 3')
            print('\nChat companion examples:')
            print("  /advise                # show productivity advice for all tasks/docs")
            print('  /select 2              # focus on task id 2')
            print("  After selecting: ask natural questions about the task or type 'summarize task 2'")
            print('\nCLI: run `python -m src.cli.main create ...` or use `tasks5` package CLI when installed.')
            input('\nPress Enter to return...')
        elif choice == '6' or choice == '5':
            print('Goodbye'); break
        else:
            print('Invalid choice'); input('\nPress Enter to continue...')


if __name__ == '__main__':
    home()
