#!/usr/bin/env python3
"""Render the plan Markdown into PDFs.

Exists because the previous PDFs were generated ad hoc and went stale the
moment the trading name changed — a compliance policy carrying the wrong
company name is worse than no PDF at all. Regenerating is now one command.

    python make_pdfs.py

Writes one PDF per source document plus a combined pack, into pdf/.
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable, KeepTogether, ListFlowable, ListItem, PageBreak, Paragraph,
    Preformatted, SimpleDocTemplate, Spacer, Table, TableStyle,
)

HERE = Path(__file__).parent
OUT = HERE / "pdf"

BRAND = "Shortlist AIO"

INK = colors.HexColor("#15181E")
MID = colors.HexColor("#3E4552")
SOFT = colors.HexColor("#6B7383")
RULE = colors.HexColor("#DCE0E9")
SIGNAL = colors.HexColor("#A25E05")
WASH = colors.HexColor("#F6E9D4")
SURFACE = colors.HexColor("#EEF1F6")

#: (source, title) for the plan pack. Rendered into pdf/.
DOCS = [
    ("README.md", "Overview"),
    ("BUSINESS-PLAN.md", "Business Plan"),
    ("FINANCIAL-MODEL.md", "Financial Model"),
    ("90-DAY-LAUNCH-PLAN.md", "90-Day Launch Plan"),
    ("COMPLIANCE-POLICY.md", "Compliance & Ethics Policy"),
    ("RESEARCH-NOTES.md", "Research Notes"),
]

#: The counsel pack, rendered into ../legal/pdf/. Draft markers and [COUNSEL]
#: questions are deliberately preserved here — unlike the website build, which
#: strips them, these PDFs exist precisely to carry those questions.
LEGAL = HERE.parent / "legal"
LEGAL_DOCS = [
    ("README.md", "Instruction to Counsel"),
    ("MSA.md", "Master Services Agreement"),
    ("CASL-screening-procedure.md", "CASL Screening Procedure"),
    ("SOW-template.md", "Statement of Work"),
    ("privacy-policy.md", "Privacy Policy"),
    ("website-terms.md", "Website Terms of Use"),
]


#: Operational runbooks, rendered into ../ops/pdf/. These are working
#: documents followed at a desk while filling in someone else's web forms, so
#: they are generated individually and never combined into a pack.
OPS = HERE.parent / "ops"
OPS_DOCS = [
    ("EMAIL-SETUP-SHEET.md", "Email Setup Sheet"),
    ("EMAIL-INFRASTRUCTURE.md", "Email Infrastructure Runbook"),
]


def styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    s = {
        "h1": ParagraphStyle("h1", parent=base["Title"], fontName="Helvetica-Bold",
                             fontSize=21, leading=25, textColor=INK,
                             alignment=TA_LEFT, spaceAfter=14, spaceBefore=0),
        "h2": ParagraphStyle("h2", parent=base["Heading2"], fontName="Helvetica-Bold",
                             fontSize=14.5, leading=18, textColor=INK,
                             spaceBefore=18, spaceAfter=7),
        "h3": ParagraphStyle("h3", parent=base["Heading3"], fontName="Helvetica-Bold",
                             fontSize=11.5, leading=14, textColor=SIGNAL,
                             spaceBefore=13, spaceAfter=5),
        "h4": ParagraphStyle("h4", parent=base["Heading4"], fontName="Helvetica-Bold",
                             fontSize=10, leading=13, textColor=MID,
                             spaceBefore=10, spaceAfter=4),
        "body": ParagraphStyle("body", parent=base["BodyText"], fontName="Helvetica",
                               fontSize=9.6, leading=14.2, textColor=INK,
                               spaceAfter=8, alignment=TA_LEFT),
        "quote": ParagraphStyle("quote", parent=base["BodyText"], fontName="Helvetica-Oblique",
                                fontSize=9.2, leading=13.5, textColor=MID,
                                leftIndent=14, spaceAfter=8, borderPadding=0),
        "cell": ParagraphStyle("cell", parent=base["BodyText"], fontName="Helvetica",
                               fontSize=8.2, leading=11, textColor=INK, spaceAfter=0),
        "cellhead": ParagraphStyle("cellhead", parent=base["BodyText"],
                                   fontName="Helvetica-Bold", fontSize=7.6, leading=10,
                                   textColor=SOFT, spaceAfter=0),
        "bullet": ParagraphStyle("bullet", parent=base["BodyText"], fontName="Helvetica",
                                 fontSize=9.6, leading=14, textColor=INK, spaceAfter=3),
    }
    return s


S = styles()

_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_BOLD = re.compile(r"\*\*(.+?)\*\*")
_ITAL = re.compile(r"(?<!\*)\*([^*]+?)\*(?!\*)")
_CODE = re.compile(r"`([^`]+)`")


def inline(text: str) -> str:
    """Convert inline Markdown to ReportLab's mini-HTML subset."""
    out = html.escape(text, quote=False)
    # Links first — their label may contain emphasis.
    out = _LINK.sub(lambda m: f'<font color="#7A4704">{m.group(1)}</font>', out)
    out = _BOLD.sub(r"<b>\1</b>", out)
    out = _ITAL.sub(r"<i>\1</i>", out)
    out = _CODE.sub(r'<font face="Courier" size="8.6">\1</font>', out)
    return out


