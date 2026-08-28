"""Core data types shared across the scanner.

Kept dependency-free and JSON-serialisable so results can be persisted,
diffed between runs, and handed to the report layer without adaptation.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class Intent(str, Enum):
    """Buyer-intent class of a prompt.

    These are not decoration: discovery and alternatives prompts are where
    shortlists actually form, so they are weighted higher when scoring.
    """

    DISCOVERY = "discovery"          # "best X software"
    ALTERNATIVES = "alternatives"    # "alternatives to A"
    COMPARISON = "comparison"        # "A vs B"
    USE_CASE = "use_case"            # "X for Y"
    CRITERIA = "criteria"            # "X with feature F"
    PROBLEM = "problem"              # "how do I solve Z"


#: Relative weight of each intent when computing a weighted visibility score.
INTENT_WEIGHTS: dict[Intent, float] = {
    Intent.DISCOVERY: 1.5,
    Intent.ALTERNATIVES: 1.3,
    Intent.COMPARISON: 1.0,
    Intent.USE_CASE: 1.0,
    Intent.CRITERIA: 0.8,
    Intent.PROBLEM: 0.6,
}


@dataclass(frozen=True)
class Brand:
    """A tracked vendor — the client or one of its competitors.

    ``ambiguous`` marks brands whose name collides with ordinary English
    ("Notion", "Monday", "Front"). Those require stricter matching; see
    :mod:`shortlist.mentions`.
    """

    name: str
    domain: str
    aliases: tuple[str, ...] = ()
    is_client: bool = False
    ambiguous: bool = False

    @property
    def all_names(self) -> tuple[str, ...]:
        return (self.name, *self.aliases)


@dataclass(frozen=True)
class Prompt:
    """One buyer question, asked verbatim to every engine."""

    text: str
    intent: Intent

    @property
    def id(self) -> str:
        """Stable hash so the same question can be tracked across runs."""
        return hashlib.sha256(self.text.strip().lower().encode()).hexdigest()[:12]


@dataclass
class Answer:
    """One engine's response to one prompt."""

    prompt_id: str
    prompt_text: str
    intent: Intent
    engine: str
    text: str
    sources: list[str] = field(default_factory=list)
    error: str | None = None
    cost_usd: float = 0.0
    latency_ms: int = 0
    fetched_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")
    )

    @property
    def ok(self) -> bool:
        return self.error is None and bool(self.text.strip())


@dataclass
class BrandHit:
    """Evidence that one brand appeared in one answer.

    ``mentioned`` and ``cited`` are deliberately separate. Engines routinely
    name a vendor without linking to it, and the two carry different weight:
    a citation drives referral traffic, a mention drives the shortlist.
    """

    brand: str
    mentioned: bool
    cited: bool
    first_position: int | None = None   # char offset of first mention
    rank: int | None = None             # 1-based order among brands in the answer
    evidence: str = ""                  # surrounding text, for the report

    @property
    def present(self) -> bool:
        return self.mentioned or self.cited


def to_jsonable(obj: Any) -> Any:
    """Recursively convert dataclasses/enums into JSON-safe primitives."""
    if hasattr(obj, "__dataclass_fields__"):
        return {k: to_jsonable(v) for k, v in asdict(obj).items()}
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, (list, tuple)):
        return [to_jsonable(v) for v in obj]
    if isinstance(obj, dict):
        return {k: to_jsonable(v) for k, v in obj.items()}
    return obj
