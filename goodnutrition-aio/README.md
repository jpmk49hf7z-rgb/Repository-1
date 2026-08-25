# GoodNutrition aio — citation scanner

Measures how often answer engines name a company when a buyer asks for the
best tool in its category, and how that compares with its competitors.

This is the instrument the whole business runs on. It is the free report that
opens a cold email, the deliverable inside a paid Diagnostic, the monthly
tracking a retainer client pays for, and the source of the aggregate dataset
behind the published Citation Index. Everything else is downstream of it
being correct.

## Quick start

```bash
pip install -r requirements.txt
cp .env.example .env            # add at least one API key
cp config/settings.example.yaml config/settings.yaml

# Offline dry run — no keys, no spend, deterministic output
PYTHONPATH=src python -m aio scan config/categories/field-service-hvac.yaml \
  --engines mock

# Live scan
PYTHONPATH=src python -m aio scan config/categories/field-service-hvac.yaml \
  --engines claude,chatgpt,perplexity
```

Outputs an HTML report and a JSON export in `reports/`, and persists the full
scan to SQLite in `data/`.

Preview the question set without spending anything:

```bash
PYTHONPATH=src python -m aio prompts config/categories/field-service-hvac.yaml
```

## Adding a prospect

Copy `config/categories/field-service-hvac.yaml`, change the client and
competitors, and run a scan. The config is the unit of work — one file per
prospect or client. Prompt generation is deterministic from it, so scans a
month apart are directly comparable.

Only two things need care:

- **Competitors.** Pick the names a buyer would actually shortlist, not the
  whole market. Share of voice is measured against this set, so padding it
  with irrelevant vendors makes the client's number look worse than it is.
- **`ambiguous: true`.** Set this when a brand name is also an ordinary
  English word — Notion, Monday, Ramp, Front. The detector then demands
  corroboration before counting a match. Common names are auto-flagged, but
  the list is not exhaustive.

## What it measures, and why three numbers

| Metric | Question it answers |
|---|---|
| **Mention rate** | How often is the brand named at all? Drives shortlist inclusion. |
| **Citation rate** | How often is the brand's own domain linked? Drives referral traffic. |
| **Share of voice** | What fraction of all tracked-brand mentions belong to it? The competitive number. |

Mention and citation are kept separate on purpose. Engines routinely name a
vendor without linking to it, and the two failures need different fixes.
Share of voice is weighted by buyer intent: discovery and alternatives
questions count for more than narrow feature questions, because that is where
shortlists actually form.

## Design notes

**Failed calls are excluded from every denominator.** An engine timing out is
not evidence that a brand is absent. Folding failures in would understate a
prospect's position, and the one thing this report cannot afford is to be
wrong in the alarming direction during a sales call.

**Detection requires corroboration for ambiguous names.** Substring matching
reports "Ramp" inside "Rampart" and "monday" in "on monday we ship". Both
inflate a prospect's apparent visibility. See `src/aio/mentions.py` and
its tests.

**Model ids and token rates are configuration, not constants.** Providers
rename models and change prices more often than we change logic; that should
be a settings edit.

**Every scan is persisted in full.** Week-over-week movement is the product,
and a trend line needs history captured before anyone knew which way it went.

## Tests

```bash
python -m unittest discover -s tests -v
```

37 tests, no external dependencies, no network. The mock engine makes the
whole pipeline testable offline.

## Status

Working end to end against the mock engine. The Claude adapter is written
against the documented API surface; the ChatGPT and Perplexity adapters need
one verification pass against live keys, since both providers have moved
their response shapes recently. Model ids in `settings.example.yaml` should be
checked against each provider's current model list before the first paid run.
