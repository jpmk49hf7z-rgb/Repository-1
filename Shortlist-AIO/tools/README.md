# tools

**You do not need to touch this.**

`make_pdfs.py` regenerates every PDF in the project from the Markdown sources.

```bash
python tools/make_pdfs.py
```

Run it after editing any `.md` file in `02-Business-Plan/`,
`03-Legal-For-Review/` or `04-Setup-Guides/`. It writes into each folder's
`pdf/` subfolder.

Editing a PDF directly is always the wrong move — the next run overwrites it.
Edit the Markdown.

Requires `reportlab` (`pip install reportlab`).
