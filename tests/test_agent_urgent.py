from datetime import datetime, timezone, timedelta

from pkms_core.agent import Agent
from pkms_core.models import Task


def make_task(id, text, days_old=0, priority=3, completed=False, details=None, tags=None):
    created = (datetime.now(timezone.utc) - timedelta(days=days_old)).isoformat()
    return Task(id=id, text=text, created=created, completed=completed, details=details or [], priority=priority, tags=tags or [])


def test_urgent_and_high_focus():
    tasks = [
        make_task(1, "Critical prod fix", days_old=8, priority=5),
        make_task(2, "New feature sketch", days_old=1, priority=5),
    ]
    agent = Agent()
    advice = agent.productivity_advice(tasks, [])
    assert any("Urgent" in a for a in advice), "Expected an 'Urgent' line for aging high-priority task"
    assert any("High focus" in a for a in advice), "Expected a 'High focus' line for high-priority tasks"


def test_no_urgent_before_7_days():
    tasks = [make_task(1, "Recent critical", days_old=6, priority=5)]
    advice = Agent().productivity_advice(tasks, [])
    assert not any("Urgent" in a for a in advice), "No 'Urgent' line expected for task younger than 7 days"


def test_completed_not_urgent():
    t = make_task(1, "Old done", days_old=10, priority=5, completed=True)
    advice = Agent().productivity_advice([t], [])
    assert not any("Urgent" in a for a in advice), "Completed tasks should not be marked Urgent"
