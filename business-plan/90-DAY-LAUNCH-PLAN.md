# Shortlist — 90-Day Launch Plan

Everything below is either **[C]** — Claude does it, or **[H]** — the human principal must do it because it needs a legal person, a payment method, or a signature. The **[H]** column is the real schedule constraint; it totals roughly 4 hours a week.

---

## Week 1 — Entity, identity, and the scanner

**[H] (≈3 hrs, one time)**
- Entity is already in place — the Manitoba corporation. No formation step.
- Open a **US-domiciled USD account** (available to a Canadian-incorporated business on its existing registration documents) and connect it to Stripe as the settlement account. Doing this before the first invoice avoids ~1% on every dollar of revenue.
- Open the Stripe account; set USD as the presentment currency.
- Book the cross-border accountant: GST/HST registration timing, and the Form 1120-F / 8833 protective-return calendar.
- Register the primary domain + 8 sending domains from the list I supply.
- Create the mailbox accounts and Smartlead account.

**[C]**
- Build the **citation scanner**: takes a company domain and a category, generates 40 buyer-intent prompts, queries ChatGPT, Perplexity, Gemini, and Google AI Overviews via official APIs, and scores share-of-voice against three named competitors. This is the single most important asset in the business — it is simultaneously the lead magnet, the sales weapon, the delivery instrument, and the reporting layer.
- Build the marketing site: positioning, offer ladder, three-page structure, one live sample report. Deploy to a free tier.
- Draft the MSA, SOW template, privacy policy, and terms for counsel.
- Configure SPF, DKIM, and aligned DMARC on every sending domain.
- Build the **CASL country screen** into the list pipeline: US-only for cold sequences, country verified from company records rather than inferred from the domain, with the exemption basis logged per recipient. This is a hard gate in code, not a checklist item.

**Gate:** scanner produces a correct, reproducible report for three test companies; Stripe settles a $1 test charge into the USD account with no conversion.

---

## Week 2 — Proof before selling

**[C]**
- Build the target list: ~1,200 companies in the two beachhead categories, from public sources (G2 category pages, funding announcements, marketing-role job postings).
- Run scans across the list. Rank by *gap severity* — big gap, direct competitor dominant, evidence of existing marketing spend.
- Write the pilot outreach for the top 40.
- Start mailbox warmup. **No production sending until day 14 minimum** (Microsoft's domain-age floor), then ramp over 30 days.

**[H] (≈1 hr)**
- Send the pilot outreach to 40 hand-picked targets from the principal's own mailbox — not the cold infrastructure. Offer: a full diagnostic, free, in exchange for a case study and a testimonial if they like it.

**Gate:** 3 pilot clients accepted.

---

## Weeks 3–4 — Deliver the pilots, build the machine

**[C]**
- Deliver all three pilot diagnostics in full. These set the quality bar for every paid engagement — over-invest here deliberately.
- Build the **delivery pipeline**: scheduled nightly tracking jobs, automated report assembly, content production templates, client dashboard.
- Write the case studies as the pilots produce results.
- Draft the first 6 outreach sequences (one per persona × category).

**[H] (≈2 hrs)**
- Review the MSA and the CASL screening procedure with counsel. Sign off on outbound copy.
- Sign the W-8BEN-E; keep a PDF ready to send the moment a US client's accounts-payable team asks.
- Approve the first sending batch.

**Gate:** pipeline runs unattended for 7 days without intervention.

---

## Month 2 — Sell

**[C]**
- Scan-qualify and write outreach continuously. Ramp sending: 40/day week 5, 80/day week 6, 120/day week 7, 150/day week 8.
- Draft every reply, proposal, and SOW within an hour of a prospect responding — speed of response is a genuine competitive advantage here and costs nothing.
- Convert pilots to paid retainers at month-end.

**[H] (≈4 hrs/week)**
- Approve sends daily. Send proposals. Take calls where a prospect asks for one. Sign.

**Targets:** 880+ emails week 5–6, 2,000+ by week 8; **2 paid diagnostics closed**; 3 pilots converted or referenced.

---

## Month 3 — Prove the loop repeats

**[C]**
- Deliver every diagnostic and retainer on schedule.
- Publish **The B2B AI Citation Index, Q4 2026** — the aggregate findings from every scan run to date. This is the inbound engine and it markets the firm through the exact mechanism the firm sells.
- Expand the target list to ~4,000. Open a third category if the first two are converting.
- Instrument the four health metrics from `FINANCIAL-MODEL.md` §7 into a weekly dashboard.

**[H] (≈4 hrs/week)**
- Sales calls, signatures, invoicing. First price review.

**Targets:** 3,000 emails/month steady state; **3 diagnostics + 1–2 retainers closed**; exit month 3 at ~$3,200 MRR and ~$6,100 in month-3 revenue.

---

## Decision points

| When | Question | Action if the answer is no |
|---|---|---|
| End of week 2 | Did 3 pilots accept a *free* diagnostic? | The offer is not compelling. Rewrite it before spending on infrastructure — this is the cheapest possible failure. |
| End of month 2 | Reply rate ≥3%? Complaints <0.10%? | Rewrite sequences; re-examine list quality before increasing volume. |
| End of month 3 | ≥1 paying retainer and ≥$8,000 cumulative? | Change vertical. Keep the machine. |
| **End of month 4** | **≥2 retainers and ≥$8,000 cumulative?** | **Kill criteria. Stop selling and reassess.** |

---

## Standing weekly rhythm after day 90

| Day | Who | What |
|---|---|---|
| Monday | [C] | Weekly client tracking reports drafted; movement flagged |
| Monday | [H] | Approve and send; 30 min |
| Tue–Thu | [C] | Content production, outreach writing, prospect scans |
| Tue–Thu | [H] | Approve sends, handle replies, calls; ~2 hrs total |
| Friday | [C] | Health-metric dashboard, pipeline review, next week's queue |
| Friday | [H] | Review metrics, invoicing, banking; 45 min |
| Monthly | [C] | Client reports, one original research asset, price review input |
