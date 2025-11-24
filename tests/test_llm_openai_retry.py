import sys
import types
import os
import time
import random

import pytest

from pkms_core.llm_openai import OpenAIAdapter


def test_openai_adapter_retries(monkeypatch):
    """Mock `openai.ChatCompletion.create` to fail a few times then succeed.

    Verify the adapter retries and returns the final successful content.
    """

    # Prepare a fake openai module with a ChatCompletion.create that fails twice
    calls = {"n": 0}

    def fake_create(*args, **kwargs):
        calls["n"] += 1
        if calls["n"] < 3:
            raise Exception("transient error")
        return {"choices": [{"message": {"content": "recovered"}}]}

    fake_openai = types.SimpleNamespace()

    class ChatCompletionObj:
        create = staticmethod(fake_create)

    fake_openai.ChatCompletion = ChatCompletionObj
    fake_openai.api_key = None

    # Inject fake openai into sys.modules before adapter import/instantiation
    monkeypatch.setitem(sys.modules, "openai", fake_openai)

    # Ensure adapter treats key as present
    monkeypatch.setenv("OPENAI_API_KEY", "dummy-key")

    # Avoid sleeping to keep tests fast
    monkeypatch.setattr(time, "sleep", lambda s: None)
    monkeypatch.setattr(random, "uniform", lambda a, b: 0)

    adapter = OpenAIAdapter()
    assert adapter.available(), "Adapter should be available with fake openai present"

    result = adapter.chat([{"role": "user", "content": "Hello"}], retries=4, backoff_factor=0.1)

    assert result == "recovered"
    assert calls["n"] == 3, "ChatCompletion.create should have been called three times (two failures, one success)"
