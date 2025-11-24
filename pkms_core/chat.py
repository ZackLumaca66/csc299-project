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
    def handle_message(self, message: str) -> str:
        self.history.add('user', message)
        msg = message.strip()
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
        elif msg.startswith('summarize doc '):
            try:
                did = int(msg.split()[-1])
                doc = next((d for d in self.dm.docs if d.id == did), None)
                if not doc:
                    response = 'Document not found'
                else:
                    response = self.agent.summarize_document(doc)
            except Exception:
                response = 'Invalid document id'
        elif msg.startswith('suggest tasks'):
            suggestions = self.agent.suggest_tasks_from_documents(self.dm.list())
            if not suggestions:
                response = 'No suggestions.'
            else:
                response = '\n'.join(f"- {s}" for s in suggestions)
        else:
            # default echo + simple guidance
            response = 'Commands: summarize task <id>, summarize doc <id>, suggest tasks'
        self.history.add('assistant', response)
        return response

__all__ = ["ChatHistory","ChatEngine"]