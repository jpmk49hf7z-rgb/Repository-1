# GoodNutrition aio — Financial Model

Companion to `BUSINESS-PLAN.md`. All figures are modelled, not observed. The purpose of this document is to make every assumption explicit enough to be attacked.

---

## 1. Funnel assumptions (base case)

| Stage | Rate | Source of the estimate |
|---|---|---|
| Emails sent / month at steady state | 3,000 | ~150/day across 10 mailboxes; within Google/Microsoft ramp limits |
| Reply rate | **4.0%** | Published 2026 benchmarks are 3.1–3.7% on managed infrastructure; we model a modest premium for a bespoke, evidence-carrying email, not the 8–12% "elite" figure |
| Positive replies (of all replies) | 25% | Conservative; most replies to any cold email are declines |
| Reply → real conversation | 60% | |
| Conversation → paid Diagnostic ($1,500) | 22% | |
| Diagnostic → retainer, within 45 days | 50% | |
| Direct-to-retainer closes (no diagnostic) | ~1/month | Larger prospects that skip the trial step |
| **Net new retainers / month at steady state** | **3.0** | |
| Blended retainer value | $3,200/mo | Mix weighted toward the $2,500 tier |
| **Monthly logo churn** | **5.0%** | Services churn; results lag 60–90 days, so early churn is the real risk |

At 3,000 emails → 120 replies → 30 positive → 18 conversations → 4 diagnostics → 2 retainer conversions + 1 direct = **3 net new retainers/month**.

---

## 2. Base case — month by month

MRR recursion: `MRR_end = MRR_prev × 0.95 + (new retainers × $3,200)`.
Retainer revenue billed is taken as the mid-month average, which approximates start dates spread through the month.

| Month | New retainers | Ending MRR | Active clients | Diagnostics sold | Retainer rev. | One-time rev. | **Total revenue** |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0 | $0 | 0 | 0 | $0 | $0 | **$0** |
| 2 | 0 | $0 | 0 | 2 | $0 | $3,000 | **$3,000** |
| 3 | 1 | $3,200 | 1 | 3 | $1,600 | $4,500 | **$6,100** |
| 4 | 2 | $9,440 | 3 | 4 | $6,320 | $6,000 | **$12,320** |
| 5 | 3 | $18,568 | 6 | 4 | $14,004 | $6,000 | **$20,004** |
| 6 | 3 | $27,240 | 9 | 4 | $22,904 | $6,000 | **$28,904** |
| 7 | 3 | $35,478 | 11 | 4 | $31,359 | $6,000 | **$37,359** |
| 8 | 3 | $43,304 | 14 | 4 | $39,391 | $6,000 | **$45,391** |
| 9 | 3 | $50,739 | 16 | 4 | $47,022 | $6,000 | **$53,022** |
| 10 | 3 | $57,802 | 18 | 4 | $54,271 | $6,000 | **$60,271** |
| 11 | 3 | $64,512 | 20 | 4 | $61,157 | $6,000 | **$67,157** |
| 12 | 3 | **$70,886** | **22** | 4 | $67,699 | $6,000 | **$73,699** |
| | | | | **41** | **$345,727** | **$61,500** | **$407,227** |

Less a 5% allowance for refunds, prorations, and negotiated discounts:

> ### Year-1 recognized revenue: **~$387,000**
> ### Exit MRR: **$70,886** → **~$851,000 ARR run-rate**

---

## 3. Base case — cost side

| Line | Basis |
|---|---|
| Outbound infrastructure | ~$124/mo — 10 mailboxes ($25), Smartlead ($39), domains amortized ($10), lead enrichment ($50) |
| Prospect scanning | $200–300/mo — ~500 qualifying scans at ~$0.40 each |
| Client delivery (LLM + search APIs) | ~$120/client/mo |
| Client-facing dashboard subscription | $160/mo from month 4, $320/mo from month 8 (we buy the commodity tool rather than build it) |
| Accounting / admin | $100/mo from month 6 |
| Entity formation and registered agent | $150, month 1 |

| | Amount |
|---|---|
| Total operating cost, year 1 | ~$21,800 |
| Stripe processing (2.9% + $0.30) | ~$11,800 |
| Stripe FX conversion — **$0 if settling to a US-domiciled USD account**, ~$3,900 if not | $0 |
| **Total cost** | **~$33,600** |
| **Pre-tax profit, year 1** | **~$353,000** |
| Corporate tax — Manitoba CCPC, 9% combined on active business income under $500k | ~$31,800 |
| **After-tax profit retained in the corporation** | **~$321,000** |

