from __future__ import annotations
from typing import List, Optional
from datetime import datetime, timezone
from .models import Task, Document
from .utils import truncate

# Threshold for focus overload warning: more than this many high-priority open tasks
FOCUS_OVERLOAD_THRESHOLD = 5

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
        now = datetime.now(timezone.utc)
        total = len(tasks)
        incomplete = len([t for t in tasks if not t.completed])
        completed = total - incomplete
        advice.append(f"Tasks: {incomplete} open / {completed} done (total {total})")
        # High-focus tasks: priority >=4 and not completed (recent and high priority)
        high_focus = [t for t in tasks if getattr(t, 'priority', 3) >= 4 and not t.completed]
        high_focus = sorted(high_focus, key=lambda t: (-getattr(t, 'priority', 3), t.id))[:3]
        if high_focus:
            advice.append("High focus: " + "; ".join(truncate(t.text, 60) for t in high_focus))

        # Quick wins: short, medium-or-higher priority tasks you can knock out fast
        QUICK_WIN_WORDS = 8
        QUICK_WIN_MIN_PRIORITY = 3
        quick_wins = [
            t for t in tasks
            if not t.completed and getattr(t, 'priority', 3) >= QUICK_WIN_MIN_PRIORITY and len(t.text.split()) <= QUICK_WIN_WORDS
        ]
        quick_wins = sorted(quick_wins, key=lambda t: (-getattr(t, 'priority', 3), t.id))[:3]
        if quick_wins:
            advice.append("Quick wins: " + "; ".join(truncate(t.text, 50) for t in quick_wins))

        # Urgent: high priority and aging beyond 7 days
        urgent = []
        for t in tasks:
            if getattr(t, 'priority', 3) >= 4 and not t.completed:
                try:
                    created = datetime.fromisoformat(t.created)
                    if created.tzinfo is None:
                        created = created.replace(tzinfo=timezone.utc)
                    age = (now - created).days
                    if age >= 7:
                        urgent.append(t)
                except Exception:
                    continue
        if urgent:
            advice.append("Urgent (high priority + aging): " + "; ".join(truncate(t.text, 50) for t in urgent[:3]))

        # Refinement candidates: priority >=3 and no details
        refinement = [t for t in tasks if getattr(t, 'priority', 3) >= 3 and not getattr(t, 'details', []) and not t.completed]
        if refinement:
            advice.append("Refine: " + "; ".join(truncate(t.text, 60) for t in refinement[:3]))

        # Stale tasks: older than 14 days
        stale = []
        for t in tasks:
            try:
                created = datetime.fromisoformat(t.created)
                if created.tzinfo is None:
                    created = created.replace(tzinfo=timezone.utc)
                age_days = (now - created).days
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
        # Focus overload: warn when too many high-priority open tasks exist
        high_open = [t for t in tasks if getattr(t, 'priority', 3) >= 4 and not t.completed]
        if len(high_open) > FOCUS_OVERLOAD_THRESHOLD:
            advice.append(f"Focus overload: {len(high_open)} high-priority tasks; consider delegating or pausing.")

        # Priority spread summary: counts of open tasks grouped by priority
        prio_counts = {}
        for t in tasks:
            if not t.completed:
                p = getattr(t, 'priority', 3)
                prio_counts[p] = prio_counts.get(p, 0) + 1
        if prio_counts:
            spread = ", ".join(f"P{p}:{prio_counts[p]}" for p in sorted(prio_counts.keys(), reverse=True))
            advice.append("Priority spread (open): " + spread)
        # Include a short doc-derived suggestions summary (count only) so callers
        # can decide whether to surface document-derived suggestions elsewhere.
        doc_suggestions = self.suggest_tasks_from_documents(docs) if docs else []
        if doc_suggestions:
            # show a concise count plus the top suggestion texts (up to 3)
            advice.append(f"Doc-derived suggestions: {len(doc_suggestions)} available.")
            top = doc_suggestions[:3]
            advice.append("Doc suggestions: " + "; ".join(truncate(s, 80) for s in top))
        # Note: we avoid exposing full document-derived suggestion text or task IDs
        # in the generic advice output to keep the dashboard concise.
        if not advice:
            advice.append("No advice available; add tasks or documents.")
        return advice

__all__ = ["Agent"]