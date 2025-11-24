"""Simple Document (PKMS) model and manager.
Stores documents in JSON at `data/docs.json` with fields: id, title, text, tags, links, created, updated.
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import List, Optional, Dict, Set, Tuple


@dataclass
class Document:
    id: int
    title: str
    text: str
    tags: List[str]
    links: List[str]
    created: str
    updated: str

    def to_dict(self) -> Dict:
        return asdict(self)


class DocumentManager:
    def __init__(self, path: Optional[str] = None):
        root = os.getcwd()
        data_dir = os.path.join(root, "data")
        os.makedirs(data_dir, exist_ok=True)
        self.path = path or os.path.join(data_dir, "docs.json")
        self.docs: List[Document] = []
        self._next_id = 1
        # Inverted index: token -> set(doc_id)
        self._index: Dict[str, Set[int]] = {}
        self.load()

    def load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                self.docs = [Document(**d) for d in data]
                if self.docs:
                    self._next_id = max(d.id for d in self.docs) + 1
                else:
                    self._next_id = 1
                self._rebuild_index()
            except Exception:
                self.docs = []
                self._next_id = 1
                self._index = {}
        else:
            self.docs = []
            self._next_id = 1
            self._index = {}

    def save(self):
        with open(self.path, "w", encoding="utf-8") as fh:
            json.dump([d.to_dict() for d in self.docs], fh, indent=2)

    def add(self, title: str, text: str, tags: Optional[List[str]] = None, links: Optional[List[str]] = None) -> Document:
        tags = tags or []
        links = links or []
        now = datetime.now(timezone.utc).isoformat()
        doc = Document(id=self._next_id, title=title, text=text, tags=tags, links=links, created=now, updated=now)
        self._next_id += 1
        self.docs.append(doc)
        self.save()
        self._index_doc(doc)
        return doc

    def list(self) -> List[Document]:
        return list(self.docs)

    def get(self, doc_id: int) -> Optional[Document]:
        for d in self.docs:
            if d.id == doc_id:
                return d
        return None

    def search(self, query: str) -> List[Document]:
        q = query.lower()
        results: List[Document] = []
        for d in self.docs:
            if q in d.title.lower() or q in d.text.lower() or any(q in t.lower() for t in d.tags):
                results.append(d)
        return results

    def delete(self, doc_id: int) -> bool:
        for i, d in enumerate(self.docs):
            if d.id == doc_id:
                del self.docs[i]
                self.save()
                self._remove_doc_from_index(doc_id)
                return True
        return False

    # ---------------- Indexing & Search Enhancements -----------------
    _STOPWORDS = {"the", "and", "or", "of", "a", "to", "in", "for", "on", "is", "it"}

    def _tokenize(self, text: str) -> List[str]:
        # Split on non-alphanumeric, lowercase, filter stopwords & empties
        tokens = re.split(r"[^A-Za-z0-9]+", text.lower())
        return [t for t in tokens if t and t not in self._STOPWORDS]

    def _rebuild_index(self):
        self._index = {}
        for d in self.docs:
            self._index_doc(d)

    def _index_doc(self, doc: Document):
        tokens = self._tokenize(doc.title + " " + doc.text + " " + " ".join(doc.tags))
        for tok in tokens:
            bucket = self._index.setdefault(tok, set())
            bucket.add(doc.id)

    def _remove_doc_from_index(self, doc_id: int):
        for tok, ids in list(self._index.items()):
            if doc_id in ids:
                ids.remove(doc_id)
                if not ids:
                    del self._index[tok]

    def search(self, query: str) -> List[Document]:  # type: ignore[override]
        """Ranked search: token match score (TF style) across title/text/tags.

        - Tokenize query; accumulate scores by counting matched tokens.
        - Fallback: if no tokens found via index, do substring search (legacy behavior).
        """
        q_tokens = self._tokenize(query)
        if not q_tokens:
            # legacy fallback substring search
            q = query.lower()
            results = [d for d in self.docs if q in d.title.lower() or q in d.text.lower() or any(q in t.lower() for t in d.tags)]
            return results
        scores: Dict[int, int] = {}
        for tok in q_tokens:
            ids = self._index.get(tok)
            if not ids:
                continue
            for did in ids:
                scores[did] = scores.get(did, 0) + 1
        if not scores:
            # fallback to substring search if index yields nothing
            q = query.lower()
            return [d for d in self.docs if q in d.title.lower() or q in d.text.lower() or any(q in t.lower() for t in d.tags)]
        # Sort by score desc then id asc for stability
        ordered: List[Tuple[int, int]] = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
        by_id = {d.id: d for d in self.docs}
        return [by_id[doc_id] for doc_id, _score in ordered if doc_id in by_id]
