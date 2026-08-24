"""Generate the buyer-intent prompt set for a category.

The prompt set is the measurement instrument, so it has to be stable and
reproducible: the same category config must always yield the same prompts in
the same order, or week-over-week comparisons are meaningless. Nothing here
is random.

Prompts are written the way buyers actually type them — short, unpunctuated,
occasionally clumsy — rather than the way a marketer would phrase them.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .models import Intent, Prompt


def singular(noun: str) -> str:
    """Crude but safe singulariser for audience nouns.

    Only needs to handle the head noun of an audience phrase ("HVAC
    contractors" -> "HVAC contractor"). A naive ``rstrip("s")`` mangles words
    like "businesses", which then reaches a live engine and skews the answer.
    """
    head, _, _ = noun.partition(",")
    words = head.split()
    if not words:
        return noun
    last = words[-1]
    if re.search(r"(ses|xes|zes|ches|shes)$", last, re.IGNORECASE):
        words[-1] = last[:-2]
    elif re.search(r"[^aeiou]ies$", last, re.IGNORECASE):
        words[-1] = last[:-3] + "y"
    elif last.lower().endswith("s") and not last.lower().endswith("ss"):
        words[-1] = last[:-1]
    return " ".join(words)


def article(word: str) -> str:
    """Pick "a" or "an" by sound, not just by first letter.

    Acronyms carry their own pronunciation: "an HVAC contractor", "an RFP",
    but "a SaaS tool".
    """
    first = word.strip().split()[0] if word.strip() else ""
    if not first:
        return "a"
    # Acronym: judge by how the leading letter is spoken.
    if first.isupper() and len(first) > 1:
        return "an" if first[0] in "AEFHILMNORSX" else "a"
    return "an" if first[0].lower() in "aeiou" else "a"


@dataclass
class CategorySpec:
    """Everything needed to generate a prompt set and score the results."""

    slug: str
    category: str                       # "field service management software"
    audience: str                       # "HVAC contractors"
    client_name: str
    client_domain: str
    competitors: list[dict] = field(default_factory=list)
    use_cases: list[str] = field(default_factory=list)
    buying_criteria: list[str] = field(default_factory=list)
    problems: list[str] = field(default_factory=list)
    client_aliases: list[str] = field(default_factory=list)
    geo: str = ""

    @property
    def competitor_names(self) -> list[str]:
        return [c["name"] for c in self.competitors]


def _dedupe(prompts: list[Prompt]) -> list[Prompt]:
    """Drop duplicates while preserving generation order."""
    seen: set[str] = set()
    out: list[Prompt] = []
    for p in prompts:
        if p.id not in seen:
            seen.add(p.id)
            out.append(p)
    return out


def build_prompt_set(spec: CategorySpec, limit: int = 40) -> list[Prompt]:
    """Build the ordered prompt set for ``spec``.

    Generated in intent priority order and then truncated, so a smaller
    ``limit`` keeps the prompts that decide shortlists rather than an
    arbitrary slice.
    """
    cat, aud = spec.category, spec.audience
    aud_one = singular(aud)
    art = article(aud_one)
    geo = f" in {spec.geo}" if spec.geo else ""
    out: list[Prompt] = []

    def add(text: str, intent: Intent) -> None:
        out.append(Prompt(" ".join(text.split()), intent))

    # Discovery — where shortlists are actually formed.
    add(f"best {cat}", Intent.DISCOVERY)
    add(f"best {cat} for {aud}", Intent.DISCOVERY)
    add(f"top {cat} for {aud}{geo}", Intent.DISCOVERY)
    add(f"what {cat} should I use as {art} {aud_one}", Intent.DISCOVERY)
    add(f"most popular {cat} for small {aud_one} businesses", Intent.DISCOVERY)
    add(f"affordable {cat} for {aud}", Intent.DISCOVERY)
    add(f"recommend {cat} for a growing {aud_one} company", Intent.DISCOVERY)
    add(f"which {cat} do {aud} actually recommend", Intent.DISCOVERY)
    add(f"{cat} reviews from real {aud}", Intent.DISCOVERY)

    # Alternatives — high intent, and where an incumbent's customers leak.
    for name in spec.competitor_names[:4]:
        add(f"alternatives to {name}", Intent.ALTERNATIVES)
    for name in spec.competitor_names[:2]:
        add(f"cheaper alternative to {name} for {aud}", Intent.ALTERNATIVES)

    # Comparison — head-to-head, including the client where known.
    names = spec.competitor_names
    for i, a in enumerate(names[:3]):
        for b in names[i + 1 : 4]:
            add(f"{a} vs {b}", Intent.COMPARISON)
    for name in names[:3]:
        add(f"{spec.client_name} vs {name}", Intent.COMPARISON)

    # Use case.
    for uc in spec.use_cases[:6]:
        add(f"best {cat} for {uc}", Intent.USE_CASE)

    # Buying criteria.
    for crit in spec.buying_criteria[:6]:
        add(f"{cat} with {crit}", Intent.CRITERIA)
        add(f"does any {cat} support {crit}", Intent.CRITERIA)

    # Problem-led — the buyer does not yet know the category name.
    for prob in spec.problems[:6]:
        add(f"how do I stop {prob}", Intent.PROBLEM)
        add(f"software to fix {prob}", Intent.PROBLEM)

    return _dedupe(out)[:limit]


def summarise(prompts: list[Prompt]) -> dict[str, int]:
    """Count prompts by intent — used to sanity-check a category config."""
    counts: dict[str, int] = {}
    for p in prompts:
        counts[p.intent.value] = counts.get(p.intent.value, 0) + 1
    return counts
