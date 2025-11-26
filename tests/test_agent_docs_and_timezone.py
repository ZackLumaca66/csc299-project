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


def test_doc_derived_suggestions_count():
    docs = [
        make_doc(1, "Notes", "TODO: add tests\nWrite code to handle edge cases"),
        make_doc(2, "Ideas", "plan: new feature\ncreate prototype"),
    ]
    advice = Agent().productivity_advice([], docs)
    # The agent returns a doc-derived suggestions count line when suggestions exist
    assert any("Doc-derived suggestions" in a for a in advice), "Expected doc-derived suggestions count in advice"


def test_timezone_less_created_parsing():
    # Provide a created timestamp without timezone information
    naive_iso = (datetime.now(timezone.utc) - timedelta(days=8)).replace(tzinfo=None).isoformat()
    t = make_task(1, "Naive old task", created_iso=naive_iso, priority=5)
    advice = Agent().productivity_advice([t], [])
    # Should mark it as Urgent because it's older than 7 days even without tz info
    assert any("Urgent" in a for a in advice), "Expected 'Urgent' for timezone-less old task"
