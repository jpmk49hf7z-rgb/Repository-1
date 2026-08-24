"""Answer-engine adapters."""
from .base import Engine, EngineError, token_cost
from .mock import MockEngine

__all__ = ["Engine", "EngineError", "token_cost", "MockEngine", "build_engines"]


def build_engines(names: list[str], brands: list[dict], settings: dict | None = None) -> list[Engine]:
    """Instantiate the requested engines, skipping any without credentials.

    Import of the real adapters is deferred so an operator running an offline
    mock scan never needs the provider SDKs installed.
    """
    settings = settings or {}
    engines: list[Engine] = []

    for name in names:
        key = name.strip().lower()
        opts = dict(settings.get(key, {}) or {})

        if key == "mock":
            engines.append(MockEngine(brands, **opts))
            continue
        if key in ("claude", "anthropic"):
            from .anthropic_engine import AnthropicEngine

            engines.append(AnthropicEngine(**opts))
            continue
        if key in ("chatgpt", "openai"):
            from .openai_engine import OpenAIEngine

            engines.append(OpenAIEngine(**opts))
            continue
        if key == "perplexity":
            from .perplexity_engine import PerplexityEngine

            engines.append(PerplexityEngine(**opts))
            continue
        raise ValueError(f"unknown engine: {name!r}")

    return engines
