from __future__ import annotations
import os

class LLMAdapter:
    """Stub LLM adapter: detects key presence and provides simulated summaries.
    Intended for later replacement with real API calls (OpenAI/Anthropic)."""
    def __init__(self):
        self.key = os.getenv('OPENAI_KEY') or os.getenv('ANTHROPIC_KEY')
    def available(self) -> bool:
        return bool(self.key)
    def summarize(self, text: str) -> str | None:
        if not self.available():
            return None
        words = text.strip().split()
        return " ".join(words[:12]) + (" ...[llm]" if len(words) > 12 else " [llm]")

__all__ = ["LLMAdapter"]