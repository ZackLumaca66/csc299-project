from __future__ import annotations
import json, os, sqlite3
from typing import List, Optional
from dataclasses import asdict
from .models import Task, Document

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
                details TEXT
            )""")
    def load(self) -> List[Task]:
        with self._conn() as conn:
            rows = conn.execute("SELECT id,text,created,completed,details FROM tasks ORDER BY id ASC").fetchall()
        import json as _json
        result: List[Task] = []
        for r in rows:
            details = []
            if r[4]:
                try:
                    details = _json.loads(r[4])
                except Exception:
                    details = []
            result.append(Task(id=r[0], text=r[1], created=r[2], completed=bool(r[3]), details=details))
        return result
    def save_all(self, tasks: List[Task]) -> None:
        with self._conn() as conn:
            conn.execute("DELETE FROM tasks")
            import json as _json
            for t in tasks:
                conn.execute(
                    "INSERT INTO tasks(id,text,created,completed,details) VALUES(?,?,?,?,?)",
                    (t.id, t.text, t.created, int(t.completed), _json.dumps(getattr(t, 'details', []))),
                )
    def add(self, task: Task) -> None:
        with self._conn() as conn:
            import json as _json
            conn.execute(
                "INSERT INTO tasks(id,text,created,completed,details) VALUES(?,?,?,?,?)",
                (task.id, task.text, task.created, int(task.completed), _json.dumps(getattr(task, 'details', []))),
            )
    def update(self, task: Task) -> None:
        with self._conn() as conn:
            import json as _json
            conn.execute(
                "UPDATE tasks SET text=?, created=?, completed=?, details=? WHERE id= ?",
                (task.text, task.created, int(task.completed), _json.dumps(getattr(task, 'details', [])), task.id),
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
