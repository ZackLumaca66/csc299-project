"""Local stub agent adapter — no external APIs required.
Provides simple, rule-based responses using the existing TaskManager and DocumentManager.
"""
from __future__ import annotations

from typing import Any


class AgentStub:
    """A tiny local agent that answers simple queries about tasks and documents."""

    def respond(self, query: str, task_manager: Any = None, doc_manager: Any = None) -> str:
        q = query.lower().strip()
        if not q:
            return "I didn't get a question — try asking about your tasks or documents."

        if "task" in q or "todo" in q:
            tasks = task_manager.list() if task_manager else []
            if not tasks:
                return "You have no tasks. Use 'add <text>' to create one."
            lines = [f"{t.id}: {t.text} [{'done' if t.completed else 'open'}]" for t in tasks]
            return "Here are your tasks:\n" + "\n".join(lines)

        if "doc" in q or "note" in q or "document" in q:
            docs = doc_manager.list() if doc_manager else []
            if not docs:
                return "You have no documents. Use 'doc add <title> <text>' to create one."
            lines = [f"{d.id}: {d.title} [tags: {', '.join(d.tags)}]" for d in docs]
            return "Here are your documents:\n" + "\n".join(lines)

        # Support simple summarization requests like 'summarize docs about python' or 'summarize tasks'
        if q.startswith("summarize") or "summary" in q:
            # If user asked for docs summary
            if "doc" in q or "note" in q or "document" in q:
                docs = doc_manager.list() if doc_manager else []
                if not docs:
                    return "No documents to summarize."
                # naive summarization: list top matches and give one-line summary
                titles = [d.title for d in docs[:5]]
                summary = f"Found {len(docs)} documents. Top titles: {', '.join(titles)}."
                # include a short combined snippet from the first docs
                snippets = []
                for d in docs[:3]:
                    text_snip = d.text[:120].replace('\n',' ') + ("..." if len(d.text) > 120 else "")
                    snippets.append(f"[{d.title}] {text_snip}")
                return summary + "\n\n" + "\n".join(snippets)

            # Summarize tasks
            if "task" in q or "todo" in q:
                tasks = task_manager.list() if task_manager else []
                if not tasks:
                    return "No tasks to summarize."
                open_tasks = [t for t in tasks if not t.completed]
                done_tasks = [t for t in tasks if t.completed]
                s = f"You have {len(tasks)} tasks ({len(open_tasks)} open, {len(done_tasks)} done)."
                # produce bullet list of up to 5 open task texts
                bullets = [f"- {t.text}" for t in open_tasks[:5]]
                return s + "\n" + "\n".join(bullets)

        # Basic fallback: echo and suggest capabilities
        return (
            "I can help with your tasks and documents. Try 'chat tasks' or 'chat docs', "
            "or ask 'summarize docs' or 'summarize tasks'."
        )
