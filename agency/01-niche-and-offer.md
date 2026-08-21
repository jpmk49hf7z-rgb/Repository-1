# Week 1 Deliverable 1 — Niche & Offer

**Status:** Decided | **Milestone:** "Niche and offer defined (Day 7)"

---

## 1. The niche

**Shopify DTC brands doing $2M–$20M/year in revenue, 5–50 employees, US-based, in high-support-volume repeat-purchase categories** — supplements, apparel, beauty/skincare, pet, and home goods.

Sub-$2M brands have no budget and the founder does everything manually. Above $20M they have an in-house ops/eng team and buy from larger agencies. The band in between is the whole market: enough revenue to pay a retainer, enough chaos to need one, no internal engineer to fix it.

## 2. The service

**Done-for-you operations automation.** We build and maintain the automated workflows that sit between their store, helpdesk, 3PL, email platform, and spreadsheets — the repetitive glue work their team currently does by hand.

We do not build custom software. We assemble and maintain integrations on a standardized stack, from a fixed menu of workflows that ~80% of brands in this niche need.

## 3. Why this niche, over the alternatives

| Factor | Ops automation (chosen) | Google Ads for med spas | SEO content for SaaS |
|---|---|---|---|
| Time to provable result | 2–4 weeks | 4–8 weeks | 4–6 months |
| Delivery is hireable | Yes — large contractor pool | Yes | Yes |
| Regulatory exposure | Low | High (medical board ad rules, before/after photo restrictions, health-data handling, platform healthcare ad policy) | Low |
| Price sensitivity | Low — compared against a salary | High — commoditized, many competitors | Medium |
| Retainer is genuinely recurring | Yes — integrations break when apps update | Yes | Yes |

The deciding factor is **time to proof**. This plan needs case studies by Day 75 to unlock Phase 3. An SEO retainer cannot produce a ranking case study in that window; an automation that deflects 40% of "where is my order" tickets is measurable in two weeks. Regulatory exposure is the tiebreaker against med spas — a two-person agency in month one should not be learning healthcare advertising compliance on a client's account.

## 4. Positioning statement

> We take the repetitive operations work off your team's plate. Every month we ship working automations, monitor the ones we've already built, and report the hours we gave you back.

One-liner for the website hero: **"Your Shopify store runs on copy-paste. We fix that."**

## 5. The productized menu

This is what makes the service productized rather than bespoke. Every engagement draws from this menu. The hire builds from templates, not from scratch.

1. **WISMO deflection** — order-status auto-reply in the helpdesk, pulling live Shopify + carrier tracking data
2. **Return/exchange intake** — customer request routed to 3PL RMA creation without manual re-entry
3. **Review request sequencing** — post-delivery, segmented by product, with sentiment gating
4. **Inventory alerts** — per-SKU reorder thresholds pushed to Slack before a stockout
5. **Failed-payment recovery** — dunning sequence for subscription and card-decline failures
6. **Daily ops digest** — yesterday's sales, refunds, top support tags, and fulfillment exceptions in one Slack message
7. **High-risk order review queue** — auto-flag and hold, instead of a chargeback three weeks later
8. **Wholesale/B2B inquiry routing** — form to CRM record to owner notification

New requests get evaluated against this menu first. Anything genuinely custom gets quoted separately or declined.

## 6. Standardized stack

Standardizing is non-negotiable — it is what lets the hire deliver without you, and what makes SOPs possible.

- **Orchestration:** Make.com (default). n8n self-hosted only when a client's operation volume makes Make's pricing painful.
- **Commerce:** Shopify Admin API + Shopify Flow
- **Helpdesk:** Gorgias (primary), Zendesk or Front (supported)
- **Email/SMS:** Klaviyo
- **Fulfillment:** ShipBob, ShipHero, or ShipStation
- **Data/reporting:** Airtable + Google Sheets
- **Comms:** Slack

A prospect on a stack we do not support is a prospect we decline, or migrate as paid onboarding work. This rule protects margin more than any pricing decision.

## 7. Pricing

**Retainer tiers, billed monthly in advance:**

