# Shortlist — Compliance & Ethics Policy

**Status: draft for review by counsel.** This document states the operating rules the business binds itself to. It is written to be reviewed as a standalone instrument and to be referenced by the MSA.

Nothing here is legal advice. Items marked **[COUNSEL]** are specific questions for the reviewing attorney.

---

## 1. Entity and contracting

**A Manitoba share corporation**, already incorporated and held by the principal, who is sole director, sole signatory, and account holder for all financial and platform accounts. All work is performed by the principal using AI systems under the principal's direction and review. The company has no US presence: no US office, no US employees, no dependent agent in the US, and no US-situated equipment.

**[COUNSEL]** Confirm professional liability (E&O) coverage timing — before the first paid engagement, or at a stated client count.
**[COUNSEL]** Confirm whether Manitoba Retail Sales Tax applies to any part of the service offering, including for the small number of Canadian clients we may take.

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

### Canada — CASL applies first, because we send from Canada

Canada's Anti-Spam Legislation is **consent-based**, not opt-out. It reaches commercial electronic messages sent from a computer system in Canada regardless of where the recipient sits. Administrative monetary penalties run to **CAD $10 million per violation** for a corporation, directors and officers can be held personally liable, and the statute carries a private right of action. It is the single largest legal exposure in this business, and it is fully manageable.

**The controlling provision is the foreign-state exemption** — Electronic Commerce Protection Regulations, para. 3(f). A commercial electronic message is exempt from CASL's consent requirement where the sender reasonably believes it will be accessed in a listed foreign state (the United States is listed) **and** the message conforms to that state's law addressing spam. US-targeted outreach that complies with CAN-SPAM therefore sits inside the exemption.

**Operational rules, binding on every campaign:**

1. **Cold sequences target US recipients only.** Country is a hard filter at list-build time, verified from company records rather than inferred from a top-level domain, and re-checked before send. A recipient we cannot confidently place in the US does not enter a cold sequence.
2. **Canadian prospects are excluded from cold outbound entirely.** If we later choose to approach them, it is under CASL implied consent — a conspicuously published business address, no statement refusing commercial messages, and a message relevant to that person's role — assessed and logged per recipient, and understood to expire (two years from a transaction, six months from an inquiry).
3. **The basis for contacting every recipient is recorded and retained**, together with the source and date of the address. Under CASL the sender bears the burden of proving consent or exemption.
4. Sender identification and a working unsubscribe honored within **10 business days** appear on every message — required by CASL and CAN-SPAM alike, so this is invariant.

**[COUNSEL]** Confirm the para. 3(f) analysis for our fact pattern, and confirm rule 1 is a sufficient screen. If counsel prefers belt-and-braces, we can additionally satisfy CASL implied consent on US recipients at negligible cost — our list is built from conspicuously published business addresses and every message is role-relevant by construction.

### United States — CAN-SPAM

- Accurate "From", "Reply-To", and routing information.
- Subject lines that reflect the message honestly.
- A valid physical postal address in every message — the Manitoba registered office address.
- A clear opt-out mechanism, honored within **10 business days**; suppression list checked before every send.

### European Union / UK — GDPR

- Lawful basis is **legitimate interest** for B2B prospecting, which does not require prior consent.
- A written **Legitimate Interest Assessment** is completed and retained before any campaign type launches, covering: the business purpose, the necessity of email as the means, and the balance against the recipient's privacy rights.
- The data source is disclosed in the message.
- One-click opt-out; deletion on request.
- We contact business role-holders at companies matching a defined ICP. **We do not send to purchased lists**, which do not survive a balancing test.

France's August 2026 tightening applies to B2C prospecting; B2B remains permissible under legitimate interest. GDPR is not engaged while outbound is US-only; it becomes live the moment EU targeting opens. **[COUNSEL]** Confirm, and confirm whether we should exclude any member states outright.

### Platform sender requirements (Google, Yahoo, Microsoft)

Non-compliant mail is now **rejected at the receiving server**, not filtered. These are conditions of delivery, not optimizations:

- SPF, DKIM, and **aligned, passing DMARC** on every sending domain.
- Spam complaint rate held **below 0.10%**; 0.30% triggers enforcement.
- One-click unsubscribe (RFC 8058) on bulk sends.
- Minimum **14-day domain age** before production sending; **30-day volume ramp**; maximum 200/day on new domains.

**Operational rule:** we email only companies whose scan showed a real, specific gap. Relevance is our complaint-rate control — every recipient receives evidence about their own company.

---

## 3A. Cross-border tax and payments

The company is Canadian; substantially all revenue is American. These are the resulting obligations. Every item here is an **accountant** question rather than a counsel question, but they belong in one document.

