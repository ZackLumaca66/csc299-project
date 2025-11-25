from datetime import datetime, timezone, timedelta

from pkms_core.agent import Agent
from pkms_core.models import Task


def make_task(id, text, days_old=0, priority=3, completed=False, details=None, tags=None):
    created = (datetime.now(timezone.utc) - timedelta(days=days_old)).isoformat()
    return Task(id=id, text=text, created=created, completed=completed, details=details or [], priority=priority, tags=tags or [])


def test_quick_wins_shown_for_short_high_priority():
    tasks = [
        make_task(1, "Reply to Bob", days_old=0, priority=3),
        make_task(2, "Pay invoice", days_old=0, priority=4),
        make_task(3, "Write long spec for project X which is long", days_old=0, priority=5),
    ]
    advice = Agent().productivity_advice(tasks, [])
    assert any(a.startswith("Quick wins:") for a in advice), "Expected Quick wins line for short high-priority tasks"


def test_quick_wins_excludes_long_or_low_priority():
    tasks = [
        make_task(1, "This task has a lot of words and is not short at all", priority=4),
        make_task(2, "Low priority short", priority=2),
    ]
    advice = Agent().productivity_advice(tasks, [])
    assert not any(a.startswith("Quick wins:") for a in advice), "Quick wins should exclude long text or low-priority tasks"
