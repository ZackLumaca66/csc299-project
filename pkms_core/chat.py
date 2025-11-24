from __future__ import annotations
import json
import os
from typing import List, Dict, Optional

from .models import Task, Document
from .agent import Agent

CHAT_HISTORY_FILE = os.path.join(os.getcwd(), "data_pkms", "chat_history.json")


class ChatHistory:
    def __init__(self, entries: Optional[List[Dict[str, str]]] = None):
        self.entries: List[Dict[str, str]] = entries or []

    def add(self, role: str, text: str) -> None:
        self.entries.append({"role": role, "text": text})

    def save(self) -> None:
        os.makedirs(os.path.dirname(CHAT_HISTORY_FILE), exist_ok=True)
        with open(CHAT_HISTORY_FILE, "w", encoding="utf-8") as fh:
            json.dump(self.entries, fh, indent=2)

    @classmethod
    def load(cls) -> "ChatHistory":
        if os.path.exists(CHAT_HISTORY_FILE):
            try:
                with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                if isinstance(data, list):
                    return cls(data)
            except Exception:
                return cls([])
        return cls([])


class ChatEngine:
    """Full-feature chat engine supporting suggestions, summaries, CRUD and confirmations."""

    def __init__(self, agent: Agent, task_manager, doc_manager, history: ChatHistory):
        self.agent = agent
        self.tm = task_manager
        self.dm = doc_manager
        self.history = history
        self.selected_task: Optional[Task] = None
        self._pending_confirmation: Optional[Dict[str, int]] = None

    def select_task(self, task_id: int) -> bool:
        # Accept either a real task id or a 1-based list index for user convenience.
        # First try to find by persistent id.
        task = next((t for t in self.tm.tasks if t.id == task_id), None)
        if task:
            self.selected_task = task
            return True
        # Fallback: treat task_id as 1-based index into the current list
        try:
            idx = int(task_id)
            if 1 <= idx <= len(self.tm.tasks):
                self.selected_task = self.tm.tasks[idx-1]
                return True
        except Exception:
            pass
        return False

    def clear_selection(self) -> None:
        self.selected_task = None

    def handle_message(self, message: str) -> str:
        self.history.add("user", message)
        msg = message.strip()

        # Confirmations
        if msg.lower() in {"yes", "y", "no", "n"} and self._pending_confirmation:
            pending = self._pending_confirmation
            self._pending_confirmation = None
            if msg.lower() in {"no", "n"}:
                response = "Cancelled."
                self.history.add("assistant", response)
                return response
            action = pending.get("action")
            tid = pending.get("task_id")
            if action == "delete":
                ok = self.tm.delete(tid)
                response = "Deleted" if ok else "Task not found"
            elif action == "complete":
                t = self.tm.set_completed(tid, True)
                response = f"Completed task {t.id}" if t else "Task not found"
            else:
                response = "Unknown pending action."
            self.history.add("assistant", response)
            return response

        # Selection
        if msg.startswith("select task "):
            try:
                tid = int(msg.split()[-1])
                ok = self.select_task(tid)
                response = f"selected task {tid}" if ok else "task not found"
            except Exception:
                response = "Invalid task id"
            self.history.add("assistant", response)
            return response

        if msg in {"clear selection", "clear"}:
            self.clear_selection()
            response = "selection cleared"
            self.history.add("assistant", response)
            return response

        # Suggest tasks
        if msg.startswith("suggest tasks"):
            suggestions = self.agent.suggest_tasks_from_documents(self.dm.list()) if hasattr(self.agent, 'suggest_tasks_from_documents') else []
            response = "\n".join(suggestions) if suggestions else "No suggestions."
            self.history.add("assistant", response)
            return response

        # Advice for all tasks/documents
        if msg.lower() in {"advise", "advice", "advise all", "productivity"}:
            # If an LLM is available, ask it for a concise, user-facing advice message.
            llm = getattr(self.agent, 'llm', None)
            tasks = self.tm.list()
            docs = self.dm.list()
            if llm and getattr(llm, 'available', lambda: False)():
                # Build a short prompt summarizing counts and top task texts
                summary_lines = [f"You are an assistant providing concise productivity advice."]
                summary_lines.append(f"Tasks: {len([t for t in tasks if not t.completed])} open / {len([t for t in tasks if t.completed])} done (total {len(tasks)})")
                # include up to 3 task summaries (no internal ids)
                for t in tasks[:3]:
                    summary_lines.append(f"- {t.text}")
                # Ask the LLM for a concise, prioritized list.
                # Request numbered, one-line suggestions with an optional 1-2 word rationale.
                prompt = (
                    "\n".join(summary_lines)
                    + "\nProvide 3 prioritized, one-line suggestions as a numbered list (1., 2., 3.)."
                    + " Keep tone concise and practical; each suggestion should be ~10-15 words and may include a short rationale in parentheses."
                    + " Do not list internal IDs or verbatim document action lists."
                )
                try:
                    llm_resp = llm.summarize(prompt)
                    if llm_resp:
                        response = llm_resp
                    else:
                        advice_lines = self.agent.productivity_advice(tasks, docs)
                        response = "\n".join(advice_lines)
                except Exception:
                    advice_lines = self.agent.productivity_advice(tasks, docs)
                    response = "\n".join(advice_lines)
            else:
                # Fall back to the simpler heuristic advice (which now avoids doc-derived lists)
                advice_lines = self.agent.productivity_advice(tasks, docs)
                response = "\n".join(advice_lines)
            self.history.add("assistant", response)
            return response

        # Summaries
        if msg.startswith("summarize doc "):
            try:
                did = int(msg.split()[-1])
                doc = next((d for d in getattr(self.dm, 'docs', []) if d.id == did), None)
                response = f"{doc.title}: {self.agent.summarize_document(doc)}" if doc else "Document not found"
            except Exception:
                response = "Invalid document id"
            self.history.add("assistant", response)
            return response

        if msg.startswith("summarize task "):
            try:
                tid = int(msg.split()[-1])
                task = next((t for t in self.tm.tasks if t.id == tid), None)
                response = self.agent.summarize_task(task) if task else "Task not found"
            except Exception:
                response = "Invalid task id"
            self.history.add("assistant", response)
            return response

        # Add task
        if msg.startswith("add task "):
            text = msg[len("add task "):].strip()
            if not text:
                response = "No task text provided."
            else:
                t = self.tm.add(text)
                response = f"Added task {t.id}: {t.text}"
            self.history.add("assistant", response)
            return response

        # Edit task
        if msg.startswith("edit task "):
            try:
                if " to " in msg:
                    left, new_text = msg.split(" to ", 1)
                    tid = int(left.split()[-1])
                    new_text = new_text.strip()
                    if not new_text:
                        response = "No new text provided."
                    else:
                        t = self.tm.edit(tid, new_text)
                        response = f"Edited task {t.id}: {t.text}" if t else "Task not found"
                else:
                    response = "Usage: edit task <id> to <new text>"
            except Exception:
                response = "Invalid command or id"
            self.history.add("assistant", response)
            return response

        # Add detail to id
        if msg.startswith("add detail to task "):
            try:
                if ":" in msg:
                    left, detail = msg.split(":", 1)
                    tid = int(left.split()[-1])
                    detail = detail.strip()
                    if detail:
                        t = self.tm.add_detail(tid, detail)
                        response = f"Added detail to task {t.id}" if t else "Task not found"
                    else:
                        response = "No detail provided."
                else:
                    response = "Usage: add detail to task <id>: <detail>"
            except Exception:
                response = "Invalid command or id"
            self.history.add("assistant", response)
            return response

        # Add detail to selected
        if msg.startswith("add detail "):
            if self.selected_task:
                detail = msg[len("add detail "):].strip()
                if detail:
                    t = self.tm.add_detail(self.selected_task.id, detail)
                    response = f"Added detail to task {t.id}" if t else "Failed to add detail"
                else:
                    response = "No detail provided."
            else:
                response = "No task selected. Use 'select task <id>' first or use 'add detail to task <id>: <text>'"
            self.history.add("assistant", response)
            return response

        # Complete (confirmation)
        if msg.startswith("complete task "):
            try:
                tid = int(msg.split()[-1])
                self._pending_confirmation = {"action": "complete", "task_id": tid}
                response = f"Please confirm: reply 'yes' to complete task {tid}, or 'no' to cancel."
            except Exception:
                response = "Invalid task id"
            self.history.add("assistant", response)
            return response

        # Delete (confirmation)
        if msg.startswith("delete task "):
            try:
                tid = int(msg.split()[-1])
                self._pending_confirmation = {"action": "delete", "task_id": tid}
                response = f"Please confirm: reply 'yes' to delete task {tid}, or 'no' to cancel."
            except Exception:
                response = "Invalid task id"
            self.history.add("assistant", response)
            return response

        # Contextual reply if selected task
        if self.selected_task:
            llm = getattr(self.agent, 'llm', None)
            if llm and getattr(llm, 'available', lambda: False)():
                prompt = f"Task: {self.selected_task.text}\nUser: {msg}"
                try:
                    llm_resp = llm.summarize(prompt)
                    response = llm_resp if llm_resp else self.agent.summarize_task(self.selected_task)
                except Exception:
                    response = self.agent.summarize_task(self.selected_task)
            else:
                summary = self.agent.summarize_task(self.selected_task)
                advice_lines: List[str] = []
                if len(self.selected_task.text.split()) > 12:
                    advice_lines.append("This task looks long — consider breaking it into smaller steps.")
                response = f"Selected task {self.selected_task.id}: {summary}"
                if advice_lines:
                    response += "\n" + "\n".join(advice_lines)
            self.history.add("assistant", response)
            return response

        # Fallback help
        response = "Commands: suggest tasks | summarize doc <id> | summarize task <id> | select task <id> | add task <text> | edit task <id> to <text> | add detail <text> | complete/delete task <id>."
        self.history.add("assistant", response)
        return response


__all__ = ["ChatHistory", "ChatEngine"]
