import os
import threading
from pkms_core.core import TaskManager, DocumentManager


def test_unicode_handling(tmp_path):
    cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        tm = TaskManager(backend='json')
        dm = DocumentManager()
        # Unicode text examples
        t = tm.add('Fix résumé parsing – ensure accents ✓')
        assert 'résumé' in t.text
        d = dm.add('设计', '这是一些中文内容，包含 TODO: 测试')
        suggestions = []
        # ensure suggestions can handle non-ascii
        from pkms_core.agent import Agent
        a = Agent()
        suggestions = a.suggest_tasks_from_document(d)
        # when no TODO in English tokens, suggestions may be empty, but adding should not error
        assert isinstance(suggestions, list)
    finally:
        os.chdir(cwd)


def test_large_smoke_and_basic_concurrency(tmp_path):
    cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        # smoke: create many tasks to ensure storage handles scale
        tm = TaskManager(backend='json')
        n = 300
        for i in range(n):
            tm.add(f"Task {i} sample")
        assert len(tm.list()) == n

        # basic concurrency test against sqlite backend
        os.chdir(tmp_path)
        tm_sql = TaskManager(backend='sqlite')

        def worker(start, count):
            for j in range(start, start + count):
                tm_sql.add(f"concurrent {j}")

        threads = [threading.Thread(target=worker, args=(i*20, 20)) for i in range(3)]
        for th in threads: th.start()
        for th in threads: th.join()

        # expect 60 new tasks
        assert len([t for t in tm_sql.list() if t.text.startswith('concurrent')]) == 60
    finally:
        os.chdir(cwd)
