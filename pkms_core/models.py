from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import List, Dict

@dataclass
class Task:
    id: int
    text: str
    created: str
    completed: bool = False

    def to_dict(self) -> Dict:
        return asdict(self)

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
