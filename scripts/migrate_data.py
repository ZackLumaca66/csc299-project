"""Manual migration helper: import legacy JSON stores into central `app_data/` sqlite DB.

Run:
  python scripts/migrate_data.py

This will look for `data_pkms/tasks.json`, `demo_data/tasks.json`, and top-level `tasks.json` and import tasks into `app_data/tasks.db`.
"""
from __future__ import annotations
import os
import sys
import json
from pkms_core.storage import SqliteTaskStore

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

legacy_paths = [os.path.join(ROOT, 'data_pkms'), os.path.join(ROOT, 'demo_data'), ROOT]
app_dir = os.path.join(ROOT, 'app_data')
os.makedirs(app_dir, exist_ok=True)
db_path = os.path.join(app_dir, 'tasks.db')

store = SqliteTaskStore(db_path)
store._ensure_schema()

found = False
for p in legacy_paths:
    src = os.path.join(p, 'tasks.json')
    if os.path.exists(src):
        print(f"Migrating from {src} -> {db_path}")
        try:
            with open(src, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
            if isinstance(data, list):
                conn = store._conn()
                import json as _json
                with conn:
                    for item in data:
                        details = _json.dumps(item.get('details', []))
                        conn.execute(
                            "INSERT OR IGNORE INTO tasks(id,text,created,completed,details) VALUES(?,?,?,?,?)",
                            (item.get('id'), item.get('text'), item.get('created'), int(bool(item.get('completed'))), details),
                        )
                print("Migration completed for:", src)
                found = True
        except Exception as e:
            print("Failed to migrate from", src, "->", e)
if not found:
    print("No legacy tasks.json found in data_pkms/ demo_data/ or project root.")
else:
    print("Done. Consider removing legacy folders to avoid future confusion.")
*** End Patch