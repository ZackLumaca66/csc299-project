import sys
import tempfile
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))

from tasks4 import create_task, list_tasks, search_tasks, ALLOWED_STATUSES  # type: ignore


def test_create_and_list_basic():
    with tempfile.TemporaryDirectory() as d:
        repo = os.path.join(d, "repo.json")
        t1 = create_task("Alpha", "First", repo_path=repo)
        t2 = create_task("Beta", "Second", repo_path=repo)
        items = list_tasks(repo)
        assert len(items) == 2
        assert items[0].id == 1
        assert items[1].id == 2
        assert items[0].created_at != items[1].created_at


def test_search_tasks():
    with tempfile.TemporaryDirectory() as d:
        repo = os.path.join(d, "repo.json")
        create_task("Write report", "Quarterly financials", repo_path=repo)
        create_task("Email team", "Send update", repo_path=repo)
        results = search_tasks("report", repo)
        assert len(results) == 1
        assert results[0].title == "Write report"


def test_invalid_status_rejected():
    with tempfile.TemporaryDirectory() as d:
        repo = os.path.join(d, "repo.json")
        try:
            create_task("Bad", "Wrong status", status="not-a-status", repo_path=repo)
        except ValueError as e:
            assert "Invalid status" in str(e)
        else:
            raise AssertionError("Expected ValueError for invalid status")


def test_allowed_statuses_create():
    with tempfile.TemporaryDirectory() as d:
        repo = os.path.join(d, "repo.json")
        for s in ALLOWED_STATUSES:
            t = create_task(f"Do {s}", f"Task {s}", status=s, repo_path=repo)
            assert t.status == s
