# Shortlist AIO — master folder

Everything for the business lives here. Download this one folder and you have
the whole thing: the plan, the legal drafts, the setup guides, the software,
and the website.

**The business:** we make B2B software companies the vendor that ChatGPT,
Perplexity, Gemini and Google AI Overviews name when a buyer asks for the best
tool in their category. Sold as a fixed monthly programme.

| | |
|---|---|
| **Legal entity** | Glass House Gardens Inc. (Manitoba corporation) |
| **Trading name** | Shortlist AIO — *DBA registration pending* |
| **Registered office** | 40 Essex Drive, Steinbach, MB R5G 2Y6, Canada |
| **Brand domain** | shortlistaio.com |
| **Year-1 target** | ~$387,000 USD revenue, ~$70,900 exit MRR |

---

## Where to go

| Folder | What it is | Do you touch it? |
|---|---|---|
| **[01-Start-Here](01-Start-Here/)** | Current status, what's done, what's blocked, what I need from you | **Yes — read this first** |
| **[02-Business-Plan](02-Business-Plan/)** | The plan, financial model, launch plan, sourced research | Read once. Reference later. |
| **[03-Legal-For-Review](03-Legal-For-Review/)** | Six documents, each under 10 pages, each submitted separately | **Yes — submit these for review** |
| **[04-Setup-Guides](04-Setup-Guides/)** | Step-by-step email and DNS setup with copy-paste values | **Yes — follow these** |
| **[05-Software-Scanner](05-Software-Scanner/)** | The measurement tool the business runs on | No — I operate this |
| **[06-Website](06-Website/)** | shortlistaio.com | No — I maintain it; you approve and deploy |
| **[tools](tools/)** | Regenerates all the PDFs | No |

Every folder has its own `README.md` explaining what's inside, whether you
need to touch it, and how.

## File formats

Each document exists as **Markdown** (`.md`) and **PDF** (`pdf/` subfolder).

- **Markdown** — the source. Edit these; the PDFs regenerate from them.
- **PDF** — for sending to people. Legal reviewers, accountants, anyone
  outside the project.

Never edit a PDF directly. Edit the `.md` and run `python tools/make_pdfs.py`.

## Files marked DELETE-

Anything prefixed `DELETE-` is redundant or superseded. I've renamed rather
than removed them so you can confirm before they go. See
[01-Start-Here](01-Start-Here/) for what each one was.