| | **Starter** | **Growth** (target) | **Scale** |
|---|---|---|---|
| Price | $1,500/mo | $2,500/mo | $3,500/mo |
| New automations shipped | 1 / month | 2 / month | 4 / month |
| Workflows monitored | up to 5 | unlimited | unlimited |
| Fix response time | 2 business days | 1 business day | same business day |
| Check-in cadence | monthly report | biweekly call + report | weekly call + report |
| Channel | email | email | shared Slack channel |
| Quarterly ops audit | — | — | included |

**Onboarding fee:** $750 one-time — operations audit plus a written automation roadmap ranked by hours saved per month. Waived for pilot clients.

**Pilot offer (first 4 clients only):** $1,250/month for a 60-day initial term, then month-to-month at standard Growth pricing. In exchange the client agrees to a written case study, a testimonial, and two referral introductions. This is the honest trade — they take a risk on an unproven agency, they get a discount, we get the proof assets Phase 3 depends on. Cap it at four so the discount does not become the price.

**Delivery guarantee:** if we do not ship the first two automations within 30 days of receiving system access, that month is free. This is a guarantee about our output, which we control — not about their revenue, which we do not. Do not promise a revenue or ROI number to close a deal.

### Why these numbers hold up

The comparison a buyer actually makes is against labor, not against other agencies. A part-time ops coordinator costs $3,000–4,000/month fully loaded. Fifteen hours a week of support and ops busywork at $22/hour is roughly $1,400/month in wages — and that person still has to be hired, trained, and replaced. A $2,500 retainer that removes 25+ hours of monthly work, prevents stockouts, and never quits is a straightforward trade. Lead with the hours-saved number, never with an hourly rate.

### Margin floor

At Growth pricing, per client per month: roughly $150–250 in client-attributable tooling, and delivery labor that should stay under 8 hours once templates exist. If a client consistently costs more than 10 hours a month, the workflows are wrong or the client is out of niche — fix it or exit them at renewal. Fixed monthly overhead (the hire, agency tooling, outreach tools) is what the first three clients pay for; everything after that is margin available to reinvest.

## 8. Scope boundaries

**Included:** discovery and audit, workflow design, building and testing, documentation, monitoring and repair of anything we built, monthly reporting.

**Not included:** custom software development, ongoing manual data entry (we automate the work; we do not do it by hand), paid media management, store platform migrations, anything requiring a client staff member's personal login rather than a proper service account, and anything on a tool outside the supported stack.

Put these in writing before the first invoice. Nearly every retainer that goes bad in this business goes bad on scope, not on quality.

## 9. Client delivery timeline — first 30 days

| Days | What happens | Output |
|---|---|---|
| 0–3 | Kickoff call, access checklist, tool inventory | Signed access list, service accounts provisioned |
| 4–7 | Operations audit | Written roadmap, ranked by hours saved per month |
| 8–14 | Build automation #1, test, ship | Live workflow + documentation |
| 15–21 | Measure #1, build and ship automation #2 | Second live workflow |
| 22–30 | First monthly report | Hours saved, tickets deflected, errors caught |

**Define the hours-saved measurement during the audit, before anything is built.** Baseline the manual process — tickets per week, minutes per ticket — and record it. That baseline is what makes the Day-75 case study credible rather than a guess.

## 10. Success metric for the offer itself

The offer works if discovery calls close at 20%+ without discounting below the pilot rate, and if a Growth client takes under 10 hours a month to service after the first 60 days. If close rate is low, the problem is the prospect list or the positioning. If hours are high, the problem is scope discipline.

---

## Revenue math against the $100k goal

Assuming first revenue lands around Day 55 and a blended retainer of $2,300:

| Month | Active clients | Monthly revenue |
|---|---|---|
| 2 | 2 (pilot rate) | $2,500 |
| 3 | 4 | $6,000 |
| 4 | 6 | $12,000 |
| 5 | 8 | $18,400 |
| 6–12 | 8–10, net of churn | ~$20,000/mo |

That path lands well past $100k. The useful read is the downside: **roughly six retained clients by Day 90 is the real break-even against the goal**, not eight. The plan has slack. Spend it on client retention, not on lowering price to close faster.
