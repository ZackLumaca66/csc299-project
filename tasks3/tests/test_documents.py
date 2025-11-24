import sys
import os

# ensure local src is importable
ROOT = os.path.join(os.getcwd(), "tasks3", "src")
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tasks3_cli.document import DocumentManager


def test_add_list_search_delete(tmp_path):
    dm_path = str(tmp_path / "docs.json")
    dm = DocumentManager(path=dm_path)
    d1 = dm.add("Note A", "This is a test note", tags=["test", "note"])
    d2 = dm.add("Note B", "Another note about python", tags=["python"])

    all_docs = dm.list()
    assert len(all_docs) == 2

    results = dm.search("python")
    assert len(results) == 1
    assert results[0].id == d2.id

    got = dm.get(d1.id)
    assert got is not None and got.title == "Note A"

    assert dm.delete(d1.id) is True
    assert dm.get(d1.id) is None
