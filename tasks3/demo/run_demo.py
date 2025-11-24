"""Scripted demo for tasks3_cli: adds tasks/docs, runs chat queries, toggles tasks to show neko healing.
Run this script to produce a short demo run that can be captured for a screencast.
"""
from tasks3_cli.core import TaskManager
from tasks3_cli.document import DocumentManager
from tasks3_cli.neko import NekoManager
from tasks3_cli.agent import AgentStub

def main():
    print("Running scripted demo for tasks3_cli")
    tm = TaskManager()
    docs = DocumentManager()
    neko = NekoManager()
    agent = AgentStub()

    # Reset state for demo
    tm.tasks = []
    tm._next_id = 1
    tm.save()
    docs.docs = []
    docs._next_id = 1
    docs.save()
    neko.reset()

    print("Adding documents...")
    docs.add("Python notes", "This document contains notes about Python testing and pytest.", tags=["python","testing"])
    docs.add("PKMS design", "Notes on linking documents and tagging for PKMS.", tags=["pkms","design"])

    print("Adding tasks...")
    tm.add("Write unit tests for documents")
    tm.add("Record demo screencast")

    print("Neko status before completing a task:")
    print(neko.render())

    print("Agent: list docs")
    print(agent.respond("list documents", task_manager=tm, doc_manager=docs))

    print("Agent: summarize docs")
    print(agent.respond("summarize documents", task_manager=tm, doc_manager=docs))

    print("Completing a task to heal neko...")
    tasks = tm.list()
    if tasks:
        tm.toggle(tasks[0].id)

    print("Neko status after completing a task:")
    print(neko.render())

    print("Demo finished. You can record this session for a short screencast.")

if __name__ == '__main__':
    main()
