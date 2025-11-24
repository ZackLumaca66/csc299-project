import os
import sys
import json
import types
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))

from tasks4.tasks4 import summarize_paragraph, summarize_paragraphs  # type: ignore


class DummyChoice(dict):
    pass


class DummyResp(dict):
    pass


def test_fallback_no_openai(monkeypatch):
    # Simulate openai import failure by injecting an ImportError in sys.modules
    monkeypatch.setitem(sys.modules, "openai", None)
    paragraph = "This is a sample paragraph that will be fallback summarized."
    s = summarize_paragraph(paragraph)
    assert s and isinstance(s, str)


def test_mocked_openai(monkeypatch):
    # Create a fake openai module with ChatCompletion.create
    fake_openai = types.SimpleNamespace()

    def fake_create(model, messages, max_tokens=32):
        # Return a structure similar to the real response
        return {"choices": [{"message": {"content": "Refactor auth module"}}]}

    fake_openai.ChatCompletion = types.SimpleNamespace(create=fake_create)
    monkeypatch.setitem(sys.modules, "openai", fake_openai)

    paragraph = "Refactor authentication to support multi-tenant providers and add tests."
    s = summarize_paragraph(paragraph)
    assert "Refactor auth" in s or "Refactor" in s


def test_summarize_multiple(monkeypatch):
    fake_openai = types.SimpleNamespace()

    def fake_create(model, messages, max_tokens=32):
        return {"choices": [{"message": {"content": "Summary A"}}]}

    fake_openai.ChatCompletion = types.SimpleNamespace(create=fake_create)
    monkeypatch.setitem(sys.modules, "openai", fake_openai)

    paragraphs = ["One.", "Two."]
    res = summarize_paragraphs(paragraphs)
    assert res == ["Summary A", "Summary A"]
