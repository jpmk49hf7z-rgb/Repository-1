"""ChatGPT with web search, via the OpenAI Responses API.

ChatGPT is the engine that matters most commercially — it is where the
majority of B2B software buyers start — and also the stingiest with brand
citations, so mention rate rather than citation rate is the number to watch
here.

The model id and web-search tool type are configuration rather than
constants: OpenAI renames both more often than the other providers, and a
rename should be a settings edit, not a code change.
"""
from __future__ import annotations

import os

from ..models import Prompt
from .base import Engine, token_cost


class OpenAIEngine(Engine):
    name = "chatgpt"

    def __init__(
        self,
        model: str = "gpt-5.6",
        tool_type: str = "web_search",
        input_rate: float = 2.00,
        output_rate: float = 12.00,
    ) -> None:
        self.model = model
        self.tool_type = tool_type
        self.input_rate = input_rate
        self.output_rate = output_rate
        self._client = None
        self.available = bool(os.environ.get("OPENAI_API_KEY"))

    @property
    def client(self):
        if self._client is None:
            from openai import OpenAI

            self._client = OpenAI()
        return self._client

    def _ask(self, prompt: Prompt) -> tuple[str, list[str], float]:
        response = self.client.responses.create(
            model=self.model,
            tools=[{"type": self.tool_type}],
            input=prompt.text,
        )

        text = (getattr(response, "output_text", "") or "").strip()
        sources = _citation_urls(response)

        usage = getattr(response, "usage", None)
        cost = token_cost(
            getattr(usage, "input_tokens", 0) or 0,
            getattr(usage, "output_tokens", 0) or 0,
            self.input_rate,
            self.output_rate,
        )
        return text, sources, cost


def _citation_urls(response) -> list[str]:
    """Pull URL citations out of the Responses payload.

    Walks defensively rather than indexing a fixed path — annotation shapes
    have changed between API revisions, and a missing citation should cost us
    one source, not the whole answer.
    """
    urls: list[str] = []
    for item in getattr(response, "output", None) or []:
        for content in getattr(item, "content", None) or []:
            for annotation in getattr(content, "annotations", None) or []:
                url = getattr(annotation, "url", None)
                if url:
                    urls.append(url)
    seen: set[str] = set()
    return [u for u in urls if not (u in seen or seen.add(u))]
