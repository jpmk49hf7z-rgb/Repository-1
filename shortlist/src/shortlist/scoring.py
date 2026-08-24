"""Aggregate per-answer brand hits into the numbers that go in the report.

Three metrics, deliberately kept distinct because they say different things:

``mention_rate``   how often an engine names the brand at all — this is what
                   drives shortlist inclusion.
``citation_rate``  how often an engine links to the brand's own domain — this
                   is what drives referral traffic, and it is typically far
                   lower than mention rate.
``share_of_voice`` the brand's mentions as a fraction of all tracked-brand
                   mentions — the competitive number, and the one that makes
                   a prospect uncomfortable in a useful way.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean

from .models import INTENT_WEIGHTS, Answer, Brand, BrandHit, Intent


@dataclass
class BrandScore:
    brand: str
    is_client: bool = False
    answers_scored: int = 0
    mentions: int = 0
    citations: int = 0
    weighted_mentions: float = 0.0
    ranks: list[int] = field(default_factory=list)
    by_engine: dict[str, dict[str, int]] = field(default_factory=dict)
    by_intent: dict[str, dict[str, int]] = field(default_factory=dict)

    @property
    def mention_rate(self) -> float:
        return self.mentions / self.answers_scored if self.answers_scored else 0.0

    @property
    def citation_rate(self) -> float:
        return self.citations / self.answers_scored if self.answers_scored else 0.0

    @property
    def average_rank(self) -> float | None:
        return round(mean(self.ranks), 2) if self.ranks else None

    @property
    def first_place_count(self) -> int:
        return sum(1 for r in self.ranks if r == 1)


@dataclass
class ScanScore:
    """Whole-scan result: per-brand scores plus the derived headline figures."""

    brands: dict[str, BrandScore] = field(default_factory=dict)
    answers_scored: int = 0
    answers_failed: int = 0
    total_cost_usd: float = 0.0
    engines: list[str] = field(default_factory=list)

    @property
    def total_weighted_mentions(self) -> float:
        return sum(b.weighted_mentions for b in self.brands.values())

    def share_of_voice(self, brand: str) -> float:
        """Weighted share of all tracked-brand mentions."""
        total = self.total_weighted_mentions
        if not total:
            return 0.0
        score = self.brands.get(brand)
        return (score.weighted_mentions / total) if score else 0.0

    @property
    def client(self) -> BrandScore | None:
        return next((b for b in self.brands.values() if b.is_client), None)

    @property
    def leader(self) -> BrandScore | None:
        """Highest-mention brand — the one the prospect is losing to."""
        return max(self.brands.values(), key=lambda b: b.mentions, default=None)

    def ranked(self) -> list[BrandScore]:
        return sorted(
            self.brands.values(),
            key=lambda b: (b.weighted_mentions, b.mentions, b.citations),
            reverse=True,
        )


def _bump(bucket: dict[str, dict[str, int]], key: str, hit: BrandHit) -> None:
    slot = bucket.setdefault(key, {"scored": 0, "mentions": 0, "citations": 0})
    slot["scored"] += 1
    slot["mentions"] += int(hit.mentioned)
    slot["citations"] += int(hit.cited)


def score_scan(
    results: list[tuple[Answer, list[BrandHit]]], brands: list[Brand]
) -> ScanScore:
    """Fold per-answer hits into a :class:`ScanScore`.

    Failed answers are counted separately and excluded from every
    denominator — an engine timing out is not evidence of invisibility, and
    quietly folding it in would understate a prospect's true position.
    """
    scan = ScanScore()
    by_name = {b.name: b for b in brands}
    for b in brands:
        scan.brands[b.name] = BrandScore(brand=b.name, is_client=b.is_client)

    for answer, hits in results:
        if not answer.ok:
            scan.answers_failed += 1
            scan.total_cost_usd += answer.cost_usd
            continue

        scan.answers_scored += 1
        scan.total_cost_usd += answer.cost_usd
        if answer.engine not in scan.engines:
            scan.engines.append(answer.engine)

        weight = INTENT_WEIGHTS.get(answer.intent, 1.0)
        for hit in hits:
            score = scan.brands.get(hit.brand)
            if score is None or hit.brand not in by_name:
                continue
            score.answers_scored += 1
            score.mentions += int(hit.mentioned)
            score.citations += int(hit.cited)
            if hit.mentioned:
                score.weighted_mentions += weight
            if hit.rank is not None:
                score.ranks.append(hit.rank)
            _bump(score.by_engine, answer.engine, hit)
            _bump(score.by_intent, answer.intent.value, hit)

    return scan
