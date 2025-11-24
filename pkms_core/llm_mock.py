from __future__ import annotations

class MockLLM:
    """Simple mock LLM adapter used for demos when no API key is present.
    Interface mirrors the real LLMAdapter: .available() and .summarize(text).
    """
    def __init__(self):
        pass

    def available(self) -> bool:
        return True

    def summarize(self, text: str) -> str:
        words = text.strip().split()
        return "[mock-llm] " + " ".join(words[:10]) + (" ..." if len(words) > 10 else "")


__all__ = ["MockLLM"]
