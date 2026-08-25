"""Command line entry point.

    python -m aio scan config/categories/field-service-hvac.yaml
    python -m aio prompts config/categories/field-service-hvac.yaml
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .config import load_category, load_settings
from .engines import build_engines
from .models import to_jsonable
from .prompts import build_prompt_set, summarise
from .report import render_report
from .scanner import run_scan
from .store import Store

DEFAULT_ENGINES = "claude,chatgpt,perplexity"


def _progress(done: int, total: int, answer) -> None:
    flag = " " if answer.ok else "!"
    pct = done / total * 100
    sys.stderr.write(f"\r  [{done:>3}/{total}] {pct:5.1f}% {flag} {answer.engine:<11}")
    sys.stderr.flush()
    if done == total:
        sys.stderr.write("\n")


def cmd_prompts(args: argparse.Namespace) -> int:
    spec, brands = load_category(args.config)
    prompts = build_prompt_set(spec, limit=args.limit)
    print(f"{len(prompts)} prompts for {spec.client_name} — {summarise(prompts)}\n")
    for p in prompts:
        print(f"  {p.intent.value:<13} {p.text}")
    print(f"\nTracking {len(brands)} brands: {', '.join(b.name for b in brands)}")
    return 0


def cmd_scan(args: argparse.Namespace) -> int:
    spec, brands = load_category(args.config)
    prompts = build_prompt_set(spec, limit=args.limit)
    settings = load_settings(args.settings)

    engine_names = [e.strip() for e in args.engines.split(",") if e.strip()]
    engines = build_engines(
        engine_names,
        [{"name": b.name, "domain": b.domain} for b in brands],
        settings.get("engines", {}),
    )

    skipped = [e.name for e in engines if not e.available]
    if skipped:
        print(f"  skipping (no API key): {', '.join(skipped)}", file=sys.stderr)

    store = Store(args.db)
    print(f"Scanning {spec.client_name} — {len(prompts)} prompts × "
          f"{len([e for e in engines if e.available])} engines", file=sys.stderr)

    result = run_scan(
        prompts=prompts,
        brands=brands,
        engines=engines,
        store=store,
        slug=spec.slug,
        category=spec.category,
        concurrency=args.concurrency,
        on_progress=None if args.quiet else _progress,
    )

    score = result.score
    client = score.client
    leader = score.leader

    print(f"\nScan #{result.scan_id} — {score.answers_scored} answers"
          f"{f', {score.answers_failed} failed' if score.answers_failed else ''}"
          f" · ${score.total_cost_usd:.2f}")
    if client:
        print(f"  {client.brand:<22} {client.mentions:>3} mentions "
              f"({client.mention_rate*100:4.1f}%)  "
              f"{client.citations:>3} citations  "
              f"SoV {score.share_of_voice(client.brand)*100:4.1f}%")
    if leader and client and leader.brand != client.brand:
        print(f"  {leader.brand + ' (leader)':<22} {leader.mentions:>3} mentions "
              f"({leader.mention_rate*100:4.1f}%)")

    outdir = Path(args.out)
    stem = f"{spec.slug}-{result.scan_id}"
    html_path = render_report(
        spec=spec, score=score, results=result.results,
        prompt_count=len(prompts), out_path=outdir / f"{stem}.html",
    )
    json_path = outdir / f"{stem}.json"
    json_path.write_text(json.dumps(store.export_scan(result.scan_id), indent=2))

    print(f"\n  report  {html_path}")
    print(f"  data    {json_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="aio", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_prompts = sub.add_parser("prompts", help="preview the generated prompt set")
    p_prompts.add_argument("config")
    p_prompts.add_argument("--limit", type=int, default=40)
    p_prompts.set_defaults(func=cmd_prompts)

    p_scan = sub.add_parser("scan", help="run a full scan and render the report")
    p_scan.add_argument("config")
    p_scan.add_argument("--engines", default=DEFAULT_ENGINES,
                        help=f"comma-separated (default: {DEFAULT_ENGINES}); "
                             "use 'mock' for an offline dry run")
    p_scan.add_argument("--limit", type=int, default=40)
    p_scan.add_argument("--concurrency", type=int, default=4)
    p_scan.add_argument("--db", default="data/aio.db")
    p_scan.add_argument("--out", default="reports")
    p_scan.add_argument("--settings", default="config/settings.yaml")
    p_scan.add_argument("--quiet", action="store_true")
    p_scan.set_defaults(func=cmd_scan)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (ValueError, RuntimeError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
