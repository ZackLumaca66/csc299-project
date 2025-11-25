from __future__ import annotations
import json, os, sqlite3
from typing import List, Optional
from dataclasses import asdict
from .models import Task, Document, Note
from .utils import map_display_index

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
                # Backfill missing fields (priority, tags) are handled by Task defaults
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
            c.execute("CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY, text TEXT, created TEXT, completed INTEGER, details TEXT, priority INTEGER DEFAULT 3, tags TEXT DEFAULT '[]')")
    def load(self)->List[Task]:
        with self._conn() as c:
            rows=c.execute("SELECT id,text,created,completed,details,priority,tags FROM tasks ORDER BY id ASC").fetchall()
        out = []
        import json as _json
        for r in rows:
            details = []
            if r[4]:
                try: details = _json.loads(r[4])
                except Exception: details = []
            try: tags = _json.loads(r[6]) if r[6] else []
            except Exception: tags = []
            priority = int(r[5]) if r[5] is not None else 3
            out.append(Task(id=r[0], text=r[1], created=r[2], completed=bool(r[3]), details=details, priority=priority, tags=tags))
        return out
    def save_all(self, tasks: List[Task])->None:
        with self._conn() as c:
            c.execute("DELETE FROM tasks")
            import json as _json
            for t in tasks:
                c.execute("INSERT INTO tasks(id,text,created,completed,details,priority,tags) VALUES(?,?,?,?,?,?,?)", (t.id,t.text,t.created,int(t.completed),_json.dumps(getattr(t,'details',[])), int(getattr(t,'priority',3)), _json.dumps(getattr(t,'tags',[]))))
    def add(self, task: Task)->None:
        with self._conn() as c:
            import json as _json
            c.execute("INSERT INTO tasks(id,text,created,completed,details,priority,tags) VALUES(?,?,?,?,?,?,?)", (task.id,task.text,task.created,int(task.completed),_json.dumps(getattr(task,'details',[])), int(getattr(task,'priority',3)), _json.dumps(getattr(task,'tags',[]))))
    def update(self, task: Task)->None:
        with self._conn() as c:
            import json as _json
            c.execute("UPDATE tasks SET text=?, created=?, completed=?, details=?, priority=?, tags=? WHERE id=?", (task.text,task.created,int(task.completed),_json.dumps(getattr(task,'details',[])), int(getattr(task,'priority',3)), _json.dumps(getattr(task,'tags',[])), task.id))
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


def make_note_store(kind: str, base_dir: str):
    data_dir = os.path.join(base_dir, 'data_pkms'); os.makedirs(data_dir, exist_ok=True)
    json_path = os.path.join(data_dir, 'notes.json')
    db_path = os.path.join(data_dir, 'notes.db')

    class JsonNoteStore:
        def __init__(self, path): self.path = path
        def load(self):
            if os.path.exists(self.path):
                try:
                    with open(self.path,'r',encoding='utf-8') as fh: data=json.load(fh)
                    return [Note(**n) for n in data]
                except Exception:
                    return []
            return []
        def save_all(self, notes):
            with open(self.path,'w',encoding='utf-8') as fh: json.dump([asdict(n) for n in notes], fh, indent=2)
        def add(self, note): notes=self.load(); notes.append(note); self.save_all(notes)
        def update(self, note):
            notes=self.load()
            for i,n in enumerate(notes):
                if n.id==note.id: notes[i]=note; break
            self.save_all(notes)
        def delete(self, note_id):
            notes=self.load()
            for i,n in enumerate(notes):
                if n.id==note_id: del notes[i]; self.save_all(notes); return True
            return False

    class SqliteNoteStore:
        def __init__(self, path): self.path=path; os.makedirs(os.path.dirname(path), exist_ok=True); self._ensure()
        def _conn(self): return sqlite3.connect(self.path)
        def _ensure(self):
            with self._conn() as c:
                c.execute('CREATE TABLE IF NOT EXISTS notes(id INTEGER PRIMARY KEY, text TEXT, created TEXT, details TEXT)')
        def load(self):
            with self._conn() as c:
                rows = c.execute('SELECT id,text,created,details FROM notes ORDER BY id ASC').fetchall()
            out = []
            import json as _json
            for r in rows:
                details = []
                if r[3]:
                    try: details = _json.loads(r[3])
                    except Exception: details = []
                out.append(Note(id=r[0], text=r[1], created=r[2], details=details))
            return out
        def save_all(self, notes):
            with self._conn() as c:
                c.execute('DELETE FROM notes')
                import json as _json
                for n in notes:
                    c.execute('INSERT INTO notes(id,text,created,details) VALUES(?,?,?,?)', (n.id,n.text,n.created,_json.dumps(getattr(n,'details',[]))))
        def add(self, note):
            with self._conn() as c:
                import json as _json
                c.execute('INSERT INTO notes(id,text,created,details) VALUES(?,?,?,?)', (note.id,note.text,note.created,_json.dumps(getattr(note,'details',[]))))
        def update(self, note):
            with self._conn() as c:
                import json as _json
                c.execute('UPDATE notes SET text=?, created=?, details=? WHERE id=?', (note.text,note.created,_json.dumps(getattr(note,'details',[])),note.id))
        def delete(self, note_id):
            with self._conn() as c:
                cur = c.execute('DELETE FROM notes WHERE id=?', (note_id,))
                return cur.rowcount>0

    if kind == 'sqlite':
        return SqliteNoteStore(db_path)
    return JsonNoteStore(json_path)


def list_notes(backend: str, base_dir: str):
    store = make_note_store(backend, base_dir)
    return store.load()

def add_note(backend: str, base_dir: str, text: str):
    notes = list_notes(backend, base_dir)
    next_id = (max((n.id for n in notes), default=0) + 1) if notes else 1
    from datetime import datetime, timezone
    created = datetime.now(timezone.utc).isoformat()
    note = Note(id=next_id, text=text, created=created, details=[])
    store = make_note_store(backend, base_dir)
    store.add(note)
    return note

def describe_note(backend: str, base_dir: str, display_index: int, detail: str):
    notes = list_notes(backend, base_dir)
    note_id = map_display_index(notes, display_index)
    # find and update
    for n in notes:
        if n.id == note_id:
            n.details.append(detail)
            make_note_store(backend, base_dir).update(n)
            return
    raise KeyError('note not found')

def delete_note(backend: str, base_dir: str, display_index: int):
    notes = list_notes(backend, base_dir)
    try:
        nid = map_display_index(notes, display_index)
    except IndexError:
        return False
    return make_note_store(backend, base_dir).delete(nid)

def search_notes(backend: str, base_dir: str, query: str):
    q = (query or '').lower()
    return [n for n in list_notes(backend, base_dir) if q in (n.text or '').lower() or any(q in (d or '').lower() for d in getattr(n,'details',[]))]

def get_note_by_display_index(backend: str, base_dir: str, display_index: int):
    notes = list_notes(backend, base_dir)
    note_id = map_display_index(notes, display_index)
    for n in notes:
        if n.id == note_id:
            return n
    raise KeyError('note not found')