def split_row(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def build_table(rows: list[list[str]], width: float) -> Table:
    """Render a Markdown table, sizing columns by content weight."""
    header, *body = rows
    ncols = len(header)
    weights = []
    for i in range(ncols):
        longest = max((len(r[i]) for r in rows if i < len(r)), default=8)
        weights.append(max(6, min(longest, 60)))
    total = sum(weights)
    widths = [width * w / total for w in weights]

    data = [[Paragraph(inline(c), S["cellhead"]) for c in header]]
    for r in body:
        r = (r + [""] * ncols)[:ncols]
        data.append([Paragraph(inline(c), S["cell"]) for c in r])

    t = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), SURFACE),
        ("LINEBELOW", (0, 0), (-1, 0), 0.6, RULE),
        ("LINEBELOW", (0, 1), (-1, -2), 0.4, RULE),
        ("BOX", (0, 0), (-1, -1), 0.6, RULE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def code_block(body: list[str], width: float):
    """Render a fenced block verbatim, shrinking the font rather than wrapping.

    These blocks exist to be copied into someone else's web form, so a value
    broken across two lines is a defect rather than a cosmetic flaw. Courier
    advances at 0.6 em, which makes the fitting calculation exact: shrink until
    the longest line fits, and only fall back to wrapping past the legibility
    floor.
    """
    text = "\n".join(body) or " "
    longest = max((len(line) for line in body), default=1)
    available = width - 16          # cell padding, both sides

    size = 8.5
    while size > 6.0 and longest * size * 0.6 > available:
        size -= 0.25

    style = ParagraphStyle(
        "code", fontName="Courier", fontSize=size, leading=size * 1.4,
        textColor=INK, alignment=TA_LEFT,
    )
    table = Table([[Preformatted(text, style)]], colWidths=[width])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), SURFACE),
        ("BOX", (0, 0), (-1, -1), 0.5, RULE),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return KeepTogether([Spacer(1, 4), table, Spacer(1, 8)])


def parse(md: str, width: float) -> list:
    """Convert a Markdown document into a Platypus flowable list."""
    flow: list = []
    lines = md.replace("\r\n", "\n").split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        # Fenced code block — must be matched before anything else, so its
        # contents are never interpreted as Markdown.
        if stripped.startswith("```"):
            i += 1
            buf: list[str] = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                buf.append(lines[i].rstrip())
                i += 1
            i += 1                                  # consume closing fence
            flow.append(code_block(buf, width))
            continue

        # Table — a header row followed by a |---| separator.
        if stripped.startswith("|") and i + 1 < len(lines) and \
                re.match(r"^\|[\s:\-|]+\|$", lines[i + 1].strip()):
            rows = [split_row(stripped)]
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(split_row(lines[i].strip()))
                i += 1
            flow.append(Spacer(1, 4))
            flow.append(build_table(rows, width))
            flow.append(Spacer(1, 10))
            continue

        if stripped.startswith("####"):
            flow.append(Paragraph(inline(stripped.lstrip("#").strip()), S["h4"])); i += 1; continue
        if stripped.startswith("###"):
            flow.append(Paragraph(inline(stripped.lstrip("#").strip()), S["h3"])); i += 1; continue
        if stripped.startswith("##"):
            flow.append(Paragraph(inline(stripped.lstrip("#").strip()), S["h2"])); i += 1; continue
        if stripped.startswith("#"):
            flow.append(Paragraph(inline(stripped.lstrip("#").strip()), S["h1"])); i += 1; continue

        if re.match(r"^(-{3,}|\*{3,}|_{3,})$", stripped):
            flow.append(Spacer(1, 6))
            flow.append(HRFlowable(width="100%", thickness=0.6, color=RULE))
            flow.append(Spacer(1, 8))
            i += 1
            continue

        # Blockquote — collected as one block.
        if stripped.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip().lstrip(">").strip())
                i += 1
            flow.append(Paragraph(inline(" ".join(buf)), S["quote"]))
            continue

        # Lists.
        if re.match(r"^([-*+]|\d+\.)\s+", stripped):
            items = []
            ordered = bool(re.match(r"^\d+\.", stripped))
            while i < len(lines) and re.match(r"^([-*+]|\d+\.)\s+", lines[i].strip()):
                text = re.sub(r"^([-*+]|\d+\.)\s+", "", lines[i].strip())
                items.append(ListItem(Paragraph(inline(text), S["bullet"]), leftIndent=16))
                i += 1
            flow.append(ListFlowable(
                items, bulletType="1" if ordered else "bullet",
                bulletFontSize=8, leftIndent=16, bulletColor=SIGNAL,
            ))
            flow.append(Spacer(1, 6))
            continue

        # Paragraph — join until a blank line or a new block starts.
        buf = []
        while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith(
                ("#", ">", "|", "---")) and not re.match(r"^([-*+]|\d+\.)\s+", lines[i].strip()):
            buf.append(lines[i].strip())
            i += 1
        if buf:
            flow.append(Paragraph(inline(" ".join(buf)), S["body"]))
    return flow


