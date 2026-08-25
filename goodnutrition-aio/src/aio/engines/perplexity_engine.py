"""Perplexity via its OpenAI-compatible Sonar endpoint.

Perplexity is the outlier worth tracking: it cites brands at roughly twenty
times ChatGPT's rate, and its citation set overlaps ChatGPT's by only about a
tenth. A prospect invisible on ChatGPT may be well covered here, or the
reverse — which is exactly the kind of finding that makes an audit
persuasive rather than generic.
"""
from __future__ import annotations

import os

from ..models import Prompt
from .base import Engine, token_cost


class PerplexityEngine(Engine):
    name = "perplexity"

    BASE_URL = "https://api.perplexity.ai"

    def __init__(
        self,
        model: str = "sonar",
        input_rate: float = 1.00,
        output_rate: float = 1.00,
    ) -> None:
        self.model = model
        self.input_rate = input_rate
        self.output_rate = output_rate
        self._client = None
        self.available = bool(os.environ.get("PERPLEXITY_API_KEY"))

    @property
    def client(self):
        if self._client is None:
            from openai import OpenAI

            self._client = OpenAI(
                api_key=os.environ.get("PERPLEXITY_API_KEY"),
                base_url=self.BASE_URL,
            )
        return self._client

    def _ask(self, prompt: Prompt) -> tuple[str, list[str], float]:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt.text}],
        )

        text = (response.choices[0].message.content or "").strip()

        # Sonar returns citations alongside the standard completion payload;
        # the key has moved between revisions, so accept either spelling.
        sources: list[str] = []
        for key in ("citations", "search_results"):
            raw = getattr(response, key, None)
            if not raw:
                continue
            for entry in raw:
                url = entry if isinstance(entry, str) else (
                    entry.get("url") if isinstance(entry, dict) else None
                )
                if url:
                    sources.append(url)
            if sources:
                break

        usage = getattr(response, "usage", None)
        cost = token_cost(
            getattr(usage, "prompt_tokens", 0) or 0,
            getattr(usage, "completion_tokens", 0) or 0,
            self.input_rate,
            self.output_rate,
        )
        seen: set[str] = set()
        return text, [u for u in sources if not (u in seen or seen.add(u))], cost
