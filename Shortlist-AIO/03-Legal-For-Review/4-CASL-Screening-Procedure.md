# CASL Screening Procedure — Outbound Email

> **DRAFT FOR REVIEW BY COUNSEL — NOT LEGAL ADVICE.**
> This is the operating procedure that keeps outbound email inside CASL. It is
> the highest-exposure process in the business and is written to be audited.

## 1. Why this document exists

Provider sends commercial electronic messages ("**CEMs**") from computer
systems located in Canada. **Canada's Anti-Spam Legislation applies on that
basis alone, regardless of where the recipient is.** CASL is consent-based
rather than opt-out. Administrative monetary penalties reach **CAD $10 million
per violation** for a corporation, directors and officers may be personally
liable, and CASL carries a private right of action.

Under CASL the **sender bears the burden of proving** consent or the
application of an exemption. This procedure exists to make that proof
routinely available.

## 2. The basis we rely on: the foreign-state exemption

Paragraph 3(f) of the *Electronic Commerce Protection Regulations* exempts a
CEM from CASL's consent requirement where:

1. the sender **reasonably believes** the message will be accessed in a listed
   foreign state — the **United States** is listed; and
2. the message **conforms to the law of that state** addressing conduct
   substantially similar to CASL — for the United States, **CAN-SPAM**.

Provider's cold outbound is therefore **United States only**, and every
message complies with CAN-SPAM.

> **[COUNSEL]** Please confirm this analysis for our fact pattern, and confirm
> that the country screen in §3 is a sufficient basis for the "reasonable
> belief" in limb 1.

## 3. Country screen — the controlling control

**3.1** A recipient enters a cold sequence **only** where the company has been
positively identified as United States–based.

**3.2** Identification is from **company records** — registered address, head
office, or the address published on the company's own site — and is recorded
with its source. **A top-level domain is not sufficient evidence** of
location and must not be used on its own.

**3.3** Where location cannot be positively established, the recipient **does
not enter a cold sequence.** Ambiguity resolves against sending.

**3.4** The screen is applied at list build and re-verified before each send.

**3.5** Canadian recipients are **excluded from cold outbound entirely.** See §5.

**3.6** The screen is implemented in the list pipeline as a hard gate that
blocks the send, not as a checklist step. A recipient without a recorded,
verified country cannot be added to a sequence.

## 4. CAN-SPAM conformity — every message, no exceptions

- Accurate "From", "Reply-To", and routing information; the sending domain is owned by Provider.
- A subject line that accurately reflects the message.
- Identification of Provider as the sender, with a valid **physical postal address** (the Manitoba registered office).
- A clear, working unsubscribe mechanism.
- Opt-outs honoured within **10 business days**; in practice, immediately.
- A global suppression list checked before every send.
- No harvested addresses; no dictionary attacks.

## 5. Canadian recipients

**5.1** Canadian recipients are excluded from cold outbound by default.

**5.2** If Provider later chooses to approach Canadian prospects, each message
must rest on **express or implied consent** established and logged *per
recipient* before sending. Implied consent by conspicuous publication requires
**all** of:

- the recipient's electronic address is **conspicuously published**;
- the publication is **not accompanied by a statement** that the person does not wish to receive unsolicited commercial messages; and
- the message is **relevant to that person's business, role, or functions**.

**5.3** Implied consent expires and must be tracked: **two years** from the
end of a business relationship or transaction; **six months** from an
inquiry. Expired consent is treated as no consent.

**5.4** Every Canadian CEM carries full CASL sender identification and an
unsubscribe mechanism honoured within 10 business days.

## 6. Record keeping — the proof obligation

For **every** recipient contacted, Provider records and retains for
**`[3]` years**:

| Field | Example |
|---|---|
| Recipient address and role | `ops@example.com`, VP Marketing |
| Company and verified country | Example Inc., **United States** |
| Country evidence and source | Head office address, example.com/about, retrieved `[date]` |
| Basis relied on | ECPR 3(f) foreign-state exemption |
| Address source and date collected | Company website, `[date]` |
| Messages sent | Campaign, template version, timestamps |
| Opt-out status and date honoured | — |

Records are exportable on request, so a regulator inquiry is answered from a
report rather than a reconstruction.

## 7. Additional belt-and-braces position

Provider's list is built from **conspicuously published business addresses**,
and every message is **relevant to the recipient's role** by construction —
it contains measurement of that recipient's own company. Provider therefore
expects to satisfy CASL implied consent on the merits **in addition to** the
foreign-state exemption, at negligible extra cost.

> **[COUNSEL]** If you prefer, we can rely on this as the primary basis rather
> than the fallback. Please advise which posture you want documented.

## 8. Escalation and review

**8.1** Any complaint alleging a CASL or CAN-SPAM breach is escalated to the
principal **within one business day**, the relevant sequence is paused, and
the recipient's record is produced.

**8.2** Sending stops entirely if the spam complaint rate exceeds **0.10%**.

**8.3** This procedure is reviewed **quarterly**, and immediately on any
change to CASL, the Regulations, the listed-state schedule, CAN-SPAM, or the
opening of a new target geography. **No new geography is opened until this
procedure has been extended to cover it and reviewed.**