def furniture(canvas, doc):
    """Running header and footer."""
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(SOFT)
    canvas.drawString(doc.leftMargin, LETTER[1] - 0.55 * inch, BRAND)
    canvas.drawRightString(LETTER[0] - doc.rightMargin, LETTER[1] - 0.55 * inch,
                           getattr(doc, "docTitle", ""))
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.5)
    canvas.line(doc.leftMargin, LETTER[1] - 0.65 * inch,
                LETTER[0] - doc.rightMargin, LETTER[1] - 0.65 * inch)
    canvas.drawCentredString(LETTER[0] / 2, 0.5 * inch, str(canvas.getPageNumber()))
    canvas.restoreState()


def render(flow: list, path: Path, title: str) -> None:
    doc = SimpleDocTemplate(
        str(path), pagesize=LETTER,
        leftMargin=0.85 * inch, rightMargin=0.85 * inch,
        topMargin=0.85 * inch, bottomMargin=0.75 * inch,
        title=f"{BRAND} — {title}", author=BRAND,
    )
    doc.docTitle = title
    doc.build(flow, onFirstPage=furniture, onLaterPages=furniture)


def main() -> int:
    OUT.mkdir(exist_ok=True)
    # Usable width excludes both margins *and* the Frame's default 6pt padding
    # on each side; sizing tables to the margin box alone overflows the frame.
    width = LETTER[0] - 1.7 * inch - 12
    combined: list = []
    made = []

    for src, title in DOCS:
        path = HERE / src
        if not path.exists():
            print(f"  missing: {src}", file=sys.stderr)
            continue
        text = path.read_text()
        dest = OUT / f"{path.stem}.pdf"
        render(parse(text, width), dest, title)
        made.append(dest.name)
        print(f"  {src:26} -> pdf/{dest.name}")

        # Re-parse rather than reuse: flowables carry per-document layout
        # state and misbehave when shared between builds.
        if combined:
            combined.append(PageBreak())
        combined.extend(parse(text, width))

    pack = OUT / f"{BRAND.replace(' ', '-')}-Complete-Business-Plan.pdf"
    render(combined, pack, "Complete Business Plan")
    print(f"  {'(all documents)':26} -> pdf/{pack.name}")

    # Counsel pack.
    legal_out = LEGAL / "pdf"
    legal_out.mkdir(exist_ok=True)
    legal_combined: list = []
    print()
    for src, title in LEGAL_DOCS:
        path = LEGAL / src
        if not path.exists():
            print(f"  missing: legal/{src}", file=sys.stderr)
            continue
        text = path.read_text()
        dest = legal_out / f"{path.stem}.pdf"
        render(parse(text, width), dest, title)
        made.append(dest.name)
        print(f"  legal/{src:20} -> legal/pdf/{dest.name}")
        if legal_combined:
            legal_combined.append(PageBreak())
        legal_combined.extend(parse(text, width))

    legal_pack = legal_out / f"{BRAND.replace(' ', '-')}-Counsel-Pack.pdf"
    render(legal_combined, legal_pack, "Counsel Pack")
    print(f"  {'(all legal drafts)':26} -> legal/pdf/{legal_pack.name}")

    # Operational runbooks — individual PDFs only, no combined pack.
    ops_out = OPS / "pdf"
    ops_out.mkdir(exist_ok=True)
    print()
    for src, title in OPS_DOCS:
        path = OPS / src
        if not path.exists():
            print(f"  missing: ops/{src}", file=sys.stderr)
            continue
        dest = ops_out / f"{path.stem}.pdf"
        render(parse(path.read_text(), width), dest, title)
        made.append(dest.name)
        print(f"  ops/{src:22} -> ops/pdf/{dest.name}")

    # Remove combined packs left over from a previous trading name, so a
    # lawyer is never sent a document branded with a name we no longer use.
    #
    # Matched by suffix and filtered against the *current* expected filename
    # rather than by hardcoding a brand: hardcoding inverts the moment the
    # brand becomes the one being matched, deleting the fresh file and keeping
    # the stale one.
    keep = {pack.name, legal_pack.name}
    for directory, suffix in ((OUT, "-Complete-Business-Plan.pdf"),
                              (legal_out, "-Counsel-Pack.pdf")):
        for old in directory.glob(f"*{suffix}"):
            if old.name not in keep:
                old.unlink()
                print(f"  removed stale: {old.parent.name}/{old.name}")

    print(f"\n{len(made) + 2} PDFs written.")  # +2 combined packs
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
