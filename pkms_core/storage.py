from __future__ import annotations
import json, os, sqlite3
from typing import List, Optional
from .utils import map_display_index
from dataclasses import asdict
from .models import Task, Document, Note

class TaskStore:
    def load(self) -> List[Task]:
        raise NotImplementedError
    def save_all(self, tasks: List[Task]) -> None:
        raise NotImplementedError
    def add(self, task: Task) -> None:
        raise NotImplementedError
    def update(self, task: Task) -> None:
        raise NotImplementedError
    def delete(self, task_id: int) -> bool:
        raise NotImplementedError

class JsonTaskStore(TaskStore):
    def __init__(self, path: str):
        self.path = path
    def load(self) -> List[Task]:
        if os.path.exists(self.path):
            try:
                with open(self.path, 'r', encoding='utf-8') as fh:
                    data = json.load(fh)
                return [Task(**t) for t in data]
            except Exception:
                return []
        return []
    def save_all(self, tasks: List[Task]) -> None:
        with open(self.path, 'w', encoding='utf-8') as fh:
            json.dump([asdict(t) for t in tasks], fh, indent=2)
    def add(self, task: Task) -> None:
        tasks = self.load(); tasks.append(task); self.save_all(tasks)
    def update(self, task: Task) -> None:
        tasks = self.load()
        for i,t in enumerate(tasks):
            if t.id == task.id: tasks[i]=task; break
        self.save_all(tasks)
    def delete(self, task_id: int) -> bool:
        tasks = self.load()
        for i,t in enumerate(tasks):
            if t.id == task_id: del tasks[i]; self.save_all(tasks); return True
        return False

