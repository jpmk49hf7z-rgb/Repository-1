"""Render a scan into the client-facing HTML report.

This file is the product's front door. The free version of this report is the
cold-email hook, and the paid Diagnostic is a deeper version of the same
document, so it has to survive being forwarded to a CMO who has never heard
of us.

Two editorial decisions are baked in:

* **Mention rate and citation rate are shown separately.** Engines routinely
  name a vendor without linking to it. Collapsing the two into one "visibility"
  number would be the industry-standard thing to do and would be wrong.
* **The comparison is always named.** "You are at 3%" is abstract. "You are at
  3% and Jobber is at 68%" is the finding that gets a reply.
"""
from __future__ import annotations

import html
from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Environment, select_autoescape

from .models import Answer, BrandHit
from .prompts import CategorySpec
from .scoring import ScanScore

TEMPLATE = """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI Visibility Report — {{ spec.client_name }}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>
:root{--paper:#F6F7FA;--surface:#FFF;--surface-2:#EEF1F6;--ink:#15181E;--ink-mid:#3E4552;
--ink-soft:#6B7383;--rule:#DCE0E9;--rule-strong:#BFC6D4;--signal:#A25E05;--signal-ink:#7A4704;
--signal-wash:#F6E9D4;--crit:#9E2A2E;--good:#1D6B4C}
@media(prefers-color-scheme:dark){:root{--paper:#0E1116;--surface:#161A21;--surface-2:#1D222B;
--ink:#E9EBF0;--ink-mid:#B6BCC9;--ink-soft:#8A92A1;--rule:#262C36;--rule-strong:#39414E;
--signal:#E5A144;--signal-ink:#F0BE7C;--signal-wash:#2E2413;--crit:#E0797C;--good:#5CBF92}}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-family:"IBM Plex Sans",system-ui,sans-serif;
font-size:16px;line-height:1.6}
.wrap{max-width:940px;margin:0 auto;padding:0 clamp(18px,4vw,36px)}
header{border-bottom:1px solid var(--rule);background:var(--surface)}
.mast{display:flex;flex-wrap:wrap;gap:10px 20px;align-items:baseline;padding:18px 0}
.wordmark{font-family:"Newsreader",Georgia,serif;font-size:22px;font-weight:600;margin:0}
.meta{margin-left:auto;font-family:"IBM Plex Mono",monospace;font-size:11px;letter-spacing:.06em;
text-transform:uppercase;color:var(--ink-soft);display:flex;gap:16px;flex-wrap:wrap}
h1{font-family:"Newsreader",Georgia,serif;font-weight:500;font-size:clamp(1.9rem,4.4vw,2.9rem);
line-height:1.12;letter-spacing:-.02em;margin:0 0 18px;max-width:20ch;text-wrap:balance}
h1 em{font-style:italic;color:var(--signal)}
.hero{padding:44px 0 38px;border-bottom:1px solid var(--rule)}
.eyebrow{font-family:"IBM Plex Mono",monospace;font-size:11px;letter-spacing:.13em;
text-transform:uppercase;color:var(--signal);margin:0 0 16px}
.lede{font-size:1.08rem;color:var(--ink-mid);max-width:62ch;margin:0}
.lede strong{color:var(--ink)}
section{padding:34px 0;border-bottom:1px solid var(--rule)}
section:last-of-type{border-bottom:0}
h2{font-family:"Newsreader",Georgia,serif;font-weight:600;font-size:1.5rem;margin:0 0 6px;
letter-spacing:-.012em}
.dek{color:var(--ink-soft);font-size:.95rem;margin:0 0 22px;max-width:60ch}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:1px;
background:var(--rule);border:1px solid var(--rule);margin:0 0 26px}
.stat{background:var(--surface);padding:16px 18px}
.stat .n{font-family:"IBM Plex Mono",monospace;font-size:1.55rem;color:var(--signal);
line-height:1.05;font-variant-numeric:tabular-nums;display:block}
.stat .n.bad{color:var(--crit)}
.stat .l{font-size:12px;color:var(--ink-soft);margin-top:6px;display:block;line-height:1.4}
.sov{background:var(--surface);border:1px solid var(--rule);padding:20px 22px}
.row{display:grid;grid-template-columns:minmax(90px,150px) 1fr minmax(96px,auto);
align-items:center;gap:14px;margin-bottom:11px}
.row:last-child{margin-bottom:0}
.nm{font-size:13.5px;color:var(--ink-mid);font-weight:500;overflow:hidden;text-overflow:ellipsis}
.nm.you{color:var(--signal-ink);font-weight:600}
.track{height:10px;background:var(--surface-2);position:relative;overflow:hidden}
.fill{position:absolute;inset:0 auto 0 0;background:var(--rule-strong)}
.fill.you{background:var(--signal)}
.val{font-family:"IBM Plex Mono",monospace;font-size:12px;font-variant-numeric:tabular-nums;
color:var(--ink-mid);text-align:right}
.scroll{overflow-x:auto;border:1px solid var(--rule);background:var(--surface);margin:0 0 20px}
table{border-collapse:collapse;width:100%;min-width:540px;font-size:13.5px}
th,td{padding:9px 14px;text-align:left;border-bottom:1px solid var(--rule);vertical-align:top}
thead th{font-family:"IBM Plex Mono",monospace;font-size:10.5px;letter-spacing:.07em;
text-transform:uppercase;color:var(--ink-soft);background:var(--surface-2);white-space:nowrap}
tbody tr:last-child td{border-bottom:0}
td.num,th.num{text-align:right;font-family:"IBM Plex Mono",monospace;
font-variant-numeric:tabular-nums;white-space:nowrap}
tr.you td{background:var(--signal-wash);color:var(--signal-ink)}
.yes{color:var(--good);font-weight:600}.no{color:var(--ink-soft)}
.ev{font-family:"IBM Plex Mono",monospace;font-size:11.5px;color:var(--ink-soft);line-height:1.5}
.note{background:var(--surface);border:1px solid var(--rule);border-left:3px solid var(--signal);
padding:17px 20px;margin:0 0 20px}
.note p{margin:0;max-width:62ch}.note p+p{margin-top:10px}
.note .tag{font-family:"IBM Plex Mono",monospace;font-size:10.5px;letter-spacing:.11em;
text-transform:uppercase;color:var(--signal);display:block;margin-bottom:8px}
footer{background:var(--surface);border-top:1px solid var(--rule);padding:26px 0 40px}
footer p{font-size:12.5px;color:var(--ink-soft);max-width:70ch;margin:0 0 9px}
</style></head><body>

<header><div class="wrap"><div class="mast">
  <p class="wordmark">AI Visibility Report</p>
  <div class="meta">
    <span>{{ spec.client_name }}</span><span>{{ generated }}</span>
    <span>{{ score.answers_scored }} answers</span>
  </div>
</div></div></header>

<div class="wrap">
<div class="hero">
  <p class="eyebrow">{{ spec.category }} · {{ spec.audience }}</p>
  {% if client and client.mentions == 0 %}
    <h1>{{ spec.client_name }} was named in <em>none</em> of the {{ score.answers_scored }} buyer answers we sampled.</h1>
  {% else %}
    <h1>{{ spec.client_name }} holds <em>{{ '%.1f'|format(sov*100) }}%</em> of the answer share in its category.</h1>
  {% endif %}
  <p class="lede">
    We asked {{ prompt_count }} questions a buyer asks before choosing {{ spec.category }},
    across {{ engines|length }} answer engine{{ 's' if engines|length != 1 }}
    ({{ engines|join(', ') }}), producing {{ score.answers_scored }} answers.
    {% if leader and client and leader.brand != client.brand %}
      <strong>{{ leader.brand }}</strong> was named in
      <strong>{{ leader.mentions }}</strong> of them; {{ spec.client_name }} in
      <strong>{{ client.mentions }}</strong>.
    {% endif %}
  </p>
</div>

<section>
  <h2>Where you stand</h2>
  <p class="dek">Share of voice weights the questions that actually form shortlists — discovery and alternatives — above narrower ones.</p>
  <div class="stats">
    <div class="stat"><span class="n {{ 'bad' if client and client.mention_rate < 0.1 }}">{{ '%.0f'|format((client.mention_rate if client else 0)*100) }}%</span><span class="l">Mention rate — how often you are named</span></div>
    <div class="stat"><span class="n {{ 'bad' if client and client.citation_rate < 0.05 }}">{{ '%.0f'|format((client.citation_rate if client else 0)*100) }}%</span><span class="l">Citation rate — how often you are linked</span></div>
    <div class="stat"><span class="n">{{ '%.1f'|format(sov*100) }}%</span><span class="l">Share of voice vs tracked set</span></div>
    <div class="stat"><span class="n">{{ client.average_rank if client and client.average_rank else '—' }}</span><span class="l">Average position when named</span></div>
  </div>

  <div class="sov">
    {% for b in ranked %}
    <div class="row">
      <span class="nm {{ 'you' if b.is_client }}">{{ b.brand }}{{ ' (you)' if b.is_client }}</span>
      <span class="track"><span class="fill {{ 'you' if b.is_client }}" style="width:{{ '%.1f'|format(b.mentions / max_mentions * 100 if max_mentions else 0) }}%"></span></span>
      <span class="val">{{ b.mentions }} / {{ b.answers_scored }}</span>
    </div>
    {% endfor %}
  </div>
</section>

<section>
  <h2>Mentioned is not the same as cited</h2>
  <p class="dek">A mention puts you on the shortlist. A citation sends you traffic. Most vendors have a gap between the two, and the size of that gap tells you which problem you have.</p>
  <div class="scroll"><table>
    <thead><tr><th>Brand</th><th class="num">Mentions</th><th class="num">Mention rate</th><th class="num">Citations</th><th class="num">Citation rate</th><th class="num">First place</th></tr></thead>
    <tbody>
    {% for b in ranked %}
      <tr class="{{ 'you' if b.is_client }}">
        <td>{{ b.brand }}{{ ' (you)' if b.is_client }}</td>
        <td class="num">{{ b.mentions }}</td>
        <td class="num">{{ '%.0f'|format(b.mention_rate*100) }}%</td>
        <td class="num">{{ b.citations }}</td>
        <td class="num">{{ '%.0f'|format(b.citation_rate*100) }}%</td>
        <td class="num">{{ b.first_place_count }}</td>
      </tr>
    {% endfor %}
    </tbody>
  </table></div>
</section>

{% if engines|length > 1 %}
<section>
  <h2>The engines disagree</h2>
  <p class="dek">Only about a tenth of cited domains overlap between engines. Being invisible on one and healthy on another is normal — and it means a single-engine check would have told you the wrong thing.</p>
  <div class="scroll"><table>
    <thead><tr><th>Brand</th>{% for e in engines %}<th class="num">{{ e }}</th>{% endfor %}</tr></thead>
    <tbody>
    {% for b in ranked %}
      <tr class="{{ 'you' if b.is_client }}">
        <td>{{ b.brand }}{{ ' (you)' if b.is_client }}</td>
        {% for e in engines %}
          {% set cell = b.by_engine.get(e) %}
          <td class="num">{{ cell.mentions if cell else 0 }} / {{ cell.scored if cell else 0 }}</td>
        {% endfor %}
      </tr>
    {% endfor %}
    </tbody>
  </table></div>
</section>
{% endif %}

<section>
  <h2>Question by question</h2>
  <p class="dek">Every question we asked, and whether you appeared in the answer. Transcripts and sources are in the accompanying JSON export.</p>
  <div class="scroll"><table>
    <thead><tr><th>Question</th><th>Intent</th><th>Engine</th><th class="num">You</th><th>Who was named first</th></tr></thead>
    <tbody>
    {% for row in prompt_rows %}
      <tr>
        <td>{{ row.prompt }}</td>
        <td class="no">{{ row.intent }}</td>
        <td class="no">{{ row.engine }}</td>
        <td class="num">{% if row.client_present %}<span class="yes">yes</span>{% else %}<span class="no">no</span>{% endif %}</td>
        <td class="{{ 'no' if not row.first_brand }}">{{ row.first_brand or '—' }}</td>
      </tr>
    {% endfor %}
    </tbody>
  </table></div>
</section>

{% if client and client.mentions == 0 %}
<section>
  <div class="note">
    <span class="tag">What this means</span>
    <p>A zero is not a ranking penalty and it is not permanent. Engines name vendors they can find corroborated across the open web — third-party coverage, comparison pages, structured listings, original data worth citing. Roughly three quarters of what drives a citation sits on domains you do not own.</p>
    <p>That is fixable work, and it is the work we do.</p>
  </div>
</section>
{% endif %}
</div>

<footer><div class="wrap">
  <p><strong>Method.</strong> {{ prompt_count }} buyer-intent questions generated from the category, audience, use cases, and buying criteria for {{ spec.category }}. Each question was put to {{ engines|join(', ') }} via official APIs — no scraping. Brand detection uses word-boundary matching with corroboration required for brand names that are ordinary English words. Failed calls are excluded from all denominators rather than counted as absence.</p>
  <p><strong>Limits.</strong> Answer engines are non-deterministic; a repeat run will differ at the margin. Treat a single scan as a snapshot and the trend across scans as the signal. Sampled {{ generated }}{% if score.answers_failed %} · {{ score.answers_failed }} call(s) failed and were excluded{% endif %}.</p>
</div></footer>
</body></html>
"""


