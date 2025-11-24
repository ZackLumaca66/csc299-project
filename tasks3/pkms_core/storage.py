from __future__ import annotations
import json, os, sqlite3
from typing import List, Optional
from dataclasses import asdict
from .models import Task, Document

class TaskStore:
    def load(self) -> List[Task]: raise NotImplementedError
    def save_all(self, tasks: List[Task]) -> None: raise NotImplementedError
    def add(self, task: Task) -> None: raise NotImplementedError
    def update(self, task: Task) -> None: raise NotImplementedError
    def delete(self, task_id: int) -> bool: raise NotImplementedError

class JsonTaskStore(TaskStore):
    def __init__(self, path: str): self.path = path
    def load(self) -> List[Task]:
        if os.path.exists(self.path):
            try:
                with open(self.path,'r',encoding='utf-8') as fh: data=json.load(fh)
                return [Task(**t) for t in data]
            except Exception: return []
        return []
    def save_all(self, tasks: List[Task]) -> None:
        with open(self.path,'w',encoding='utf-8') as fh: json.dump([asdict(t) for t in tasks], fh, indent=2)
    def add(self, task: Task) -> None:
        tasks=self.load(); tasks.append(task); self.save_all(tasks)
    def update(self, task: Task) -> None:
        tasks=self.load();
        for i,t in enumerate(tasks):
            if t.id==task.id: tasks[i]=task; break
        self.save_all(tasks)
    def delete(self, task_id: int) -> bool:
        tasks=self.load();
        for i,t in enumerate(tasks):
            if t.id==task_id: del tasks[i]; self.save_all(tasks); return True
        return False

class SqliteTaskStore(TaskStore):
    def __init__(self, path: str):
        self.path=path; os.makedirs(os.path.dirname(path), exist_ok=True); self._ensure()
    def _conn(self): return sqlite3.connect(self.path)
    def _ensure(self):
        with self._conn() as c:
            c.execute("CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY, text TEXT, created TEXT, completed INTEGER)")
    def load(self)->List[Task]:
        with self._conn() as c:
            rows=c.execute("SELECT id,text,created,completed FROM tasks ORDER BY id ASC").fetchall()
        return [Task(id=r[0], text=r[1], created=r[2], completed=bool(r[3])) for r in rows]
    def save_all(self, tasks: List[Task])->None:
        with self._conn() as c:
            c.execute("DELETE FROM tasks")
            for t in tasks:
                c.execute("INSERT INTO tasks(id,text,created,completed) VALUES(?,?,?,?)", (t.id,t.text,t.created,int(t.completed)))
    def add(self, task: Task)->None:
        with self._conn() as c:
            c.execute("INSERT INTO tasks(id,text,created,completed) VALUES(?,?,?,?)", (task.id,task.text,task.created,int(task.completed)))
    def update(self, task: Task)->None:
        with self._conn() as c:
            c.execute("UPDATE tasks SET text=?, created=?, completed=? WHERE id=?", (task.text,task.created,int(task.completed),task.id))
    def delete(self, task_id: int)->bool:
        with self._conn() as c:
            cur=c.execute("DELETE FROM tasks WHERE id=?", (task_id,))
            return cur.rowcount>0

class DocumentStore:
    def __init__(self, path: str): self.path=path
    def load(self)->List[Document]:
        if os.path.exists(self.path):
            try:
                with open(self.path,'r',encoding='utf-8') as fh: data=json.load(fh)
                return [Document(**d) for d in data]
            except Exception: return []
        return []
    def save_all(self, docs: List[Document])->None:
        with open(self.path,'w',encoding='utf-8') as fh:
            json.dump([asdict(d) for d in docs], fh, indent=2)

def make_task_store(kind: str, base_dir: str)->TaskStore:
    data_dir=os.path.join(base_dir,'data_pkms'); os.makedirs(data_dir, exist_ok=True)
    return SqliteTaskStore(os.path.join(data_dir,'tasks.db')) if kind=='sqlite' else JsonTaskStore(os.path.join(data_dir,'tasks.json'))

def make_document_store(base_dir: str)->DocumentStore:
    data_dir=os.path.join(base_dir,'data_pkms'); os.makedirs(data_dir, exist_ok=True)
    return DocumentStore(os.path.join(data_dir,'docs.json'))
