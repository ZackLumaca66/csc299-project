from datetime import datetime, timezone, timedelta

from pkms_core.agent import Agent
from pkms_core.models import Task


def make_task(id, text, days_old=0, priority=3, completed=False, details=None, tags=None):
    created = (datetime.now(timezone.utc) - timedelta(days=days_old)).isoformat()
    return Task(id=id, text=text, created=created, completed=completed, details=details or [], priority=priority, tags=tags or [])


def test_stale_tasks_detected():
    # Task older than 14 days should be considered stale
    tasks = [make_task(1, "Old task", days_old=15, priority=2, completed=False)]
    advice = Agent().productivity_advice(tasks, [])
    assert any("Stale" in a for a in advice), "Expected 'Stale' line for tasks older than 14 days"


def test_refine_candidates_detection():
    # Priority >=3 and no details triggers 'Refine'
    tasks = [make_task(1, "Needs details", days_old=1, priority=3, details=[])]
    advice = Agent().productivity_advice(tasks, [])
    assert any(a.startswith("Refine:") for a in advice), "Expected 'Refine:' line for candidate"


def test_long_task_breakdown_notice():
    long_text = "This is a deliberately long task text containing more than twelve words to trigger breakdown suggestion"
    tasks = [make_task(1, long_text, days_old=1, priority=2)]
    advice = Agent().productivity_advice(tasks, [])
    assert any("Break down" in a for a in advice), "Expected 'Break down' suggestion for long tasks"


def test_high_focus_grouping():
    tasks = [
        make_task(1, "High priority one", days_old=0, priority=4),
        make_task(2, "High priority two", days_old=0, priority=5),
    ]
    advice = Agent().productivity_advice(tasks, [])
    assert any(a.startswith("High focus:") for a in advice), "Expected 'High focus' grouping for high-priority open tasks"
