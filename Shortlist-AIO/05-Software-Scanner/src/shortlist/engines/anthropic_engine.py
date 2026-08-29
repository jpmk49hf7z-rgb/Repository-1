"""Claude with server-side web search.

Mirrors what a buyer sees when they ask Claude to research vendors, so the
web-search tool is on: a model answering from memory alone measures training
data, not the live answer surface a prospect is judged on.
"""
from __future__ import annotations

import os

from ..models import Prompt
from .base import Engine, token_cost

#: Per-million-token rates for the default model (Claude Opus 5).
INPUT_RATE = 5.00
OUTPUT_RATE = 25.00
#: Anthropic bills server-side web search per thousand searches.
SEARCH_COST_PER_USE = 10.00 / 1000


class AnthropicEngine(Engine):
    name = "claude"

    def __init__(self, model: str = "claude-opus-5", max_searches: int = 5) -> None:
        self.model = model
        self.max_searches = max_searches
        self._client = None
        self.available = bool(os.environ.get("ANTHROPIC_API_KEY"))

    @property
    def client(self):
        if self._client is None:
            from anthropic import Anthropic

            self._client = Anthropic()
        return self._client

    def _ask(self, prompt: Prompt) -> tuple[str, list[str], float]:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            thinking={"type": "adaptive"},
            tools=[
                {
                    "type": "web_search_20260209",
                    "name": "web_search",
                    "max_uses": self.max_searches,
                }
            ],
            messages=[{"role": "user", "content": prompt.text}],
        )

        parts: list[str] = []
        sources: list[str] = []
        searches = 0

        for block in response.content:
            kind = getattr(block, "type", "")
            if kind == "text":
                parts.append(block.text)
            elif kind == "web_search_tool_result":
                searches += 1
                # On error the content is a single object, not a list of results.
                results = getattr(block, "content", None)
                if isinstance(results, list):
                    for item in results:
                        url = getattr(item, "url", None)
                        if url:
                            sources.append(url)

        cost = token_cost(
            response.usage.input_tokens,
            response.usage.output_tokens,
            INPUT_RATE,
            OUTPUT_RATE,
        ) + searches * SEARCH_COST_PER_USE

        return "\n".join(parts).strip(), _dedupe(sources), cost


def _dedupe(urls: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out
