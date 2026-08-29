# Legal documents — for review

Six drafts. **Every one is under 10 pages**, so each fits a free-review limit
and can be submitted on its own. Submit them individually — do not combine.

**None of these is legal advice.** They are drafts prepared with AI
assistance for a lawyer to review. Bracketed fields `[LIKE THIS]` need a
decision. Blocks marked **[COUNSEL]** are specific questions for the reviewer;
**[ACCOUNTANT]** items are for a cross-border CPA and do not need a lawyer.

---

## The six documents

| # | Document | Pages | Priority | Why |
|---|---|---|---|---|
| 1 | Master Services Agreement | **6** | **First** | The contract every client signs. §3 (no outcome guarantee), §9 (measurement data rights), §12 (liability cap) are the clauses that decide disputes. |
| 2 | Statement of Work Template | **3** | Later | Per-engagement scope. Mostly mechanics. |
| 3 | Compliance & Ethics Policy | **7** | **First** | Referenced by the MSA, so it is read as binding. Covers the FTC review rules and our hard limits. |
| 4 | CASL Screening Procedure | **3** | **First** | Highest legal exposure in the business — CAD $10M per violation, with director liability. |
| 5 | Privacy Policy | **3** | Later | Standard. Goes on the website. |
| 6 | Website Terms of Use | **2** | Later | Standard. Goes on the website. |

**Submit 1, 3 and 4 first.** They cross-reference each other and are where the
real risk sits. 2, 5 and 6 can wait — unpaid pilot work carries no contract
risk, and the site is not live yet.

---

## What to tell the reviewer

Copy this into your submission:

> We are a Manitoba corporation (Glass House Gardens Inc.) selling marketing
> measurement and content services to United States business customers,
> remotely, with no US presence. Our three concerns, in order:
>
> 1. **Outcome-guarantee exposure.** We measure and try to influence
>    third-party AI systems we do not control. MSA §3 is meant to foreclose any
>    claim that we promised a result, including claims founded on pre-contract
>    statements.
> 2. **CASL.** We send commercial email from Canada to US recipients and rely
>    on the foreign-state exemption in ECPR para. 3(f). Please confirm the
>    analysis and whether our country screen supports the required reasonable
>    belief.
> 3. **Rights in aggregated measurement data.** MSA §9 lets us publish
>    anonymised aggregate research built from client and prospect measurements.
>    This is a core business asset; please confirm it is adequately drafted and
>    survives termination.
>
> Also of note: jurisdiction (MSA §16) — US clients often resist Manitoba, and
> we would like a fallback position.

---

## Trademark question — worth adding to your review

You plan to register **Shortlist AIO** as a Manitoba business name. Two things
are true at once, and they are easy to conflate:

**Filing the DBA will not itself infringe anything.** A provincial business
name registration is an administrative filing. It creates no trademark rights
and adjudicates nobody else's. The Companies Office name search checks for
conflicts with *other Manitoba registrations* — it does not check trademarks,
and it does not look at the United States at all.

**But there are existing users of the name, and every one of your customers is
American.** Publicly visible as of August 2026:

| Name | What they do |
|---|---|
| **Shortlist** (shortlist.co, now Worksuite) | Freelancer management SaaS, San Francisco — used "Shortlist" commercially in the US |
| **shortlistd.io** | AI recruitment platform |
| **shortlists.io** | AI-native recruiting platform for agencies |
| **Shortlister** (myshortlister.com) | Vendor comparison |

**Why this is probably survivable:** they all cluster in HR, recruiting and
freelancer management. We sell marketing measurement and content services — a
different service class. Infringement turns on likelihood of confusion between
*related* goods and services. "Shortlist" is also an ordinary English word,
and descriptive marks get narrow protection. The crowded field cuts both ways:
several parties using near-identical names means no one of them holds strong
exclusive rights.

**Why it still needs checking:** US trademark rights are **use-based**, so an
earlier US user has priority regardless of what you register in Manitoba. A
cease-and-desist arriving after you have built domain authority and client
contracts around the name is expensive — not because you would necessarily
lose, but because rebranding mid-flight would cost far more than checking now.

**Ask your reviewer:**

> We intend to trade as "Shortlist AIO" selling AI-search-visibility and
> content marketing services (roughly Nice class 35) to US customers, from a
> Manitoba corporation. Existing US users of "Shortlist" appear to be in HR and
> recruiting software (classes 9/42). Is a US clearance search warranted before
> we build brand equity, and does the class separation give us reasonable
> comfort?

**Free check you can run yourself first:** search `SHORTLIST` at
<https://tmsearch.uspto.gov> and filter to classes 35 and 42. Ten minutes, no
cost, and it tells you whether there is a registered mark worth worrying about.

**Do not treat the $105 DBA filing as brand protection.** It is a compliance
step so you can lawfully trade under the name. Actual protection is a
trademark registration, and that is a separate decision for a later year.

---

## Editing these

Edit the `.md` files. The PDFs in `pdf/` are generated — run
`python ../tools/make_pdfs.py` after any change.

Two of these files are also the live source for the website: `5-Privacy-Policy.md`
and `6-Website-Terms-of-Use.md` are published to shortlistaio.com by
`../06-Website/build.py`. **The website build strips the draft warnings and
[COUNSEL] notes; the PDFs deliberately keep them.** Same source, two audiences.