### US federal — no tax, but a filing

Under Articles V and VII of the Canada–US tax treaty, business profits are taxable in the US only through a **permanent establishment** there. Performing services from Canada for US clients creates none. The exemption is not self-executing:

- File **Form 1120-F** annually as a *protective return*, marked as such, with **Form 8833** attached disclosing the treaty-based position under Article VII. Filing starts the IRS assessment clock and preserves the position; a late filing can forfeit deductions.
- Deadline is the 15th day of the 6th month after year-end for a corporation with no US permanent establishment.

### US withholding — none, but documentation is required

Services performed entirely outside the US are **foreign-source income** and fall outside the 30% withholding regime. US clients will nonetheless request documentation of foreign status before paying: provide **Form W-8BEN-E**. One form, reusable, refreshed every three years. A client's accounts-payable team asking for a W-9 is asking the wrong question; the W-8BEN-E is the answer.

### US state taxes — the real watch item

Tax treaties bind the federal government, **not the states**. Several states assert economic nexus for income or gross-receipts tax without any physical presence — Washington's B&O, Ohio's and Oregon's CAT, the Texas franchise tax, the Nevada commerce tax, and the San Francisco gross receipts tax among them. At the base case's revenue spread across many clients we expect to sit under most thresholds, but this is a monitoring obligation, not a one-time answer.

Separately, most states do not tax marketing or advertising services, but a minority tax categories our work could touch — Texas taxes data processing services, and several others tax specified services.

**[ACCOUNTANT]** Review state economic-nexus thresholds annually against the actual client roster by state, and confirm whether any client's state characterizes our deliverables as a taxable service.

### GST/HST — zero-rated, and worth registering for

Advisory, consulting, and professional services supplied to a **non-resident person who is not registered for GST/HST** are zero-rated under Schedule VI, Part V, s. 23. We charge US clients 0%. Zero-rated is not exempt: we may still claim **input tax credits** on GST/HST paid on Canadian business expenses, which makes voluntary registration worthwhile before the $30,000 CAD small-supplier threshold is crossed.

The supplier bears the burden of verifying non-residence and non-registration, so client onboarding captures and retains that evidence. The section 23 exclusions — litigation services, services in respect of Canadian real property or tangible property, and acting as the non-resident's agent or soliciting orders on their behalf — do not describe our work, but the last one is worth watching if the service ever extends toward selling on a client's behalf.

**[ACCOUNTANT]** Confirm the s. 23 characterization of each tier in the offer ladder, and set the registration date.

### Payments and currency

Invoice in **USD**. Stripe supports Canadian businesses charging in USD, but converts to the settlement currency automatically, taking roughly **1%** — about $3,900 a year on base-case revenue. Avoid it by settling into a **US-domiciled** USD account, which a Canadian-incorporated business can open on its existing registration documents. A USD account at a Canadian bank does not solve this, because it still settles over the Canadian network. Set this up before the first invoice.

Costs are largely USD too — LLM APIs, sending tools, domains — so billing in USD is a natural hedge and leaves only retained earnings exposed to FX.

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
| CASL screening procedure + consent/exemption log | 2 pp | Claude drafts → **counsel reviews** |
| Form W-8BEN-E (for US clients) | 1 pp | Principal signs; no drafting needed |
| Website privacy policy + terms | 3 pp | Claude drafts → counsel reviews |
| GDPR Legitimate Interest Assessment (deferred — only if EU targeting opens) | 2 pp | Claude drafts → counsel reviews |

All are within the 10-page target. The MSA, this policy, and the CASL screening procedure are the three that genuinely need attorney time; the remainder are largely standard. The GDPR Legitimate Interest Assessment is deferred until EU targeting opens — it is not needed for a US-only list.

Annual filings, handled by the accountant rather than counsel: **Form 1120-F** protective return with **Form 8833** attached (US), the Canadian T2 corporate return, and GST/HST returns once registered.

---

## 6. Review cadence

This policy is reviewed **quarterly**, and immediately upon: a change to FTC endorsement guidance, a change to CASL or the Electronic Commerce Protection Regulations, a material change to Google/Microsoft/Yahoo sender requirements, a change to the terms of any AI platform we query, the opening of a new target geography, or the first engagement with a client in a regulated vertical (healthcare, financial services, or legal), each of which carries its own advertising rules.

**Annually**, before filing: the accountant reviews US state economic-nexus thresholds against the actual client roster by state (§3A).

**[COUNSEL]** Flag any additional obligations if we take clients in healthcare, financial services, or legal services — sector-specific advertising rules would apply on top of everything above.
