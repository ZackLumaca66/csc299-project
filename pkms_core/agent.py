from __future__ import annotations
from typing import List, Optional
from datetime import datetime, timezone
from .models import Task, Document
from .utils import truncate

_VERBS = {"add","create","implement","write","refactor","plan","review","test","fix","update","remove","design"}

class Agent:
    """Rule/heuristic agent with optional LLM adapter."""
    def __init__(self, llm: Optional[object] = None):
        self.llm = llm
    def summarize_task(self, task: Task) -> str:
        if self.llm and getattr(self.llm, 'available', lambda: False)():
            llm_text = self.llm.summarize(task.text)
            if llm_text: return llm_text
        words = task.text.strip().split()
        return " ".join(words[:7]) + ("..." if len(words) > 7 else "")
    def summarize_document(self, doc: Document) -> str:
        if self.llm and getattr(self.llm, 'available', lambda: False)():
            llm_text = self.llm.summarize(doc.text)
            if llm_text: return f"{doc.title}: {llm_text}"
        first_line = doc.text.strip().splitlines()[0] if doc.text.strip() else doc.title
        words = first_line.split()
        return f"{doc.title}: {' '.join(words[:10])}{'...' if len(words)>10 else ''}"
    def suggest_tasks_from_document(self, doc: Document) -> List[str]:
        suggestions: List[str] = []
        for line in doc.text.splitlines():
            l = line.strip()
            if not l: continue
            upper = l.upper()
            if "TODO" in upper or upper.startswith("TODO:"):
                suggestions.append(l.replace("TODO:", "").replace("TODO", "").strip())
                continue
            first = l.split()[0].lower()
            if first in _VERBS:
                suggestions.append(l)
        return suggestions
    def suggest_tasks_from_documents(self, docs: List[Document]) -> List[str]:
        out: List[str] = []
        for d in docs:
            out.extend(self.suggest_tasks_from_document(d))
        # de-duplicate preserving order
        seen = set(); dedup = []
        for s in out:
            if s not in seen:
                dedup.append(s); seen.add(s)
        return dedup

    # Productivity / advice layer
    def productivity_advice(self, tasks: List[Task], docs: List[Document]) -> List[str]:
        advice: List[str] = []
        total = len(tasks)
        incomplete = len([t for t in tasks if not t.completed])
        completed = total - incomplete
        advice.append(f"Tasks: {incomplete} open / {completed} done (total {total})")
        # High-focus tasks: priority >=4 and not completed
        high_focus = [t for t in tasks if getattr(t, 'priority', 3) >= 4 and not t.completed]
        high_focus = sorted(high_focus, key=lambda t: (-getattr(t, 'priority', 3), t.id))[:3]
        if high_focus:
            advice.append("High focus: " + "; ".join(truncate(t.text, 60) for t in high_focus))

        # Refinement candidates: priority >=3 and no details
        refinement = [t for t in tasks if getattr(t, 'priority', 3) >= 3 and not getattr(t, 'details', []) and not t.completed]
        if refinement:
            advice.append("Refine: " + "; ".join(truncate(t.text, 60) for t in refinement[:3]))

        # Stale tasks: older than 14 days
        stale = []
        for t in tasks:
            try:
                created = datetime.fromisoformat(t.created)
                age_days = (datetime.now(timezone.utc) - created).days
                if age_days > 14 and not t.completed:
                    stale.append(t)
            except Exception:
                continue
        if stale:
            advice.append(f"Stale: {len(stale)} tasks older than 14 days.")

        # Identify long tasks (heuristic: > 12 words) as candidates for breaking down
        long_tasks = [t for t in tasks if len(t.text.split()) > 12 and not t.completed]
        if long_tasks:
            advice.append(f"Break down {len(long_tasks)} long tasks (>{12} words) for momentum.")
        # Include a short doc-derived suggestions summary (count only) so callers
        # can decide whether to surface document-derived suggestions elsewhere.
        doc_suggestions = self.suggest_tasks_from_documents(docs) if docs else []
        if doc_suggestions:
            advice.append(f"Doc-derived suggestions: {len(doc_suggestions)} available.")
        # Note: we avoid exposing full document-derived suggestion text or task IDs
        # in the generic advice output to keep the dashboard concise.
        if not advice:
            advice.append("No advice available; add tasks or documents.")
        return advice

__all__ = ["Agent"]