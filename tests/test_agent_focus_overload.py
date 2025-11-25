from datetime import datetime, timezone, timedelta

from pkms_core.agent import Agent
from pkms_core.models import Task


def make_task(id, text, days_old=0, priority=3, completed=False, details=None, tags=None):
    created = (datetime.now(timezone.utc) - timedelta(days=days_old)).isoformat()
    return Task(id=id, text=text, created=created, completed=completed, details=details or [], priority=priority, tags=tags or [])


def test_focus_overload_triggers():
    # Create 6 high-priority open tasks to exceed default threshold (5)
    tasks = [make_task(i, f"High {i}", priority=4) for i in range(1, 7)]
    advice = Agent().productivity_advice(tasks, [])
    assert any("Focus overload" in a for a in advice), "Expected focus overload warning when >5 high-priority tasks"


def test_focus_overload_not_triggered_at_threshold():
    # Exactly 5 should not trigger (> threshold required)
    tasks = [make_task(i, f"High {i}", priority=4) for i in range(1, 6)]
    advice = Agent().productivity_advice(tasks, [])
    assert not any("Focus overload" in a for a in advice), "Focus overload should not trigger at threshold"
