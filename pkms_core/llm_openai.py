from __future__ import annotations
import os
import time
import random
from typing import List, Dict, Optional


class OpenAIAdapter:
    """A lightweight OpenAI Chat Completions adapter with retry/backoff.

    - Uses `OPENAI_API_KEY` or `OPENAI_KEY` from the environment.
    - If the `openai` package is present and a key is configured, it will
      make ChatCompletion requests. Calls are wrapped with simple retry
      + exponential backoff (with jitter) to increase robustness in
      production environments.
    """

    def __init__(self, model: str = "gpt-5-mini"):
        self.model = model
        self.key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_KEY")
        self._client = None
        if self.key:
            try:
                import openai  # type: ignore

                openai.api_key = self.key
                self._client = openai
            except Exception:
                # If import fails or client cannot be configured, keep _client None
                self._client = None

    def available(self) -> bool:
        return self._client is not None

    def _extract_text_from_response(self, resp) -> Optional[str]:
        try:
            if hasattr(resp, "choices"):
                choice = resp.choices[0]
            else:
                choice = resp.get("choices", [{}])[0]

            if hasattr(choice, "message"):
                msg = choice.message
                if isinstance(msg, dict):
                    return msg.get("content")
                # some SDK versions provide a Message object with .content
                return getattr(msg, "content", None)

            if isinstance(choice, dict):
                return choice.get("message", {}).get("content") or choice.get("text")
        except Exception:
            return None
        return None

    def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 256,
        temperature: float = 0.2,
        retries: int = 3,
        backoff_factor: float = 1.0,
    ) -> Optional[str]:
        """Send chat messages to the provider with retry/backoff.

        Args:
            messages: list of message dicts as per OpenAI API.
            max_tokens: generation limit.
            temperature: sampling temperature.
            retries: number of attempts (default 3).
            backoff_factor: base seconds used for exponential backoff.

        Returns:
            The text content of the first choice, or None on failure.
        """

        if not self.available():
            return None

        attempt = 0
        while attempt < retries:
            attempt += 1
            try:
                resp = self._client.ChatCompletion.create(
                    model=self.model, messages=messages, max_tokens=max_tokens, temperature=temperature
                )
                return self._extract_text_from_response(resp)
            except Exception as exc:  # noqa: BLE001 - deliberate broad catch for retry logic
                # If the error appears to be an authentication or invalid request,
                # do not retry since it won't succeed by backing off.
                msg = str(exc).lower()
                if any(term in msg for term in ("invalid api key", "authentication", "invalid request", "401")):
                    return None

                if attempt >= retries:
                    return None

                # exponential backoff with jitter
                sleep = backoff_factor * (2 ** (attempt - 1))
                sleep = sleep + random.uniform(0, 0.5)
                time.sleep(sleep)

        return None

    def summarize(self, text: str) -> Optional[str]:
        if not self.available():
            return None
        system = {"role": "system", "content": "You are a concise summarizer."}
        user = {"role": "user", "content": f"Summarize the following text in one short sentence:\n\n{text}"}
        return self.chat([system, user], max_tokens=60, temperature=0.2)


__all__ = ["OpenAIAdapter"]
