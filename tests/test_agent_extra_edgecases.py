from datetime import datetime, timezone, timedelta

from pkms_core.agent import Agent
from pkms_core.models import Task, Document


def make_task(id, text, days_old=0, priority=3, completed=False, details=None, tags=None, created_iso=None):
    if created_iso is None:
        created = (datetime.now(timezone.utc) - timedelta(days=days_old)).isoformat()
    else:
        created = created_iso
    return Task(id=id, text=text, created=created, completed=completed, details=details or [], priority=priority, tags=tags or [])


def make_doc(id, title, text, tags=None):
    return Document(id=id, title=title, text=text, tags=tags or [], links=[], created="", updated="")


def test_doc_suggestion_contents():
    docs = [
        make_doc(1, "Notes", "TODO: add unit tests\ncreate prototype"),
    ]
    agent = Agent()
    suggestions = agent.suggest_tasks_from_documents(docs)
    assert any("add unit tests" == s for s in suggestions), "Expected 'add unit tests' suggestion from TODO line"
    assert any("create prototype" == s for s in suggestions), "Expected 'create prototype' suggestion from verb-start line"


def test_malformed_and_empty_created_handling():
    # created that cannot be parsed should not raise and should not be considered urgent
    t1 = make_task(1, "Broken date task", created_iso="not-a-date", priority=5)
    t2 = make_task(2, "Empty created", created_iso="", priority=5)
    advice = Agent().productivity_advice([t1, t2], [])
    assert not any("Urgent" in a for a in advice), "Malformed or empty created should not mark tasks urgent"


def test_future_created_not_marked_urgent():
    future_iso = (datetime.now(timezone.utc) + timedelta(days=10)).isoformat()
    t = make_task(1, "Future task", created_iso=future_iso, priority=5)
    advice = Agent().productivity_advice([t], [])
    assert not any("Urgent" in a for a in advice), "Future created dates should not be marked urgent"
