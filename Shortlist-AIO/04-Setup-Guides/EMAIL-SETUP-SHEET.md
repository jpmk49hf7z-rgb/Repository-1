# Email Setup Sheet

Everything needed to provision email, in the order the forms ask for it.
Replace `{FIRST}` and `{LAST}` with the principal's actual first and last name
throughout — one find-and-replace does the whole document.

---

## Business details (used by both signups)

```
Business name:      Shortlist AIO
Legal entity:       Glass House Gardens Inc.
Address:            40 Essex Drive
City:               Steinbach
Province:           Manitoba (MB)
Postal code:        R5G 2Y6
Country:            Canada
Employees:          1 (just me / 1-9)
Primary domain:     shortlistaio.com
```

---

## Part 1 — Google Workspace (brand mailbox)

**Go to:** https://workspace.google.com/business/signup/welcome

Choose **Business Starter — $8/user/month**. One seat only.

### Signup form

```
Business name:              Shortlist AIO
Number of employees:        Just you
Region:                     Canada
First name:                 {FIRST}
Last name:                  {LAST}
Current email address:      (your existing personal address)
Domain:                     Yes, I have a domain
Domain name:                shortlistaio.com
Username:                   {FIRST}
Full new address:           {FIRST}@shortlistaio.com
```

### After signup: verify the domain

Google gives you a TXT record. In Namecheap: **Domain List → shortlistaio.com
→ Manage → Advanced DNS → Add New Record**

```
Type:   TXT Record
Host:   @
Value:  google-site-verification=XXXXXXXX   (Google supplies this)
TTL:    Automatic
```

### Then: MX records for shortlistaio.com

Delete any existing MX records first (Namecheap adds parking records by
default and they will silently break delivery). Also set **Mail Settings** to
*Custom MX* rather than Namecheap's email forwarding.

```
Type: MX Record   Host: @   Value: smtp.google.com   Priority: 1   TTL: Automatic
```

That single record is Google's current recommendation. If the interface
rejects it, the legacy five-record set also works:

```
MX  @  aspmx.l.google.com          Priority 1
MX  @  alt1.aspmx.l.google.com     Priority 5
MX  @  alt2.aspmx.l.google.com     Priority 5
MX  @  alt3.aspmx.l.google.com     Priority 10
MX  @  alt4.aspmx.l.google.com     Priority 10
```

### Then: SPF and DMARC for shortlistaio.com

```
Type: TXT Record   Host: @        Value: v=spf1 include:_spf.google.com ~all
Type: TXT Record   Host: _dmarc   Value: v=DMARC1; p=none; rua=mailto:dmarc@shortlistaio.com; fo=1; adkim=r; aspf=r
```

DKIM is generated inside the Google Admin console, not here:
**Admin → Apps → Google Workspace → Gmail → Authenticate email → Generate new
record** (choose 2048-bit). It gives you a TXT record with host
`google._domainkey` — add that in Namecheap the same way.

### Free aliases — add these after the mailbox exists

**Admin → Directory → Users → {FIRST} → User information → Email aliases**

```
hello@shortlistaio.com
privacy@shortlistaio.com
dmarc@shortlistaio.com
billing@shortlistaio.com
support@shortlistaio.com
```

All five deliver into the one paid mailbox. No extra cost.

---

## Part 2 — Sending infrastructure (16 mailboxes)

**Go to:** https://maildoso.com

Sign up, then add the eight sending domains. Most providers in this category
let you paste a list and will set DNS automatically if you delegate
nameservers — **do not delegate the brand domain**, only these eight.

### The eight sending domains

```
getshortlistaio.com
tryshortlistaio.com
useshortlistaio.com
goshortlistaio.com
joinshortlistaio.com
withshortlistaio.com
shortlistaiohq.com
shortlistaioteam.com
```

### The sixteen mailboxes — two per domain

```
{FIRST}@getshortlistaio.com
{FIRST}.{LAST}@getshortlistaio.com
{FIRST}@tryshortlistaio.com
{FIRST}.{LAST}@tryshortlistaio.com
{FIRST}@useshortlistaio.com
{FIRST}.{LAST}@useshortlistaio.com
{FIRST}@goshortlistaio.com
{FIRST}.{LAST}@goshortlistaio.com
{FIRST}@joinshortlistaio.com
{FIRST}.{LAST}@joinshortlistaio.com
{FIRST}@withshortlistaio.com
{FIRST}.{LAST}@withshortlistaio.com
{FIRST}@shortlistaiohq.com
{FIRST}.{LAST}@shortlistaiohq.com
{FIRST}@shortlistaioteam.com
{FIRST}.{LAST}@shortlistaioteam.com
```

### Display name and signature — same on every mailbox

```
Display name:  {FIRST} {LAST}
```

```
{FIRST} {LAST}
Shortlist AIO
shortlistaio.com

Glass House Gardens Inc. o/a Shortlist AIO
40 Essex Drive, Steinbach, MB R5G 2Y6, Canada

Don't want to hear from me? Reply "no thanks" and I'll remove you.
```

The postal address is a CAN-SPAM requirement on every commercial message, not
a nicety. The opt-out line must work: honour it within 10 business days, and
in practice immediately.

*Note:* use "o/a Shortlist AIO" only once the Manitoba business name
registration is filed. Until then, write `Glass House Gardens Inc.` alone.

### Settings to confirm at the provider

```
Warmup:                    ON, all 16 mailboxes, starting immediately
Daily send limit:          15 per mailbox (hard cap)
Open tracking:             OFF
Click tracking:            OFF
Custom tracking domain:    none
```

Open and click tracking **off** is deliberate and is what the published
privacy policy says. Several providers default them on — check.

---

## Part 3 — Verify before any real send

Run this once DNS has propagated (allow up to 24 hours, usually far less).

- [ ] Exactly **one** SPF record per domain; two is a permanent failure
- [ ] DKIM verifies; 2048-bit
- [ ] DMARC present, and **SPF and DKIM both align** with the From domain
- [ ] Namecheap parking MX records deleted from shortlistaio.com
- [ ] Namecheap email forwarding disabled on shortlistaio.com
- [ ] Every sending domain registered with Google Postmaster Tools and Microsoft SNDS
- [ ] Send a seed test to Gmail, Outlook and Yahoo — confirm **inbox**, not Promotions or Junk
- [ ] mail-tester.com score 9+/10

Free checks: https://mxtoolbox.com/SuperTool.aspx and https://www.mail-tester.com

---

## What not to do

- **No sending from `shortlistaio.com`.** Ever. It carries contracts and
  invoices; the eight sending domains are consumable, it is not.
- **No `info@`, `sales@`, `team@` or `noreply@`** on sending mailboxes.
- **Do not skip warmup** even though the domains are new and clean. Fourteen
  days of aging, thirty days of ramp, no exceptions.
- **Do not exceed 15/day per mailbox** during month one.
