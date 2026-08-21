# Week 1 Deliverable 3 — Delivery Model

**Status:** Complete | Defines how the offer in `01-niche-and-offer.md` actually gets produced

---

This file exists because the delivery capacity is an AI assistant, and an offer whose delivery model is vague is an offer that quietly turns into your problem at 11pm. Everything below is a constraint, not a preference.

## 1. How a month runs

| Week | Work | Your time |
|---|---|---|
| 1 | Research block: competitor sweep, keyword-to-page assignment, page briefs for the month | ~1 hr — approve the page list |
| 2 | Production block: batch one built | ~1.5 hrs — review and publish |
| 3 | Production block: batch two built | ~1.5 hrs — review and publish |
| 4 | Reporting, refreshes, next month's page map | ~1 hr — send reports |

Work happens in **sessions you start**. I do not run between them, so nothing is produced on a week you skip. Two scheduled production blocks a week is the cadence that makes the volume commitments in §8 of the offer real. If a week gets eaten by sales calls, the batch moves — it does not disappear, and it does not silently become a smaller batch the client wasn't told about.

## 2. The source pack

The single largest determinant of whether pages are good or generic. Collected during onboarding, before any page is written, and named as a client responsibility in the agreement.

**Required:**
- Product documentation and a walkthrough of what the product actually does
- Current pricing, including what's on each tier
- Positioning: who it's for, who it's not for, what it replaces
- The competitors that come up in sales calls, and how they lose to each one
- Two or three recorded sales calls or demo transcripts — the highest-value item on this list, because it contains the buyer's real language

**Strongly wanted:** existing customer quotes and case studies, win/loss notes, the objections that kill deals, and anything their sales team already sends prospects.

Without this, pages come out plausible and hollow — the failure mode that makes a prospect think "I could have gotten this from ChatGPT," because they could have. A thin source pack is a contract problem to raise with the client, never a gap to paper over with confident writing.

**I will not invent claims about a client's product.** If a page needs a number, an integration detail, or a competitor's current pricing that isn't in the source pack or verifiable publicly, it gets flagged for the client to fill in rather than guessed. Expect a handful of these per batch — that's the system working.

## 3. The review gate

**Nothing reaches a client's live site without a human reading it first.** This is the one rule with no exceptions, and it is yours.

Budget ~15 minutes per page. What you're checking:

1. **Factual claims about their product** — the only thing you're better positioned than me to catch
2. **Competitor claims** — is every statement about a competitor currently true and fair? Pricing changes; check it.
3. **Does it sound like them** — voice drift across a batch is the tell that gives AI production away
4. **Would a buyer find this useful** — if it reads like it exists to rank, it does, and Google agrees
5. **Links, and the CTA actually working**

At six clients averaging 12 pages, that's about 18 hours a month. That is the real cost of this business and it belongs in your calendar as a standing block, not in the gaps. If it ever feels skippable, remember what publishing a false claim about a named competitor on a client's live site costs — that's the risk this gate is priced against.

## 4. Publishing

I don't hold client credentials. Three models, in order of preference:

1. **Git-based sites** (Next.js, Astro, Docusaurus, Hugo) — pages delivered as a pull request. The client reviews a diff and merges. Cleanest possible fit: reviewable, revertible, no credentials, and their normal workflow. **Prefer prospects on this setup.**
2. **You publish** — the seller holds the credential and builds the page in their CMS. Roughly 20 minutes a page and it doubles as the review gate. Fine at this scale; it's the model most clients will land on.
3. **Client publishes** — we deliver built pages plus assets and instructions, they push them live. Lowest access burden, slowest, and their delay becomes your missed deadline. Adjust the guarantee clock accordingly.

Never take standing admin access to a client's production site. It converts a content retainer into a systems-liability retainer, and it's the same mistake as the ops-automation offer.

## 5. AI disclosure

**Position: we do not volunteer our production process, we never deny it, and we answer honestly when asked.**

That's the same standard as any agency's use of contractors and tooling. The offer is a researched, reviewed, published program of pages with a human accountable for every one — which is true, and is what they're buying.

Three hard rules:

- **Never claim pages are written without AI assistance.** It's a lie a single prospect can disprove, and the churn it causes arrives with a story attached.
- **Honor contractual restrictions.** Some enterprise clients prohibit AI-generated content or require disclosure. Read their vendor terms. If they prohibit it, decline the client — do not sign and hope.
- **Never let a client publish under a named human byline someone didn't write.** Publish under the company, or under a byline the client's own person actually reviews and stands behind. Fabricating a person is where this stops being defensible.

If disclosure loses a deal, it was a deal that would have blown up later at a worse time.

## 6. Volume has a ceiling, on purpose

Google's spam policies target **scaled content abuse** — producing pages at volume primarily to manipulate rankings rather than to help someone. AI authorship itself isn't the trigger; volume without substance is. Since near-zero marginal cost makes "just ship 400 pages" technically easy, the guardrails are deliberate:

- **Tiers cap at 20 pages a month.** Not a capacity limit — a quality limit.
- **Every page targets a real query with a distinct answer.** No spinning one template across 200 city names with the noun swapped.
- **Every page carries genuine research** the client couldn't get from a generic prompt.
- **Human review before publish**, per §3.

Refuse the client who wants 500 programmatic pages next month. Torching a client's domain is not recoverable, and it will be traced back to us.

## 7. Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| Pages read generic | Thin source pack | Escalate to the client; get sales call recordings. Don't compensate with better prose. |
| Voice drifts across a batch | No style reference | Build a voice guide from their best existing page during onboarding; use it as the reference every batch. |
| Review time creeping past 15 min/page | Briefs too loose, or the source pack degraded | Fix the brief stage. Never fix it by reviewing less. |
| Client asks for something off-menu | Scope creep, month two, every time | `01-niche-and-offer.md` §10. Quote it separately or decline. |
| Batch slipped because the week vanished | No standing production block | Calendar it. The guarantee in the agreement is a real commitment. |
| Client wants a competitor page that misrepresents the competitor | Their sales team wrote the brief | Refuse the framing, offer the honest version, explain why it converts better. |

## 8. What this model does not do

State these on sales calls before the client discovers them:

- No same-day turnaround. Work is batched.
- No monitoring, no on-call, no emergency response.
- No standing access to their systems.
- No management of their existing content, CMS, or hosting.
- No claims we can't source.

Every one of these is a reason to decline a prospect rather than a gap to stretch to cover. The offer is narrow because narrow is what makes it deliverable — a client who needs something on this list is a good client for a different agency.
