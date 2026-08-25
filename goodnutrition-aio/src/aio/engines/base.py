"""Engine adapter contract and shared retry/cost plumbing.

Every answer engine we measure — ChatGPT, Claude, Perplexity, Google AI
Overviews — is reached through a different API with a different response
shape. Adapters normalise them to a single :class:`~aio.models.Answer`.

Two rules hold for every adapter:

1. **An adapter never raises into the scan.** A failed call returns an
   ``Answer`` carrying ``error``. Scoring excludes failures from its
   denominators, so a flaky engine degrades coverage rather than silently
   reporting a prospect as invisible.
2. **Every adapter reports its own cost.** Per-scan spend is a headline number
   in the business model, so it is measured rather than estimated after
   the fact.
"""
from __future__ import annotations

import random
import time
from abc import ABC, abstractmethod

from ..models import Answer, Prompt

#: Attempts per prompt before giving up, including the first.
MAX_ATTEMPTS = 3


class EngineError(RuntimeError):
    """Raised inside an adapter's ``_ask``; converted to a failed Answer."""


class Engine(ABC):
    """Base adapter. Subclasses implement :meth:`_ask` only."""

    #: Short stable identifier used in reports and the database.
    name: str = "engine"

    #: Set False when the adapter lacks credentials, so a scan can skip it
    #: cleanly instead of producing a wall of identical auth failures.
    available: bool = True

    def ask(self, prompt: Prompt) -> Answer:
        """Ask one prompt, retrying transient failures with jittered backoff."""
        started = time.monotonic()
        last_error = "unknown error"

        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                text, sources, cost = self._ask(prompt)
                return Answer(
                    prompt_id=prompt.id,
                    prompt_text=prompt.text,
                    intent=prompt.intent,
                    engine=self.name,
                    text=text,
                    sources=sources,
                    cost_usd=cost,
                    latency_ms=int((time.monotonic() - started) * 1000),
                )
            except Exception as exc:  # noqa: BLE001 - adapters must not escape
                last_error = f"{type(exc).__name__}: {exc}"
                if attempt < MAX_ATTEMPTS and self._retryable(exc):
                    time.sleep(min(2**attempt, 8) + random.uniform(0, 0.75))
                    continue
                break

        return Answer(
            prompt_id=prompt.id,
            prompt_text=prompt.text,
            intent=prompt.intent,
            engine=self.name,
            text="",
            error=last_error,
            latency_ms=int((time.monotonic() - started) * 1000),
        )

    @staticmethod
    def _retryable(exc: Exception) -> bool:
        """Retry rate limits, timeouts, and 5xx; never retry a bad request."""
        marker = f"{type(exc).__name__} {exc}".lower()
        if any(w in marker for w in ("badrequest", "invalid_request", "notfound", "permission")):
            return False
        return any(
            w in marker
            for w in ("ratelimit", "timeout", "connection", "overloaded",
                      "internal", "unavailable", "502", "503", "504", "529")
        )

    @abstractmethod
    def _ask(self, prompt: Prompt) -> tuple[str, list[str], float]:
        """Return ``(answer_text, source_urls, cost_usd)`` or raise."""


def token_cost(in_tokens: int, out_tokens: int, in_rate: float, out_rate: float) -> float:
    """Cost in USD from token counts and per-million-token rates."""
    return (in_tokens / 1_000_000) * in_rate + (out_tokens / 1_000_000) * out_rate
