from datetime import datetime, timezone, timedelta

from pkms_core.agent import Agent
from pkms_core.models import Task


def make_task(id, text, days_old=0, priority=3, completed=False):
    created = (datetime.now(timezone.utc) - timedelta(days=days_old)).isoformat()
    return Task(id=id, text=text, created=created, completed=completed, details=[], priority=priority, tags=[])


def test_priority_spread_counts():
    tasks = [
        make_task(1, "A", priority=5),
        make_task(2, "B", priority=4),
        make_task(3, "C", priority=4),
        make_task(4, "D", priority=3),
        make_task(5, "E", priority=5, completed=True),  # completed should be excluded
    ]
    advice = Agent().productivity_advice(tasks, [])
    spread_lines = [a for a in advice if a.startswith("Priority spread")]
    assert spread_lines, "Expected a Priority spread line"
    # Expect P5:1 (one open P5), P4:2, P3:1
    assert "P5:1" in spread_lines[0]
    assert "P4:2" in spread_lines[0]
    assert "P3:1" in spread_lines[0]
