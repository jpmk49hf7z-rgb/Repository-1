"""SQLite persistence for scans.

Every scan is kept in full — prompts, raw answers, sources, per-brand hits.
Two reasons this is not optional:

* **Week-over-week movement is the product.** A client pays for a trend line,
  and a trend line needs history that was captured before anyone knew which
  direction it would go.
* **The aggregate becomes the moat.** Every prospect scan feeds the dataset
  behind the published Citation Index, which is the inbound engine.

Stored in a single file so it is trivial to back up and needs no server.
"""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from .models import Answer, BrandHit, to_jsonable

SCHEMA = """
CREATE TABLE IF NOT EXISTS scans (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    slug          TEXT NOT NULL,
    client_name   TEXT NOT NULL,
    client_domain TEXT NOT NULL,
    category      TEXT NOT NULL,
    started_at    TEXT NOT NULL,
    finished_at   TEXT,
    engines       TEXT NOT NULL,
    prompt_count  INTEGER NOT NULL DEFAULT 0,
    cost_usd      REAL NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS answers (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_id     INTEGER NOT NULL REFERENCES scans(id) ON DELETE CASCADE,
    prompt_id   TEXT NOT NULL,
    prompt_text TEXT NOT NULL,
    intent      TEXT NOT NULL,
    engine      TEXT NOT NULL,
    text        TEXT NOT NULL,
    sources     TEXT NOT NULL,
    error       TEXT,
    cost_usd    REAL NOT NULL DEFAULT 0,
    latency_ms  INTEGER NOT NULL DEFAULT 0,
    fetched_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS hits (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_id   INTEGER NOT NULL REFERENCES scans(id) ON DELETE CASCADE,
    answer_id INTEGER NOT NULL REFERENCES answers(id) ON DELETE CASCADE,
    brand     TEXT NOT NULL,
    mentioned INTEGER NOT NULL,
    cited     INTEGER NOT NULL,
    rank      INTEGER,
    evidence  TEXT NOT NULL DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_answers_scan ON answers(scan_id);
CREATE INDEX IF NOT EXISTS idx_hits_scan ON hits(scan_id, brand);
CREATE INDEX IF NOT EXISTS idx_scans_slug ON scans(slug, started_at);
"""


class Store:
    def __init__(self, path: str | Path = "data/aio.db") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.executescript(SCHEMA)

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def start_scan(
        self, slug: str, client_name: str, client_domain: str,
        category: str, engines: list[str], prompt_count: int,
    ) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                """INSERT INTO scans
                   (slug, client_name, client_domain, category, started_at,
                    engines, prompt_count)
                   VALUES (?,?,?,?,?,?,?)""",
                (slug, client_name, client_domain, category,
                 datetime.now(timezone.utc).isoformat(timespec="seconds"),
                 json.dumps(engines), prompt_count),
            )
            return int(cur.lastrowid)

    def record(self, scan_id: int, answer: Answer, hits: list[BrandHit]) -> None:
        """Persist one answer and its brand hits in a single transaction."""
        with self._connect() as conn:
            cur = conn.execute(
                """INSERT INTO answers
                   (scan_id, prompt_id, prompt_text, intent, engine, text,
                    sources, error, cost_usd, latency_ms, fetched_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (scan_id, answer.prompt_id, answer.prompt_text,
                 answer.intent.value, answer.engine, answer.text,
                 json.dumps(answer.sources), answer.error, answer.cost_usd,
                 answer.latency_ms, answer.fetched_at),
            )
            answer_id = int(cur.lastrowid)
            conn.executemany(
                """INSERT INTO hits
                   (scan_id, answer_id, brand, mentioned, cited, rank, evidence)
                   VALUES (?,?,?,?,?,?,?)""",
                [(scan_id, answer_id, h.brand, int(h.mentioned), int(h.cited),
                  h.rank, h.evidence) for h in hits],
            )

    def finish_scan(self, scan_id: int, cost_usd: float) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE scans SET finished_at = ?, cost_usd = ? WHERE id = ?",
                (datetime.now(timezone.utc).isoformat(timespec="seconds"),
                 cost_usd, scan_id),
            )

    def previous_scan(self, slug: str, before_id: int) -> sqlite3.Row | None:
        """Most recent completed scan for ``slug`` before ``before_id``.

        Used to render movement arrows in the report; returns ``None`` on a
        first run, which the report must handle rather than showing 0%.
        """
        with self._connect() as conn:
            return conn.execute(
                """SELECT * FROM scans
                   WHERE slug = ? AND id < ? AND finished_at IS NOT NULL
                   ORDER BY id DESC LIMIT 1""",
                (slug, before_id),
            ).fetchone()

    def brand_totals(self, scan_id: int) -> dict[str, dict[str, int]]:
        """Per-brand mention/citation totals for a completed scan."""
        with self._connect() as conn:
            rows = conn.execute(
                """SELECT brand,
                          SUM(mentioned) AS mentions,
                          SUM(cited)     AS citations,
                          COUNT(*)       AS scored
                   FROM hits WHERE scan_id = ? GROUP BY brand""",
                (scan_id,),
            ).fetchall()
        return {
            r["brand"]: {"mentions": r["mentions"] or 0,
                         "citations": r["citations"] or 0,
                         "scored": r["scored"] or 0}
            for r in rows
        }

    def export_scan(self, scan_id: int) -> dict:
        """Full scan as JSON-safe dict — the deliverable clients can keep."""
        with self._connect() as conn:
            scan = conn.execute("SELECT * FROM scans WHERE id = ?", (scan_id,)).fetchone()
            if scan is None:
                raise KeyError(f"no scan {scan_id}")
            answers = conn.execute(
                "SELECT * FROM answers WHERE scan_id = ? ORDER BY id", (scan_id,)
            ).fetchall()
            hits = conn.execute(
                "SELECT * FROM hits WHERE scan_id = ? ORDER BY answer_id", (scan_id,)
            ).fetchall()

        by_answer: dict[int, list[dict]] = {}
        for h in hits:
            by_answer.setdefault(h["answer_id"], []).append(dict(h))

        return to_jsonable({
            "scan": dict(scan),
            "answers": [
                {**dict(a), "sources": json.loads(a["sources"]),
                 "hits": by_answer.get(a["id"], [])}
                for a in answers
            ],
        })
