"""OpenAI Chat Completions summarizer for tasks4.

Implements a small wrapper that takes paragraph-length descriptions and
returns a short phrase summary for each. If the OpenAI client or API key
is not available the module falls back to a heuristic summary.
"""
from __future__ import annotations
import os
from typing import List


def _heuristic_summary(paragraph: str, max_words: int = 6) -> str:
    """Simple fallback summarizer: return the first `max_words` words."""
    words = paragraph.strip().split()
    return " ".join(words[:max_words]) if words else ""


def summarize_paragraph(paragraph: str, model: str = "chatgpt-5-mini") -> str:
    """Summarize a single paragraph using OpenAI Chat Completions.

    If the OpenAI client or API key is not present the function returns
    a heuristic fallback summary.
    """
    try:
        import openai

        # Attempt to call the OpenAI client. If it fails for any reason (missing
        # API key, network error, etc.) we fall back to the heuristic summary.

        # Construct a short prompt asking for a short phrase
        system = {
            "role": "system",
            "content": "You are a task summarizer. Reply with a short, title-like phrase."
        }
        user = {"role": "user", "content": f"Summarize this task description in one short phrase:\n\n{paragraph}"}

        # Use Chat Completions API; library API may differ slightly across versions.
        # We attempt to call `openai.ChatCompletion.create` and gracefully fall back on failure.
        try:
            resp = openai.ChatCompletion.create(model=model, messages=[system, user], max_tokens=32)
            # Response formats vary; try to extract text robustly
            if hasattr(resp, "choices"):
                choice = resp.choices[0]
            else:
                choice = resp.get("choices", [{}])[0]

            # Newer spec uses .message.content
            if hasattr(choice, "message"):
                text = choice.message.get("content") if isinstance(choice.message, dict) else None
            else:
                text = choice.get("message", {}).get("content") if isinstance(choice, dict) else None

            if not text:
                # older style with 'text' field
                text = choice.get("text") if isinstance(choice, dict) else None
            if not text and isinstance(resp, dict):
                text = resp.get("choices", [{}])[0].get("message", {}).get("content")
            return (text or _heuristic_summary(paragraph)).strip()
        except Exception:
            return _heuristic_summary(paragraph)
    except Exception:
        # openai import failed
        return _heuristic_summary(paragraph)


def summarize_paragraphs(paragraphs: List[str], model: str = "chatgpt-5-mini") -> List[str]:
    return [summarize_paragraph(p, model=model) for p in paragraphs]


SAMPLE_PARAGRAPHS = [
    "Refactor the authentication module to support multi-tenant deployment, including extracting provider-specific logic and adding integration tests to validate each provider.",
    "Build a weekly analytics reporting pipeline that aggregates user engagement metrics, produces CSV and JSON exports, and pushes summaries to the analytics S3 bucket for downstream consumption."
]


def main() -> int:
    print("Summarizing task descriptions...\n")
    summaries = summarize_paragraphs(SAMPLE_PARAGRAPHS)
    for i, s in enumerate(summaries, start=1):
        print(f"Paragraph {i} summary: {s}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
