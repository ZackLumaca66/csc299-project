from pkms_core.agent import Agent
from pkms_core.models import Task, Document
from datetime import datetime, timezone, timedelta

def test_advise_includes_high_focus():
    now = datetime.now(timezone.utc).isoformat()
    tasks = [
        Task(id=1, text='Low priority task', created=now, completed=False, details=[], priority=2, tags=[]),
        Task(id=2, text='High priority important task', created=now, completed=False, details=[], priority=5, tags=[]),
        Task(id=3, text='Another high priority', created=now, completed=False, details=[], priority=4, tags=[]),
    ]
    agent = Agent()
    advice = agent.productivity_advice(tasks, [])
    combined = '\n'.join(advice)
    assert 'High focus' in combined

def test_advise_refine_shows_when_no_details():
    now = datetime.now(timezone.utc).isoformat()
    tasks = [
        Task(id=1, text='Refine me task', created=now, completed=False, details=[], priority=3, tags=[]),
    ]
    agent = Agent()
    advice = agent.productivity_advice(tasks, [])
    combined = '\n'.join(advice)
    assert 'Refine' in combined
