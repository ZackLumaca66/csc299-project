from __future__ import annotations
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional

@dataclass
class Task:
    id: int
    text: str
    created: str
    completed: bool = False
    details: List[str] = field(default_factory=list)
    priority: int = 3
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class Note:
    id: int
    text: str
    created: str
    details: List[str] = field(default_factory=list)
    task_id: Optional[int] = None

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
