#!/usr/bin/env python3
"""Render the legal Markdown files into site pages.

Keeps ../legal/*.md as the single source of truth. Editing a policy in one
place and forgetting the other is exactly the kind of drift that turns a
privacy policy into a liability, so the published pages are generated rather
than maintained.

    python build.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import markdown

SITE = Path(__file__).parent
LEGAL = SITE.parent / "legal"

PAGES = [
    ("privacy-policy.md", "privacy.html", "Privacy Policy"),
    ("website-terms.md", "terms.html", "Terms of Use"),
]

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — Shortlist</title>
<meta name="robots" content="noindex">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<link rel="stylesheet" href="styles.css">
</head>
<body>
<header class="site"><div class="wrap"><div class="bar">
  <a class="wordmark" href="/">Short<span>list</span></a>
  <nav><a href="/privacy.html">Privacy</a><a href="/terms.html">Terms</a></nav>
</div></div></header>
<div class="wrap narrow doc">
<section>
{body}
</section>
</div>
<footer class="site"><div class="wrap">
  <nav><a href="/">Home</a><a href="/privacy.html">Privacy</a><a href="/terms.html">Terms</a></nav>
  <p><strong>Shortlist</strong> is operated by [COMPANY LEGAL NAME], a Manitoba corporation.</p>
</div></footer>
</body>
</html>
"""

#: Anything inside a blockquote that starts with these markers is an internal
#: note to counsel and must never reach the published site.
DRAFT_MARKERS = ("DRAFT FOR REVIEW", "[COUNSEL]", "NOT LEGAL ADVICE")


def strip_draft_notes(md: str) -> tuple[str, int]:
    """Remove blockquote blocks carrying internal review notes.

    Publishing a policy with "[COUNSEL] confirm this is enforceable" still in
    it would be worse than having no policy at all.
    """
    lines = md.splitlines()
    out: list[str] = []
    removed = 0
    i = 0
    while i < len(lines):
        if lines[i].lstrip().startswith(">"):
            block = []
            while i < len(lines) and (lines[i].lstrip().startswith(">") or not lines[i].strip()):
                if not lines[i].strip() and block:
                    break
                block.append(lines[i])
                i += 1
            text = "\n".join(block)
            if any(m in text for m in DRAFT_MARKERS):
                removed += 1
                continue
            out.extend(block)
            continue
        out.append(lines[i])
        i += 1
    return "\n".join(out), removed


def check_clean(html: str, name: str) -> list[str]:
    """Fail the build on anything that should not be public."""
    problems = []
    for marker in DRAFT_MARKERS:
        if marker in html:
            problems.append(f"{name}: still contains {marker!r}")
    if re.search(r"\[[A-Z][A-Z0-9 _/,'’.\-]{2,}\]", html):
        placeholders = set(re.findall(r"\[[A-Z][A-Z0-9 _/,'’.\-]{2,}\]", html))
        problems.append(f"{name}: unfilled placeholders {sorted(placeholders)}")
    return problems


def main() -> int:
    problems: list[str] = []
    for src, dest, title in PAGES:
        path = LEGAL / src
        if not path.exists():
            print(f"missing source: {path}", file=sys.stderr)
            return 1

        md, removed = strip_draft_notes(path.read_text())
        body = markdown.markdown(md, extensions=["tables", "sane_lists"])
        # The H1 is replaced by the page title in the template.
        body = re.sub(r"<h1>.*?</h1>", f"<h2>{title}</h2>", body, count=1, flags=re.S)

        (SITE / dest).write_text(TEMPLATE.format(title=title, body=body), encoding="utf-8")
        found = check_clean(body, dest)
        problems += found
        status = "OK" if not found else "NEEDS ATTENTION"
        print(f"  {src:26} -> {dest:14} ({removed} draft note(s) stripped)  {status}")

    if problems:
        print("\nNot ready to publish:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        print("\nFill the bracketed fields in ../legal/ before deploying.", file=sys.stderr)
        return 1

    print("\nAll pages clean.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