def _prompt_rows(
    results: list[tuple[Answer, list[BrandHit]]], client_name: str
) -> list[dict]:
    rows = []
    for answer, hits in results:
        if not answer.ok:
            continue
        ranked = sorted(
            (h for h in hits if h.rank is not None),
            key=lambda h: h.rank,  # type: ignore[arg-type,return-value]
        )
        client_hit = next((h for h in hits if h.brand == client_name), None)
        rows.append(
            {
                "prompt": answer.prompt_text,
                "intent": answer.intent.value.replace("_", " "),
                "engine": answer.engine,
                "client_present": bool(client_hit and client_hit.present),
                "first_brand": ranked[0].brand if ranked else None,
            }
        )
    return sorted(rows, key=lambda r: (r["intent"], r["prompt"], r["engine"]))


def render_report(
    *,
    spec: CategorySpec,
    score: ScanScore,
    results: list[tuple[Answer, list[BrandHit]]],
    prompt_count: int,
    out_path: str | Path,
) -> Path:
    """Write the HTML report and return its path."""
    env = Environment(autoescape=select_autoescape(["html"]))
    template = env.from_string(TEMPLATE)

    ranked = score.ranked()
    client = score.client
    leader = score.leader

    rendered = template.render(
        spec=spec,
        score=score,
        ranked=ranked,
        client=client,
        leader=leader,
        sov=score.share_of_voice(client.brand) if client else 0.0,
        max_mentions=max((b.mentions for b in ranked), default=0),
        engines=score.engines,
        prompt_count=prompt_count,
        prompt_rows=_prompt_rows(results, client.brand if client else ""),
        generated=datetime.now(timezone.utc).strftime("%d %b %Y"),
    )

    path = Path(out_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(rendered, encoding="utf-8")
    return path