Revenue is invoiced in USD; the figures throughout this model are USD. Costs are also largely USD (APIs, sending tools, domains), so the currency exposure is limited to retained earnings. Settle Stripe into a US-domiciled USD account from the first invoice — otherwise automatic conversion takes roughly 1%, about $3,900 a year at base case.

The business is cash-positive from month 2 and never requires capital beyond the initial $1,000. This is the defining structural advantage: **there is no month in which growth is constrained by money.** It is constrained by delivery capacity and by close rate.

---

## 4. Scenarios

| | Conservative | **Base** | Aggressive |
|---|---|---|---|
| Reply rate | 3.0% | 4.0% | 5.0% |
| Net new retainers / mo (steady) | 1.5 | 3.0 | 4.0 |
| Blended retainer | $2,800 | $3,200 | $4,500 |
| Monthly churn | 6% | 5% | 4% |
| First retainer lands | Month 4 | Month 3 | Month 3 |
| Diagnostics / mo | 2 | 4 | 5 |
| **Exit MRR** | **~$29,000** | **~$70,900** | **~$115,400** |
| **Exit ARR run-rate** | ~$348,000 | ~$851,000 | ~$1,385,000 |
| **Year-1 revenue** | **~$159,000** | **~$387,000** | **~$698,000** |
| Active clients at month 12 | 10 | 22 | 26 |

The aggressive case is **capacity-capped from month 10** (new adds cut from 4/mo to 2/mo). Uncapped it produces a higher number, but 30+ concurrent clients is not deliverable at the quality this business sells. Past that point the correct move is a price increase, not another logo.

---

## 5. Sensitivity — what actually moves the outcome

Year-1 revenue, varying one assumption at a time from the base case:

| Change | Year-1 revenue | Δ |
|---|---|---|
| Reply rate 4.0% → 3.0% | ~$300,000 | −22% |
| Reply rate 4.0% → 5.0% | ~$470,000 | +21% |
| Churn 5% → 8%/mo | ~$333,000 | −14% |
| Churn 5% → 3%/mo | ~$425,000 | +10% |
| Blended retainer $3,200 → $4,000 | ~$450,000 | +16% |
| First retainer slips month 3 → month 5 | ~$310,000 | −20% |

**Two conclusions.** First, *speed to first client matters as much as conversion rate* — a two-month slip costs as much as a full point of reply rate. Front-load the pilots. Second, **price is the cheapest lever available**: raising the blended retainer 25% costs nothing, consumes no capacity, and adds more than cutting churn by 40% does. Raise prices at months 6 and 10.

---

## 6. Reinvestment policy

| Period | Rule |
|---|---|
| Months 1–6 | 100% of profit to sending capacity, then API credits. Outreach volume is the growth constraint. |
| Months 7–9 | Cap outbound spend at ~$600/mo. Route surplus into original research studies (inbound engine) and a refund reserve equal to one month of MRR. |
| Months 10–12 | Hold a 3-month operating reserve. Distributions permitted above that. Consider a part-time human editor if quality metrics slip. |

**A note on distributions.** The 9% Manitoba CCPC rate is a *deferral*, not forgiveness — personal tax applies when profits leave the company as salary or dividends. Retaining earnings inside the corporation through year 1 is therefore worth real money, and the reinvestment schedule above already does that. Salary-versus-dividend mix is an accountant question to settle before the first distribution.

---

## 7. What would falsify this model

Watch these four numbers monthly. Each has a threshold that should trigger a change in plan, not a change in effort.

| Metric | Healthy | Trigger |
|---|---|---|
| Reply rate | ≥3% | <2% for two consecutive months → rewrite offer or change vertical |
| Spam complaint rate | <0.10% | >0.10% → stop sending, rebuild infrastructure |
| Diagnostic → retainer | ≥40% | <25% → the diagnostic is not proving value; rebuild the deliverable |
| 90-day client retention | ≥80% | <60% → the program does not work; fix delivery before selling more |

**Kill criteria: fewer than 2 paying retainers and under $8,000 cumulative revenue at the end of month 4.** Reassess the vertical first — the machine repoints in about two weeks.
