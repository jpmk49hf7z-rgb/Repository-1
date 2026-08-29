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
ROOT = HERE.parent

BRAND = "Shortlist AIO"

#: Palette, matched to the website and the client report so every artefact
#: the business produces reads as one system.
INK = colors.HexColor("#15181E")
MID = colors.HexColor("#3E4552")
SOFT = colors.HexColor("#6B7383")
RULE = colors.HexColor("#DCE0E9")
SIGNAL = colors.HexColor("#A25E05")
WASH = colors.HexColor("#F6E9D4")
SURFACE = colors.HexColor("#EEF1F6")

#: Each entry is (folder, [(filename, title), ...]). PDFs are written into a
#: pdf/ subfolder alongside the Markdown, so every folder is self-contained
#: and can be handed to someone on its own.
GROUPS = [
    ("02-Business-Plan", [
        ("BUSINESS-PLAN.md", "Business Plan"),
        ("FINANCIAL-MODEL.md", "Financial Model"),
        ("90-DAY-LAUNCH-PLAN.md", "90-Day Launch Plan"),
        ("RESEARCH-NOTES.md", "Research Notes"),
    ]),
    # Reviewed individually — each is under 10 pages so it fits a free-review
    # limit, and draft markers and [COUNSEL] questions are deliberately kept.
    ("03-Legal-For-Review", [
        ("1-Master-Services-Agreement.md", "Master Services Agreement"),
        ("2-Statement-of-Work-Template.md", "Statement of Work"),
        ("3-Compliance-and-Ethics-Policy.md", "Compliance & Ethics Policy"),
        ("4-CASL-Screening-Procedure.md", "CASL Screening Procedure"),
        ("5-Privacy-Policy.md", "Privacy Policy"),
        ("6-Website-Terms-of-Use.md", "Website Terms of Use"),
    ]),
    ("04-Setup-Guides", [
        ("EMAIL-SETUP-SHEET.md", "Email Setup Sheet"),
        ("EMAIL-INFRASTRUCTURE.md", "Email Infrastructure Runbook"),
    ]),
]

#: Only the business plan gets a combined pack. The legal documents are
#: submitted one at a time, and the setup guides are followed at a desk.
COMBINED_FROM = "02-Business-Plan"


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
    width = LETTER[0] - 1.7 * inch - 12   # margins plus the Frame's 6pt padding
    made = 0

    for folder, docs in GROUPS:
        src_dir = ROOT / folder
        out_dir = src_dir / "pdf"
        out_dir.mkdir(parents=True, exist_ok=True)
        combined: list = []

        for name, title in docs:
            path = src_dir / name
            if not path.exists():
                print(f"  missing: {folder}/{name}", file=sys.stderr)
                continue
            text = path.read_text()
            dest = out_dir / f"{path.stem}.pdf"
            render(parse(text, width), dest, title)
            made += 1
            print(f"  {folder}/{name:34} -> pdf/{dest.name}")

            if folder == COMBINED_FROM:
                # Re-parse rather than reuse: flowables carry per-document
                # layout state and misbehave when shared between builds.
                if combined:
                    combined.append(PageBreak())
                combined.extend(parse(text, width))

        if folder == COMBINED_FROM and combined:
            pack = out_dir / f"{BRAND.replace(' ', '-')}-Complete-Business-Plan.pdf"
            render(combined, pack, "Complete Business Plan")
            made += 1
            print(f"  {'(all plan documents)':47} -> pdf/{pack.name}")
        print()

    # Sweep packs left from a previous trading name. Matched by suffix and
    # filtered against the current expected name rather than hardcoding a
    # brand, which inverts the moment the brand becomes the one being matched.
    expected = f"{BRAND.replace(' ', '-')}-Complete-Business-Plan.pdf"
    for old in (ROOT / COMBINED_FROM / "pdf").glob("*-Complete-Business-Plan.pdf"):
        if old.name != expected:
            old.unlink()
            print(f"  removed stale: {old.name}")

    print(f"{made} PDFs written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
