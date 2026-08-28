"""Detect brand mentions and citations inside engine answers.

This is the correctness-critical layer of the scanner: every headline number
we put in front of a prospect is downstream of it. Two failure modes matter,
and they pull in opposite directions.

*False positives* come from brand names that are ordinary English words —
Notion, Monday, Front, Ramp, Loop. Substring matching reports these
everywhere and inflates a prospect's apparent visibility, which is the
embarrassing direction to be wrong in during a sales call.

*False negatives* come from over-strict matching that misses possessives
("Jobber's"), domain-only references ("see jobber.com"), or a brand named
only in the source list rather than the prose.

The approach: word-boundary matching by default, and for names flagged
``ambiguous`` an additional gate — the match must be capitalised as the
brand is, or corroborated by the brand's domain or a nearby product word.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from .models import Answer, Brand, BrandHit

#: Words that read as ordinary English and therefore need corroboration.
#: Used to auto-flag brands when a category config does not say either way.
COMMON_WORD_NAMES: frozenset[str] = frozenset(
    {
        "asana", "front", "loop", "ramp", "notion", "monday", "slack", "stripe",
        "square", "shift", "pipe", "brex", "deel", "rippling", "gusto", "atlas",
        "arc", "linear", "height", "sift", "drift", "intercom", "amplitude",
        "mixpanel", "segment", "census", "fivetran", "prefect", "dagster",
        "airtable", "coda", "guru", "lattice", "culture", "bob", "sage", "wave",
        "jane", "harvest", "toggl", "clockify", "float", "forecast", "motion",
        "sunsama", "reclaim", "clockwise", "vanta", "drata", "secureframe",
    }
)

#: Product words that corroborate an ambiguous name in the surrounding text.
_CONTEXT_WORDS = (
    "software", "platform", "tool", "app", "vendor", "solution", "system",
    "product", "saas", "suite", "provider", "pricing", "plan", "dashboard",
)
_CONTEXT_RE = re.compile("|".join(_CONTEXT_WORDS), re.IGNORECASE)

#: How far either side of a match to look for a corroborating product word.
_CONTEXT_WINDOW = 70

#: How much surrounding text to keep as report evidence.
_EVIDENCE_WINDOW = 90


def looks_ambiguous(name: str) -> bool:
    """True if ``name`` collides with ordinary English and needs corroboration."""
    return name.strip().lower() in COMMON_WORD_NAMES


def _name_pattern(name: str) -> re.Pattern[str]:
    """Word-boundary pattern for a brand name, tolerating possessives.

    Uses explicit lookarounds rather than ``\\b`` because brand names often
    contain punctuation ("monday.com", "E-Z Rent") where ``\\b`` misbehaves.
    A leading hyphen is excluded so "Pilot" does not match inside "co-pilot";
    a trailing hyphen is allowed so "Jobber-based" still counts.
    """
    escaped = re.escape(name.strip())
    return re.compile(
        rf"(?<![A-Za-z0-9\-]){escaped}(?:'s|’s)?(?![A-Za-z0-9])",
        re.IGNORECASE,
    )


def normalise_host(url: str) -> str:
    """Reduce a URL or bare host to a comparable lowercase hostname."""
    raw = url.strip().lower()
    if not raw:
        return ""
    if "//" not in raw:
        raw = "//" + raw
    host = urlparse(raw).hostname or ""
    return host[4:] if host.startswith("www.") else host


def _domain_matches(candidate: str, domain: str) -> bool:
    """True if ``candidate`` host is ``domain`` or a subdomain of it."""
    host = normalise_host(candidate)
    target = normalise_host(domain)
    if not host or not target:
        return False
    return host == target or host.endswith("." + target)


def _cited_in_sources(sources: list[str], domain: str) -> bool:
    return any(_domain_matches(s, domain) for s in sources)


def _corroborated(text: str, match: re.Match[str], brand: Brand) -> bool:
    """Decide whether an ambiguous-name match is really the brand.

    Accepts the match when it is capitalised the way the brand is, when the
    brand's domain appears anywhere in the text, or when a product word sits
    close by.
    """
    matched = match.group(0)
    # Capitalised exactly as the brand writes it — strongest cheap signal.
    if matched[:1].isupper() and not matched.isupper():
        return True
    if brand.domain and brand.domain.lower() in text.lower():
        return True
    start = max(0, match.start() - _CONTEXT_WINDOW)
    end = min(len(text), match.end() + _CONTEXT_WINDOW)
    return bool(_CONTEXT_RE.search(text[start:end]))


def _evidence(text: str, start: int, end: int) -> str:
    left = max(0, start - _EVIDENCE_WINDOW)
    right = min(len(text), end + _EVIDENCE_WINDOW)
    snippet = " ".join(text[left:right].split())
    return ("…" if left > 0 else "") + snippet + ("…" if right < len(text) else "")


def find_brand(answer: Answer, brand: Brand) -> BrandHit:
    """Locate ``brand`` within a single ``answer``."""
    text = answer.text or ""
    ambiguous = brand.ambiguous or looks_ambiguous(brand.name)

    first: re.Match[str] | None = None
    for name in brand.all_names:
        # An alias that is itself a domain is matched by the domain rule below.
        if not name.strip():
            continue
        for match in _name_pattern(name).finditer(text):
            if ambiguous and not _corroborated(text, match, brand):
                continue
            if first is None or match.start() < first.start():
                first = match
            break  # first accepted match per alias is enough

    # A bare domain in the prose counts as a mention even with no name match.
    if first is None and brand.domain:
        domain_match = _name_pattern(brand.domain).search(text)
        if domain_match is not None:
            first = domain_match

    cited = _cited_in_sources(answer.sources, brand.domain) if brand.domain else False

    return BrandHit(
        brand=brand.name,
        mentioned=first is not None,
        cited=cited,
        first_position=first.start() if first else None,
        evidence=_evidence(text, first.start(), first.end()) if first else "",
    )


def analyse_answer(answer: Answer, brands: list[Brand]) -> list[BrandHit]:
    """Locate every tracked brand in one answer and rank them by order of first mention.

    Rank matters commercially: being named ninth in a list of ten is not the
    same outcome as being named first, and shortlists have compressed to
    roughly two or three names.
    """
    hits = [find_brand(answer, b) for b in brands]

    ordered = sorted(
        (h for h in hits if h.first_position is not None),
        key=lambda h: h.first_position,  # type: ignore[arg-type,return-value]
    )
    for rank, hit in enumerate(ordered, start=1):
        hit.rank = rank
    return hits
