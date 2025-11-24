from __future__ import annotations
import types
import sys
import os

import pytest


def make_fake_openai(return_text: str = "fake summary"):
    fake = types.SimpleNamespace()

    def fake_create(**kwargs):
        # mimic response shape with dicts
        return {"choices": [{"message": {"content": return_text}}]}

    fake.ChatCompletion = types.SimpleNamespace(create=fake_create)
    return fake


def test_openai_adapter_summarize_with_mocked_openai(monkeypatch, tmp_path):
    # Ensure env key present so adapter attempts to use openai
    monkeypatch.setenv("OPENAI_API_KEY", "dummy-key")

    fake_openai = make_fake_openai("mocked summary")
    monkeypatch.setitem(sys.modules, "openai", fake_openai)

    # Import here so it picks up the patched sys.modules
    from pkms_core.llm_openai import OpenAIAdapter

    a = OpenAIAdapter()
    assert a.available()
    s = a.summarize("This is a long test text that should be summarized.")
    assert s is not None
    assert "mocked summary" in s


def test_openai_adapter_not_available_without_key(monkeypatch):
    # Remove env keys and any openai module
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_KEY", raising=False)
    monkeypatch.setitem(sys.modules, "openai", None)

    from pkms_core.llm_openai import OpenAIAdapter

    a = OpenAIAdapter()
    assert not a.available()
    assert a.summarize("text") is None