class SqliteTaskStore(TaskStore):
    def __init__(self, path: str):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self._ensure_schema()
    def _conn(self): return sqlite3.connect(self.path)
    def _ensure_schema(self):
        with self._conn() as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                text TEXT,
                created TEXT,
                completed INTEGER,
                details TEXT,
                priority INTEGER DEFAULT 3,
                tags TEXT DEFAULT '[]'
            )""")
            # Ensure columns exist for older DBs: add priority and tags if missing
            cur = conn.execute("PRAGMA table_info(tasks)").fetchall()
            cols = [c[1] for c in cur]
            if 'priority' not in cols:
                conn.execute("ALTER TABLE tasks ADD COLUMN priority INTEGER DEFAULT 3")
            if 'tags' not in cols:
                conn.execute("ALTER TABLE tasks ADD COLUMN tags TEXT DEFAULT '[]'")
    def load(self) -> List[Task]:
        with self._conn() as conn:
            rows = conn.execute("SELECT id,text,created,completed,details,priority,tags FROM tasks ORDER BY id ASC").fetchall()
        import json as _json
        result: List[Task] = []
        for r in rows:
            details = []
            if r[4]:
                try:
                    details = _json.loads(r[4])
                except Exception:
                    details = []
            # parse tags (stored as JSON text)
            tags = []
            try:
                tags = _json.loads(r[6]) if r[6] else []
            except Exception:
                tags = []
            priority = int(r[5]) if r[5] is not None else 3
            result.append(Task(id=r[0], text=r[1], created=r[2], completed=bool(r[3]), details=details, priority=priority, tags=tags))
        return result
    def save_all(self, tasks: List[Task]) -> None:
        with self._conn() as conn:
            conn.execute("DELETE FROM tasks")
            import json as _json
            for t in tasks:
                conn.execute(
                    "INSERT INTO tasks(id,text,created,completed,details,priority,tags) VALUES(?,?,?,?,?,?,?)",
                    (t.id, t.text, t.created, int(t.completed), _json.dumps(getattr(t, 'details', [])), int(getattr(t, 'priority', 3)), _json.dumps(getattr(t, 'tags', []))),
                )
    def add(self, task: Task) -> None:
        with self._conn() as conn:
            import json as _json
            conn.execute(
                "INSERT INTO tasks(id,text,created,completed,details,priority,tags) VALUES(?,?,?,?,?,?,?)",
                (task.id, task.text, task.created, int(task.completed), _json.dumps(getattr(task, 'details', [])), int(getattr(task, 'priority', 3)), _json.dumps(getattr(task, 'tags', [])) ),
            )
    def update(self, task: Task) -> None:
        with self._conn() as conn:
            import json as _json
            conn.execute(
                "UPDATE tasks SET text=?, created=?, completed=?, details=?, priority=?, tags=? WHERE id=?",
                (task.text, task.created, int(task.completed), _json.dumps(getattr(task, 'details', [])), int(getattr(task, 'priority', 3)), _json.dumps(getattr(task, 'tags', [])), task.id),
            )
    def delete(self, task_id: int) -> bool:
        with self._conn() as conn:
            cur = conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
            return cur.rowcount>0

# Document storage simple JSON only for legacy/debug
class DocumentStore:
    def __init__(self, path: str):
        self.path = path
    def load(self) -> List[Document]:
        if os.path.exists(self.path):
            try:
                with open(self.path,'r',encoding='utf-8') as fh: data=json.load(fh)
                return [Document(**d) for d in data]
            except Exception: return []
        return []
    def save_all(self, docs: List[Document]) -> None:
        with open(self.path,'w',encoding='utf-8') as fh:
            json.dump([asdict(d) for d in docs], fh, indent=2)

def make_task_store(kind: str, base_dir: str) -> TaskStore:
    data_dir = os.path.join(base_dir, 'app_data'); os.makedirs(data_dir, exist_ok=True)
    # If migrating to sqlite, look for legacy JSON stores in common legacy locations and import them.
    db_path = os.path.join(data_dir, 'tasks.db')
    json_path = os.path.join(data_dir, 'tasks.json')

    def _legacy_locations(root: str):
        return [os.path.join(root, 'data_pkms'), os.path.join(root, 'demo_data')]

    def _migrate_from_json(src_json: str, target_db: str) -> None:
        try:
            if not os.path.exists(src_json):
                return
            import json as _json
            with open(src_json, 'r', encoding='utf-8') as fh:
                data = _json.load(fh)
            if not isinstance(data, list) or not data:
                return
            # Ensure DB exists and schema present
            SqliteTaskStore(target_db)._ensure_schema()
            conn = SqliteTaskStore(target_db)._conn()
            with conn:
                for item in data:
                    # Item expected to have id, text, created, completed, details
                    details = _json.dumps(item.get('details', []))
                    conn.execute(
                        "INSERT OR IGNORE INTO tasks(id,text,created,completed,details) VALUES(?,?,?,?,?)",
                        (item.get('id'), item.get('text'), item.get('created'), int(bool(item.get('completed'))), details),
                    )
        except Exception:
            # Best-effort: ignore migration failures
            return

    # If sqlite requested and DB not present, attempt migration from legacy json files
    if kind == 'sqlite':
        if not os.path.exists(db_path):
            # try legacy locations
            for loc in _legacy_locations(base_dir):
                try_src = os.path.join(loc, 'tasks.json')
                _migrate_from_json(try_src, db_path)
            # also try top-level tasks.json
            _migrate_from_json(os.path.join(base_dir, 'tasks.json'), db_path)
        return SqliteTaskStore(db_path)
    # For json backend: if app_data/tasks.json doesn't exist, attempt to copy from legacy
    if not os.path.exists(json_path):
        for loc in _legacy_locations(base_dir):
            candidate = os.path.join(loc, 'tasks.json')
            try:
                if os.path.exists(candidate):
                    import shutil
                    shutil.copyfile(candidate, json_path)
                    break
            except Exception:
                continue
    return JsonTaskStore(json_path)

def make_document_store(base_dir: str) -> DocumentStore:
    data_dir = os.path.join(base_dir, 'app_data'); os.makedirs(data_dir, exist_ok=True)
    dest = os.path.join(data_dir,'docs.json')
    # If docs.json not present, attempt best-effort migration from legacy locations
    if not os.path.exists(dest):
        def _legacy_doc_locations(root: str):
            return [
                os.path.join(root, 'data_pkms'),
                os.path.join(root, 'demo_data'),
                os.path.join(root, 'task_neko'),
                root,
            ]

        def _migrate_docs_from_json(src: str, dst: str) -> bool:
            try:
                if not os.path.exists(src):
                    return False
                import json as _json
                with open(src, 'r', encoding='utf-8') as fh:
                    data = _json.load(fh)
                docs = []
                # If top-level dict with 'documents' or 'docs'
                if isinstance(data, dict):
                    if 'documents' in data and isinstance(data['documents'], list):
                        docs = data['documents']
                    elif 'docs' in data and isinstance(data['docs'], list):
                        docs = data['docs']
                    # Some legacy dumps store a 'task_neko_data' style root
                    elif 'documents' in data.get('task_neko_data', {}) and isinstance(data['task_neko_data']['documents'], list):
                        docs = data['task_neko_data']['documents']
                elif isinstance(data, list):
                    # If it's a list of dicts that look like documents, accept them
                    if data and all(isinstance(d, dict) for d in data):
                        # Heuristic: if items have 'title' and 'text' keys, consider them documents
                        if all(('title' in d or 'id' in d) and ('text' in d or 'body' in d or 'content' in d) for d in data):
                            docs = data
                if not docs:
                    return False
                # Normalize documents to Document dataclass fields
                normalized = []
                for d in docs:
                    title = d.get('title') or d.get('name') or ('Doc ' + str(d.get('id', '')))
                    text = d.get('text') or d.get('body') or d.get('content') or ''
                    tags = d.get('tags') or d.get('labels') or []
                    normalized.append({'title': title, 'text': text, 'tags': tags, 'id': d.get('id')})
                with open(dst, 'w', encoding='utf-8') as out:
                    _json.dump(normalized, out, indent=2, ensure_ascii=False)
                return True
            except Exception:
                return False

        for loc in _legacy_doc_locations(base_dir):
            # check common filenames
            for fname in ('docs.json', 'documents.json', 'task_neko_data.json', 'task_neko_data.json'):
                candidate = os.path.join(loc, fname)
                if _migrate_docs_from_json(candidate, dest):
                    break
            if os.path.exists(dest):
                break
    return DocumentStore(dest)


def make_note_store(kind: str, base_dir: str):
    """Create a note store for 'json' or 'sqlite' backends.
    Notes are stored in `app_data/notes.json` or `app_data/notes.db` (sqlite path uses tasks.db dir).
    """
    data_dir = os.path.join(base_dir, 'app_data'); os.makedirs(data_dir, exist_ok=True)
    db_path = os.path.join(data_dir, 'notes.db')
    json_path = os.path.join(data_dir, 'notes.json')

    class JsonNoteStore:
        def __init__(self, path: str):
            self.path = path
        def load(self) -> List[Note]:
            if os.path.exists(self.path):
                try:
                    with open(self.path, 'r', encoding='utf-8') as fh:
                        data = json.load(fh)
                    return [Note(**n) for n in data]
                except Exception:
                    return []
            return []
        def save_all(self, notes: List[Note]) -> None:
            with open(self.path, 'w', encoding='utf-8') as fh:
                json.dump([asdict(n) for n in notes], fh, indent=2, ensure_ascii=False)
        def add(self, note: Note) -> None:
            notes = self.load(); notes.append(note); self.save_all(notes)
        def delete(self, note_id: int) -> bool:
            notes = self.load()
            for i,n in enumerate(notes):
                if n.id == note_id:
                    del notes[i]; self.save_all(notes); return True
            return False
        def update(self, note: Note) -> None:
            notes = self.load()
            for i,n in enumerate(notes):
                if n.id == note.id: notes[i]=note; break
            self.save_all(notes)

    class SqliteNoteStore:
        def __init__(self, path: str):
            self.path = path
            os.makedirs(os.path.dirname(path), exist_ok=True)
            self._ensure_schema()
        def _conn(self): return sqlite3.connect(self.path)
        def _ensure_schema(self):
            with self._conn() as conn:
                conn.execute("""CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY,
                    text TEXT,
                    created TEXT,
                    details TEXT,
                    task_id INTEGER
                )""")
                # Ensure task_id column exists for older DBs
                cur = conn.execute("PRAGMA table_info(notes)").fetchall()
                cols = [c[1] for c in cur]
                if 'task_id' not in cols:
                    try:
                        conn.execute("ALTER TABLE notes ADD COLUMN task_id INTEGER")
                    except Exception:
                        pass
        def load(self) -> List[Note]:
            with self._conn() as conn:
                rows = conn.execute("SELECT id,text,created,details,task_id FROM notes ORDER BY id ASC").fetchall()
            import json as _json
            result: List[Note] = []
            for r in rows:
                details = []
                if r[3]:
                    try:
                        details = _json.loads(r[3])
                    except Exception:
                        details = []
                # task_id may be NULL
                task_id = r[4] if len(r) > 4 else None
                result.append(Note(id=r[0], text=r[1], created=r[2], details=details, task_id=task_id))
            return result
        def save_all(self, notes: List[Note]) -> None:
            with self._conn() as conn:
                conn.execute("DELETE FROM notes")
                import json as _json
                for n in notes:
                    conn.execute("INSERT INTO notes(id,text,created,details,task_id) VALUES(?,?,?,?,?)",
                                 (n.id, n.text, n.created, _json.dumps(getattr(n, 'details', [])), getattr(n, 'task_id', None)),)
        def add(self, note: Note) -> None:
            with self._conn() as conn:
                import json as _json
                conn.execute("INSERT INTO notes(id,text,created,details,task_id) VALUES(?,?,?,?,?)",
                             (note.id, note.text, note.created, _json.dumps(getattr(note, 'details', [])), getattr(note, 'task_id', None)),)
        def update(self, note: Note) -> None:
            with self._conn() as conn:
                import json as _json
                conn.execute("UPDATE notes SET text=?, created=?, details=?, task_id=? WHERE id=?",
                             (note.text, note.created, _json.dumps(getattr(note, 'details', [])), getattr(note, 'task_id', None), note.id))
        def delete(self, note_id: int) -> bool:
            with self._conn() as conn:
                cur = conn.execute("DELETE FROM notes WHERE id=?", (note_id,))
                return cur.rowcount>0

    # Migration or legacy best-effort: if sqlite requested and DB missing, try to migrate from legacy json
    def _migrate_from_json(src_json: str, target_db: str) -> None:
        try:
            if not os.path.exists(src_json):
                return
            import json as _json
            with open(src_json, 'r', encoding='utf-8') as fh:
                data = _json.load(fh)
            if not isinstance(data, list) or not data:
                return
            SqliteNoteStore(target_db)._ensure_schema()
            conn = SqliteNoteStore(target_db)._conn()
            with conn:
                for item in data:
                    details = _json.dumps(item.get('details', []))
                    task_id = item.get('task_id') if isinstance(item, dict) else None
                    conn.execute("INSERT OR IGNORE INTO notes(id,text,created,details,task_id) VALUES(?,?,?,?,?)",
                                 (item.get('id'), item.get('text'), item.get('created'), details, task_id),)
        except Exception:
            return

    # Return appropriate store
    if kind == 'sqlite':
        if not os.path.exists(db_path):
            # attempt legacy json locations
            for loc in (os.path.join(base_dir, 'data_pkms'), os.path.join(base_dir, 'demo_data')):
                try_src = os.path.join(loc, 'notes.json')
                _migrate_from_json(try_src, db_path)
            _migrate_from_json(os.path.join(base_dir, 'notes.json'), db_path)
        return SqliteNoteStore(db_path)
    # json backend: copy from legacy if missing
    if not os.path.exists(json_path):
        for loc in (os.path.join(base_dir, 'data_pkms'), os.path.join(base_dir, 'demo_data')):
            candidate = os.path.join(loc, 'notes.json')
            try:
                if os.path.exists(candidate):
                    import shutil
                    shutil.copyfile(candidate, json_path)
                    break
            except Exception:
                continue
    return JsonNoteStore(json_path)


### Outward-facing helpers for notes (backend dispatch)
# Use map_display_index from pkms_core.utils for mapping 1-based display indexes to ids

def list_notes(backend: str, base_dir: str) -> List[Note]:
    store = make_note_store(backend, base_dir)
    return store.load()

def add_note(backend: str, base_dir: str, text: str, task_id: int = None) -> Note:
    notes = list_notes(backend, base_dir)
    next_id = (max((n.id for n in notes), default=0) + 1) if notes else 1
    from datetime import datetime, timezone
    created = datetime.now(timezone.utc).isoformat()
    note = Note(id=next_id, text=text, created=created, details=[], task_id=task_id)
    store = make_note_store(backend, base_dir)
    store.add(note)
    return note

def describe_note(backend: str, base_dir: str, display_index: int, detail: str) -> None:
    notes = list_notes(backend, base_dir)
    note_id = map_display_index(notes, display_index)
    store = make_note_store(backend, base_dir)
    # find note modify then update
    for n in notes:
        if n.id == note_id:
            n.details.append(detail)
            store.update(n)
            return
    raise KeyError('note not found')

def delete_note(backend: str, base_dir: str, display_index: int) -> bool:
    notes = list_notes(backend, base_dir)
    note_id = map_display_index(notes, display_index)
    store = make_note_store(backend, base_dir)
    return store.delete(note_id)

def search_notes(backend: str, base_dir: str, query: str) -> List[Note]:
    q = (query or '').lower()
    results: List[Note] = []
    for n in list_notes(backend, base_dir):
        if q in (n.text or '').lower() or any(q in (d or '').lower() for d in getattr(n, 'details', [])):
            results.append(n)
    return results

def get_note_by_display_index(backend: str, base_dir: str, display_index: int) -> Note:
    notes = list_notes(backend, base_dir)
    note_id = map_display_index(notes, display_index)
    for n in notes:
        if n.id == note_id:
            return n
    raise KeyError('note not found')
