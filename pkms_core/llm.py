from __future__ import annotations
import os
from typing import Optional

"""LLM selection and small adapter utilities.

This module provides a lightweight fallback adapter (`LLMAdapter`) and a factory
function `make_llm()` which returns an OpenAI-backed adapter if an API key is
present and the adapter can be loaded, otherwise the simple local adapter is
returned. This keeps demos and tests deterministic when no network/key is
available.
"""

try:
    # Local import to avoid adding a hard dependency at package import time
    from .llm_openai import OpenAIAdapter  # type: ignore
except Exception:
    OpenAIAdapter = None  # type: ignore

try:
    from .keyring_store import get_api_key
except Exception:
    get_api_key = None


class LLMAdapter:
    """Stub LLM adapter: detects key presence and provides simulated summaries.

    This adapter returns None for `summarize()` when no key is present; it can
    be used as a non-networked fallback so demos and tests remain deterministic.
    """

    def __init__(self):
        # Prefer key stored in OS keyring, then fall back to environment variables
        kr_key = None
        if callable(get_api_key):
            try:
                kr_key = get_api_key()
            except Exception:
                kr_key = None
        self.key = kr_key or os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_KEY") or os.getenv("ANTHROPIC_KEY")

    def available(self) -> bool:
        return bool(self.key)

    def summarize(self, text: str) -> Optional[str]:
        if not self.available():
            return None
        words = text.strip().split()
        return " ".join(words[:12]) + (" ...[llm]" if len(words) > 12 else " [llm]")


def make_llm() -> object:
    """Return an LLM adapter object.

    Priority:
    1. If `OpenAIAdapter` is available (module present) and env var present,
       return an instantiated OpenAIAdapter.
    2. Otherwise, return the simple `LLMAdapter` fallback.
    """
    # If OpenAIAdapter class exists, attempt to instantiate and confirm availability
    if OpenAIAdapter is not None:
        try:
            adapter = OpenAIAdapter()
            if hasattr(adapter, "available") and adapter.available():
                return adapter
        except Exception:
            # Fall through to the local adapter on any error
            pass

    return LLMAdapter()


__all__ = ["LLMAdapter", "make_llm"]