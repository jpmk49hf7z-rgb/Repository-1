# Shortlist — Compliance & Ethics Policy

**Status: draft for review by counsel.** This document states the operating rules the business binds itself to. It is written to be reviewed as a standalone instrument and to be referenced by the MSA.

Nothing here is legal advice. Items marked **[COUNSEL]** are specific questions for the reviewing attorney.

---

## 1. Entity and contracting

Single-member LLC. The principal is the sole member, sole signatory, and the account holder for all financial and platform accounts. All work is performed by the principal using AI systems under the principal's direction and review.

**[COUNSEL]** Formation state — home state versus Wyoming, weighing banking and tax simplicity against Wyoming's lower fees ($100 filing / $60 annual, versus Delaware's $110 / $300 franchise tax).
**[COUNSEL]** Whether professional liability (E&O) coverage is warranted before the first paid engagement, and at what client count.

### Contract terms to be reflected in the MSA

1. **Deliverables are activities, not outcomes.** The agreement commits to defined work product — tracked prompt sets, a stated number of content assets, reporting cadence, outreach volume. It must **not** guarantee citation rates, ranking, traffic, or revenue. We do not control the ranking systems of third parties and will not represent that we do.
2. **AI-assisted delivery is disclosed.** The MSA states plainly that work product is produced with AI assistance under human review. Clients are told before they sign, not after they ask.
3. **IP assignment.** All content delivered to the client is assigned to the client on payment. Our scanner, methodology, prompt libraries, and aggregate dataset remain ours.
4. **Aggregate data rights.** We reserve the right to use anonymized, aggregated measurement data in published research. No client is named or identifiable without written consent.
5. **Term.** 3-month initial term, then month-to-month with 30 days' notice.
6. **Limitation of liability** capped at fees paid in the preceding 3 months.

**[COUNSEL]** Confirm items 1 and 4 are drafted tightly enough — outcome-guarantee exposure and client-data reuse are the two most likely sources of dispute in this business.

---

## 2. Advertising, endorsements, and the hard lines

The FTC's **Rule on the Use of Consumer Reviews and Testimonials** (16 CFR Part 465, effective 21 October 2024) authorizes civil penalties of up to approximately **$52,000 per violation**, and reaches conduct that a party **"knew or should have known"** about. Because our service produces third-party visibility, this rule sits directly on top of our core deliverable.

### Prohibited without exception — for the firm and on behalf of any client

| We never | Why |
|---|---|
| Write, buy, sell, or broker consumer reviews or testimonials — including AI-generated ones | Core prohibition of the Rule |
| Compensate or incentivize anyone to leave a review expressing a particular sentiment | Prohibited whether the sentiment is positive or negative |
| Post to forums, Reddit, review sites, or social platforms as a client, or operate sockpuppet or unattributed accounts | Deceptive; also breaches platform terms |
| Create or operate a site presenting itself as an independent review or comparison source while controlled by us or a client | Explicitly prohibited misrepresentation |
| Suppress, hide, or selectively surface negative reviews | Explicitly prohibited |
| Publish testimonials from insiders without clear and conspicuous disclosure of the relationship | Disclosure requirement |
| Fabricate statistics, studies, or survey results in original research | Deceptive advertising, and fatal to the firm's credibility |

### What we do instead

- **Earned mentions only.** Genuinely useful content, published under the client's own name, pitched to publications on its merits.
- **Community participation is done by named client employees with disclosed affiliation.** We may draft; we never post, and we never post anonymously. This is written into every SOW that touches community channels.
- **Original research is real research.** Methodology published, sample sizes stated, raw data available on request.
- **Third-party profile work is factual accuracy work** — correcting and completing the client's own listings on directories, review platforms, and structured-data sources.

This is stricter than the market norm in this category, and deliberately so. Astroturfing is the obvious shortcut in AI-visibility work; it is the reason the category will eventually draw enforcement; and a firm that publishes its methodology and refuses to fake anything is differentiated precisely where buyers will start looking.

**[COUNSEL]** Review the boundary between (a) drafting content published under a client employee's name with disclosure, and (b) endorsement rules. Confirm our disclosure language is adequate.

---

## 3. Outbound email

### United States — CAN-SPAM

- Accurate "From", "Reply-To", and routing information.
- Subject lines that reflect the message honestly.
- A valid physical postal address in every message.
- A clear opt-out mechanism, honored within **10 business days**; suppression list checked before every send.

### European Union / UK — GDPR

- Lawful basis is **legitimate interest** for B2B prospecting, which does not require prior consent.
- A written **Legitimate Interest Assessment** is completed and retained before any campaign type launches, covering: the business purpose, the necessity of email as the means, and the balance against the recipient's privacy rights.
- The data source is disclosed in the message.
- One-click opt-out; deletion on request.
- We contact business role-holders at companies matching a defined ICP. **We do not send to purchased lists**, which do not survive a balancing test.

France's August 2026 tightening applies to B2C prospecting; B2B remains permissible under legitimate interest. **[COUNSEL]** Confirm, and confirm whether we should exclude any member states outright.

### Platform sender requirements (Google, Yahoo, Microsoft)

Non-compliant mail is now **rejected at the receiving server**, not filtered. These are conditions of delivery, not optimizations:

- SPF, DKIM, and **aligned, passing DMARC** on every sending domain.
- Spam complaint rate held **below 0.10%**; 0.30% triggers enforcement.
- One-click unsubscribe (RFC 8058) on bulk sends.
- Minimum **14-day domain age** before production sending; **30-day volume ramp**; maximum 200/day on new domains.

**Operational rule:** we email only companies whose scan showed a real, specific gap. Relevance is our complaint-rate control — every recipient receives evidence about their own company.

---

## 4. Data, platforms, and measurement

- **Measurement uses official paid APIs.** We do not scrape AI search products in violation of their terms.
- **Client credentials.** Where a client grants access to their CMS or analytics, access is least-privilege, individually provisioned, logged, and revoked at engagement end. We do not share logins between clients.
- **Confidentiality.** Client strategy, roadmap, and performance data are confidential. Only anonymized aggregates enter published research (§1.4).
- **No security scanning of prospects.** Our prospect scans query public AI products about publicly available information. We do not probe, test, or scan prospect infrastructure.

---

## 5. Documents required before the first paid engagement

| Document | Length | Status |
|---|---|---|
| Master Services Agreement | 6–8 pp | Claude drafts → **counsel reviews** |
| Statement of Work template | 2 pp | Claude drafts → counsel reviews |
| This Compliance & Ethics Policy | 4 pp | **Counsel reviews** |
| Legitimate Interest Assessment | 2 pp | Claude drafts → counsel reviews |
| Website privacy policy + terms | 3 pp | Claude drafts → counsel reviews |

All five are within the 10-page target. The MSA and this policy are the two that genuinely need attorney time; the remainder are largely standard.

---

## 6. Review cadence

This policy is reviewed **quarterly**, and immediately upon: a change to FTC endorsement guidance, a material change to Google/Microsoft/Yahoo sender requirements, a change to the terms of any AI platform we query, or the first engagement with a client in a regulated vertical (healthcare, financial services, or legal), each of which carries its own advertising rules.

**[COUNSEL]** Flag any additional obligations if we take clients in healthcare, financial services, or legal services — sector-specific advertising rules would apply on top of everything above.
