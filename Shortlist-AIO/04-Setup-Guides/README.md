# Setup guides

**You follow these.** They are the only documents in this folder tree that ask
you to do something at a keyboard.

| File | What it's for | When |
|---|---|---|
| `EMAIL-SETUP-SHEET.md` | Every field value, DNS record and checklist item for provisioning email, in the order the forms ask for them | **Now — this is the next task** |
| `EMAIL-INFRASTRUCTURE.md` | The reasoning: why nine domains, why separate registrations, warmup schedule, health thresholds, what to do when something breaks | Read once; return when a number looks wrong |

`pdf/` has both for reading away from a screen. **For actually filling in
forms, use the `.md` files** — copy-paste out of a PDF can pick up stray line
breaks.

## Before you start

The setup sheet uses `{FIRST}` and `{LAST}` placeholders. Do one
find-and-replace with your real first and last name and the whole document
becomes paste-ready.

## Order of operations

1. **Google Workspace** for `shortlistaio.com` — one seat, $8/mo, free aliases
2. **DNS** on the brand domain — MX, SPF, DKIM, DMARC
3. **Sending mailboxes** — 16 across the 8 sending domains
4. **Warmup on, immediately** — then leave them alone for 14 days

Step 3 is the urgent one. Domain aging started **28 August 2026** and runs 14
days whether or not mailboxes exist — but warmup only starts once they do. Set
them up now and the two clocks run in parallel instead of end to end.

## The mistakes that cost a week

- **Nameservers must be Namecheap BasicDNS.** On anything else, records you
  enter in Advanced DNS are simply not authoritative — everything looks right
  and nothing works.
- **Mail Settings must be "Custom MX".** Namecheap defaults to Email
  Forwarding, which injects its own MX records that you cannot delete as rows.
- **Never send cold outbound from `shortlistaio.com`.** It carries your
  contracts and invoices. The eight sending domains are consumable; it is not.
