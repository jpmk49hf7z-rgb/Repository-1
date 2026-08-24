"""Load a category config and turn it into a spec plus tracked brands."""
from __future__ import annotations

from pathlib import Path

import yaml

from .mentions import looks_ambiguous
from .models import Brand
from .prompts import CategorySpec

REQUIRED = ("slug", "category", "audience", "client")


def load_category(path: str | Path) -> tuple[CategorySpec, list[Brand]]:
    """Read a category YAML file into a :class:`CategorySpec` and brand list.

    Fails loudly on a malformed config. A silently half-loaded config would
    produce a plausible-looking report built on the wrong competitor set,
    which is worse than an error.
    """
    path = Path(path)
    raw = yaml.safe_load(path.read_text()) or {}

    missing = [k for k in REQUIRED if not raw.get(k)]
    if missing:
        raise ValueError(f"{path}: missing required key(s): {', '.join(missing)}")

    client = raw["client"]
    if not client.get("name") or not client.get("domain"):
        raise ValueError(f"{path}: client needs both 'name' and 'domain'")

    competitors = raw.get("competitors") or []
    for c in competitors:
        if not c.get("name") or not c.get("domain"):
            raise ValueError(f"{path}: every competitor needs 'name' and 'domain'")
    if not competitors:
        raise ValueError(f"{path}: at least one competitor is required — "
                         "share of voice is meaningless without a comparison set")

    spec = CategorySpec(
        slug=raw["slug"],
        category=raw["category"],
        audience=raw["audience"],
        client_name=client["name"],
        client_domain=client["domain"],
        client_aliases=list(client.get("aliases") or []),
        competitors=competitors,
        use_cases=list(raw.get("use_cases") or []),
        buying_criteria=list(raw.get("buying_criteria") or []),
        problems=list(raw.get("problems") or []),
        geo=raw.get("geo", "") or "",
    )

    brands = [
        Brand(
            name=client["name"],
            domain=client["domain"],
            aliases=tuple(client.get("aliases") or []),
            is_client=True,
            ambiguous=bool(client.get("ambiguous", looks_ambiguous(client["name"]))),
        )
    ]
    for c in competitors:
        brands.append(
            Brand(
                name=c["name"],
                domain=c["domain"],
                aliases=tuple(c.get("aliases") or []),
                ambiguous=bool(c.get("ambiguous", looks_ambiguous(c["name"]))),
            )
        )
    return spec, brands


def load_settings(path: str | Path | None) -> dict:
    """Optional engine settings (model ids, rates). Absent file is fine."""
    if not path:
        return {}
    p = Path(path)
    return (yaml.safe_load(p.read_text()) or {}) if p.exists() else {}
