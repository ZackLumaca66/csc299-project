from __future__ import annotations
import os, re
from datetime import datetime, timezone
from typing import List, Optional, Set, Dict, Tuple, Callable
from .models import Task, Document
from .storage import make_task_store, make_document_store, TaskStore, DocumentStore

class TaskManager:
    def __init__(self, backend: str = 'json', store: Optional[TaskStore] = None, on_toggle: Optional[Callable[[Task,bool],None]] = None):
        root = os.getcwd()
        self.store = store or make_task_store(backend, root)
        self.tasks: List[Task] = self.store.load()
        self._next_id = max([t.id for t in self.tasks], default=0) + 1
        self.on_toggle = on_toggle
    def add(self, text: str, priority: int = 3, tags: Optional[List[str]] = None) -> Task:
        tags = tags or []
        t = Task(id=self._next_id, text=text, created=datetime.now(timezone.utc).isoformat(), completed=False, details=[], priority=priority, tags=tags)
        self._next_id += 1
        self.tasks.append(t)
        try: self.store.add(t)
        except Exception: self.store.save_all(self.tasks)
        return t
    def add_detail(self, task_id: int, detail: str) -> Optional[Task]:
        for t in self.tasks:
            if t.id == task_id:
                t.details.append(detail)
                try: self.store.update(t)
                except Exception: self.store.save_all(self.tasks)
                return t
        return None
    def remove_detail(self, task_id: int, index: int) -> Optional[Task]:
        for t in self.tasks:
            if t.id == task_id:
                try:
                    del t.details[index]
                    try: self.store.update(t)
                    except Exception: self.store.save_all(self.tasks)
                    return t
                except Exception:
                    return None
        return None
    def list(self, include_completed: bool = True) -> List[Task]:
        return list(self.tasks) if include_completed else [t for t in self.tasks if not t.completed]
    def search(self, query: str) -> List[Task]:
        q = query.lower(); return [t for t in self.tasks if q in t.text.lower()]
    def toggle(self, task_id: int) -> Optional[Task]:
        for t in self.tasks:
            if t.id == task_id:
                t.completed = not t.completed
                try: self.store.update(t)
                except Exception: self.store.save_all(self.tasks)
                if self.on_toggle and t.completed: self.on_toggle(t, t.completed)
                return t
        return None
    def set_completed(self, task_id: int, completed: bool) -> Optional[Task]:
        for t in self.tasks:
            if t.id == task_id:
                was = t.completed; t.completed = bool(completed)
                try: self.store.update(t)
                except Exception: self.store.save_all(self.tasks)
                if self.on_toggle and (not was and t.completed): self.on_toggle(t, t.completed)
                return t
        return None
    def delete(self, task_id: int) -> bool:
        for i,t in enumerate(self.tasks):
            if t.id == task_id:
                del self.tasks[i]
                try:
                    if not self.store.delete(t.id): self.store.save_all(self.tasks)
                except Exception: self.store.save_all(self.tasks)
                return True
        return False
    def export(self, out_path: str) -> None:
        import json
        with open(out_path,'w',encoding='utf-8') as fh: json.dump([t.__dict__ for t in self.tasks], fh, indent=2)
    def edit(self, task_id: int, new_text: str) -> Optional[Task]:
        """Edit the text of an existing task and persist the change."""
        for t in self.tasks:
            if t.id == task_id:
                t.text = new_text
                try: self.store.update(t)
                except Exception: self.store.save_all(self.tasks)
                return t
        return None

class DocumentManager:
    _STOPWORDS = {"the","and","or","of","a","to","in","for","on","is","it"}
    def __init__(self, store: Optional[DocumentStore] = None):
        root = os.getcwd()
        self.store = store or make_document_store(root)
        self.docs: List[Document] = self.store.load()
        self._next_id = max([d.id for d in self.docs], default=0) + 1
        self._index: Dict[str, Set[int]] = {}
        self._rebuild_index()
    def _tokenize(self, text: str) -> List[str]:
        tokens = re.split(r"[^A-Za-z0-9]+", text.lower())
        return [t for t in tokens if t and t not in self._STOPWORDS]
    def _index_doc(self, doc: Document):
        for tok in self._tokenize(doc.title + " " + doc.text + " " + " ".join(doc.tags)):
            self._index.setdefault(tok, set()).add(doc.id)
    def _rebuild_index(self):
        self._index = {}
        for d in self.docs: self._index_doc(d)
    def add(self, title: str, text: str, tags: Optional[List[str]] = None, links: Optional[List[str]] = None) -> Document:
        tags = tags or []; links = links or []
        now = datetime.now(timezone.utc).isoformat()
        doc = Document(id=self._next_id, title=title, text=text, tags=tags, links=links, created=now, updated=now)
        self._next_id += 1
        self.docs.append(doc)
        self.store.save_all(self.docs)
        self._index_doc(doc)
        return doc
    def list(self) -> List[Document]: return list(self.docs)
    def get(self, doc_id: int) -> Optional[Document]:
        for d in self.docs:
            if d.id == doc_id: return d
        return None
    def delete(self, doc_id: int) -> bool:
        for i,d in enumerate(self.docs):
            if d.id == doc_id:
                del self.docs[i]
                self.store.save_all(self.docs)
                self._rebuild_index()
                return True
        return False
    def search(self, query: str) -> List[Document]:
        q_tokens = self._tokenize(query)
        if not q_tokens:
            q = query.lower()
            return [d for d in self.docs if q in d.title.lower() or q in d.text.lower() or any(q in t.lower() for t in d.tags)]
        scores: Dict[int,int] = {}
        for tok in q_tokens:
            ids = self._index.get(tok);
            if not ids: continue
            for did in ids: scores[did] = scores.get(did,0) + 1
        if not scores:
            q = query.lower()
            return [d for d in self.docs if q in d.title.lower() or q in d.text.lower() or any(q in t.lower() for t in d.tags)]
        ordered: List[Tuple[int,int]] = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
        by_id = {d.id: d for d in self.docs}
        return [by_id[i] for i,_s in ordered if i in by_id]
