from __future__ import annotations
import json, os
from typing import List, Dict
from .models import Task, Document
from .agent import Agent

CHAT_HISTORY_FILE = os.path.join(os.getcwd(), 'data_pkms', 'chat_history.json')

class ChatHistory:
    def __init__(self, entries: List[Dict[str,str]] | None = None):
        self.entries: List[Dict[str,str]] = entries or []
    def add(self, role: str, text: str) -> None:
        self.entries.append({"role": role, "text": text})
    def save(self) -> None:
        os.makedirs(os.path.dirname(CHAT_HISTORY_FILE), exist_ok=True)
        with open(CHAT_HISTORY_FILE,'w',encoding='utf-8') as fh:
            json.dump(self.entries, fh, indent=2)
    @classmethod
    def load(cls) -> 'ChatHistory':
        if os.path.exists(CHAT_HISTORY_FILE):
            try:
                with open(CHAT_HISTORY_FILE,'r',encoding='utf-8') as fh:
                    data = json.load(fh)
                if isinstance(data, list): return cls(data)
            except Exception:
                return cls([])
        return cls([])

class ChatEngine:
    def __init__(self, agent: Agent, task_manager, doc_manager, history: ChatHistory):
        self.agent = agent
        self.tm = task_manager
        self.dm = doc_manager
        self.history = history
        # selected task context for a chat session
        self.selected_task: Task | None = None

    def select_task(self, task_id: int) -> bool:
        task = next((t for t in self.tm.tasks if t.id == task_id), None)
        if not task:
            return False
        self.selected_task = task
        return True

    def clear_selection(self) -> None:
        self.selected_task = None

    def handle_message(self, message: str) -> str:
        self.history.add('user', message)
        msg = message.strip()
        # selection commands
        if msg.startswith('select task '):
            try:
                tid = int(msg.split()[-1])
                ok = self.select_task(tid)
                response = f"selected task {tid}" if ok else "task not found"
                self.history.add('assistant', response)
                return response
            except Exception:
                response = 'Invalid task id'
                self.history.add('assistant', response)
                return response

        if msg in {'clear selection', 'clear'}:
            self.clear_selection()
            response = 'selection cleared'
            self.history.add('assistant', response)
            return response

        # explicit summarization
        if msg.startswith('summarize task '):
            try:
                tid = int(msg.split()[-1])
                task = next((t for t in self.tm.tasks if t.id == tid), None)
                if not task:
                    response = 'Task not found'
                else:
                    response = self.agent.summarize_task(task)
            except Exception:
                response = 'Invalid task id'
            self.history.add('assistant', response)
            return response

        if msg.startswith('summarize doc '):
            try:
                did = int(msg.split()[-1])
                doc = next((d for d in self.dm.docs if d.id == did), None)
                if not doc:
                    response = 'Document not found'
                else:
                    response = self.agent.summarize_document(doc)
            except Exception:
                response = 'Invalid document id'
            self.history.add('assistant', response)
            return response

        if msg.startswith('suggest tasks'):
            suggestions = self.agent.suggest_tasks_from_documents(self.dm.list())
            if not suggestions:
                response = 'No suggestions.'
            else:
                response = '\n'.join(f"- {s}" for s in suggestions)
            self.history.add('assistant', response)
            return response

        # If a task is selected, attempt context-aware reply using LLM if available
        if self.selected_task:
            # prefer LLM if present
            llm = getattr(self.agent, 'llm', None)
            if llm and getattr(llm, 'available', lambda: False)():
                # give LLM the task context and user message
                prompt = f"Task: {self.selected_task.text}\nUser: {msg}"
                try:
                    llm_response = llm.summarize(prompt)
                    if llm_response:
                        response = llm_response
                    else:
                        response = self.agent.summarize_task(self.selected_task)
                except Exception:
                    response = self.agent.summarize_task(self.selected_task)
            else:
                # No LLM: reply with heuristic summary + simple guidance
                summary = self.agent.summarize_task(self.selected_task)
                # include simple advice lines from productivity_advice filtered for this task
                advice_lines = []
                # produce a tiny heuristic: if task is long, suggest breaking down
                if len(self.selected_task.text.split()) > 12:
                    advice_lines.append('This task looks long — consider breaking it into smaller steps.')
                response = f"Selected task {self.selected_task.id}: {summary}"
                if advice_lines:
                    response += "\n" + "\n".join(advice_lines)
            self.history.add('assistant', response)
            return response

        # default help / fallback
        response = 'Commands: select task <id>, summarize task <id>, summarize doc <id>, suggest tasks, or type a message after selecting a task.'
        self.history.add('assistant', response)
        return response

__all__ = ["ChatHistory","ChatEngine"]