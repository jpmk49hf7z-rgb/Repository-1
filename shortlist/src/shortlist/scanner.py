"""Run a scan: ask every prompt of every engine, detect brands, score, persist.

Calls are issued concurrently because a serial scan of 40 prompts across
three engines takes long enough that nobody runs it often — and a
measurement nobody runs is not a measurement. Concurrency is capped low: the
bottleneck is provider rate limits, not local CPU, and tripping a rate limit
costs more time than it saves.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Callable

from .engines.base import Engine
from .mentions import analyse_answer
from .models import Answer, Brand, BrandHit, Prompt
from .scoring import ScanScore, score_scan
from .store import Store

#: Concurrent in-flight requests per engine.
DEFAULT_CONCURRENCY = 4


@dataclass
class ScanResult:
    scan_id: int
    score: ScanScore
    results: list[tuple[Answer, list[BrandHit]]]


def run_scan(
    *,
    prompts: list[Prompt],
    brands: list[Brand],
    engines: list[Engine],
    store: Store,
    slug: str,
    category: str,
    concurrency: int = DEFAULT_CONCURRENCY,
    on_progress: Callable[[int, int, Answer], None] | None = None,
) -> ScanResult:
    """Execute a full scan and return its scored result."""
    live = [e for e in engines if e.available]
    if not live:
        raise RuntimeError(
            "no engines available — set the relevant API keys, or use --engines mock"
        )

    client = next((b for b in brands if b.is_client), brands[0])
    scan_id = store.start_scan(
        slug=slug,
        client_name=client.name,
        client_domain=client.domain,
        category=category,
        engines=[e.name for e in live],
        prompt_count=len(prompts),
    )

    jobs = [(engine, prompt) for engine in live for prompt in prompts]
    results: list[tuple[Answer, list[BrandHit]]] = []
    total = len(jobs)

    with ThreadPoolExecutor(max_workers=max(1, concurrency * len(live))) as pool:
        futures = {pool.submit(engine.ask, prompt): (engine, prompt)
                   for engine, prompt in jobs}
        for done, future in enumerate(as_completed(futures), start=1):
            answer = future.result()          # ask() never raises
            hits = analyse_answer(answer, brands) if answer.ok else []
            store.record(scan_id, answer, hits)
            results.append((answer, hits))
            if on_progress:
                on_progress(done, total, answer)

    score = score_scan(results, brands)
    store.finish_scan(scan_id, score.total_cost_usd)
    return ScanResult(scan_id=scan_id, score=score, results=results)
