from pkms_core.agent import Agent
from pkms_core.models import Document


def test_imperative_detection_and_todo_parsing():
    a = Agent()
    doc = Document(
        id=1,
        title="Notes",
        text="""
    Create README for the project
    Review PR #12 and leave comments
    TODO: add unit tests for storage
    This line is just a note and should not become a task
    todo fix the failing CI pipeline
    """,
        tags=[],
        links=[],
        created="",
        updated="",
    )

    suggestions = a.suggest_tasks_from_document(doc)
    # Expect to find the imperative lines and todos
    assert any("Create README" in s for s in suggestions)
    assert any("Review PR" in s for s in suggestions)
    assert any("add unit tests" in s or "add unit tests for storage" in s for s in suggestions)
    assert any("fix the failing CI" in s or "fix the failing CI pipeline" in s for s in suggestions)


def test_dedup_and_order_across_documents():
    a = Agent()
    d1 = Document(id=1, title="A", text="TODO: write tests\nCreate sample data", tags=[], links=[], created="", updated="")
    d2 = Document(id=2, title="B", text="Create sample data\nTODO: write tests\nRefactor parser", tags=[], links=[], created="", updated="")

    out = a.suggest_tasks_from_documents([d1, d2])
    # Should preserve first-seen order and deduplicate exact strings
    assert out[0].lower().startswith("write tests") or "write tests" in out[0].lower()
    # 'Create sample data' should appear once
    assert sum(1 for s in out if "create sample data" in s.lower()) == 1


def test_ignores_blank_and_nonmatching_lines():
    a = Agent()
    doc = Document(id=3, title="Empty", text="\n   \nNote: remember to breathe\n", tags=[], links=[], created="", updated="")
    assert a.suggest_tasks_from_document(doc) == []
