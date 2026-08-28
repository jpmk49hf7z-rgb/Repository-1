"""Deterministic offline engine.

Exists so the whole pipeline — prompts, detection, scoring, storage, report —
can be exercised and regression-tested without spending money or depending on
a live API. Output is seeded from the prompt text, so a given prompt always
produces the same answer.
"""
from __future__ import annotations

import hashlib
import random

from ..models import Prompt
from .base import Engine


class MockEngine(Engine):
    name = "mock"

    def __init__(self, brands: list[dict], visibility: float = 0.35) -> None:
        """``brands`` are dicts with ``name``/``domain``; the first is the client.

        ``visibility`` is the probability the client is named, letting tests
        simulate both an invisible prospect and a dominant one.
        """
        self.brands = brands
        self.visibility = visibility

    def _ask(self, prompt: Prompt) -> tuple[str, list[str], float]:
        rng = random.Random(
            int(hashlib.sha256(prompt.text.encode()).hexdigest()[:8], 16)
        )
        client, *rivals = self.brands
        named = [b for b in rivals if rng.random() < 0.6]
        if rng.random() < self.visibility:
            named.insert(rng.randint(0, len(named)), client)
        if not named:
            named = [rivals[0]] if rivals else [client]

        lead = ", ".join(b["name"] for b in named[:-1])
        joined = f"{lead} and {named[-1]['name']}" if lead else named[-1]["name"]
        text = (
            f"For this need, the options most often recommended are {joined}. "
            f"{named[0]['name']} is generally considered the strongest overall, "
            f"with good reviews and broad integration support."
        )
        sources = [f"https://{b['domain']}/" for b in named[:2]]
        sources.append("https://www.g2.com/categories/example")
        return text, sources, 0.0
