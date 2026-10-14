#!/usr/bin/env python3
"""Generate printable PDF with side-by-side UI-style chunking examples."""

from __future__ import annotations

import html
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from rag_chunkers import (
    CHUNK_BORDERS,
    CHUNK_COLORS,
    PDF_EXCERPTS,
    SAMPLE_DOCUMENTS,
    STRATEGY_INFO,
    Chunk,
    chunk_document,
)

OUT = Path(__file__).resolve().parent / "RAG_Chunking_Lab_Guide.pdf"

TEAL = colors.HexColor("#0f6e6a")
INK = colors.HexColor("#14212b")
MUTED = colors.HexColor("#5a6675")
LIGHT = colors.HexColor("#e6f4f4")
PAPER = colors.HexColor("#f8f6f3")


def esc(text: str) -> str:
    return html.escape(text)


def searchable_chunks(chunks: list[Chunk]) -> list[Chunk]:
    return [c for c in chunks if c.role != "parent"]


def highlight_on_white(hex_color: str, opacity: float = 0.4) -> str:
    """Blend #RRGGBB(AA) over white for PDF backColor (no alpha support)."""
    h = hex_color.lstrip("#")
    if len(h) >= 8:
        opacity = int(h[6:8], 16) / 255
    h = h[:6]
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    r = int(r * opacity + 255 * (1 - opacity))
    g = int(g * opacity + 255 * (1 - opacity))
    b = int(b * opacity + 255 * (1 - opacity))
    return f"#{r:02x}{g:02x}{b:02x}"


def highlighted_source_xml(content: str, chunks: list[Chunk]) -> str:
    parts: list[str] = []
    cursor = 0
    searchable = sorted(searchable_chunks(chunks), key=lambda c: c.start)
    for i, chunk in enumerate(searchable):
        if chunk.start > cursor:
            parts.append(esc(content[cursor : chunk.start]))
        bg = highlight_on_white(CHUNK_COLORS[i % len(CHUNK_COLORS)])
        parts.append(
            f'<font backColor="{bg}">{esc(content[chunk.start : chunk.end])}</font>'
        )
        cursor = max(cursor, chunk.end)
    if cursor < len(content):
        parts.append(esc(content[cursor:]))
    return "".join(parts).replace("\n", "<br/>")


def chunk_card_xml(chunk: Chunk, index: int, strategy: str) -> str:
    border = CHUNK_BORDERS[index % len(CHUNK_BORDERS)] if chunk.role != "parent" else "#3d4f5c"
    badge = "not embedded" if chunk.role == "parent" else "embedded"
    labels = []
    if chunk.label:
        labels.append(chunk.label.replace("·", "*"))
    if chunk.split_level:
        labels.append(chunk.split_level)
    label_row = " * ".join(labels)

    meta = f"chars {chunk.start}-{chunk.end} * {chunk.char_count} chars"
    if chunk.similarity_to_prev is not None:
        meta += f" * sim to prev: {chunk.similarity_to_prev:.2f}"
    if chunk.role == "child" and chunk.parent_id:
        meta += f" * parent: {chunk.parent_id}"

    text = chunk.text if strategy == "proposition" else chunk.text.strip()
    bg = "#f8f6f2" if chunk.role == "parent" else "#ffffff"

    return (
        f'<font color="{border}"><b>|</b></font> '
        f"<b>{esc(chunk.id)}</b> "
        f'<font color="#0f6e6a">{esc(label_row)}</font> '
        f'<font color="#5a6675">[{badge}]</font><br/>'
        f"{esc(text)}<br/>"
        f'<font size="7" color="#5a6675">{esc(meta)}</font><br/><br/>'
    )


def chunks_panel_xml(chunks: list[Chunk], strategy: str) -> str:
    parents = [c for c in chunks if c.role == "parent"]
    children = [c for c in chunks if c.role == "child"]
    regular = [c for c in chunks if not c.role]
    parts: list[str] = []

    if parents:
        parts.append("<b>PARENTS (stored - not embedded)</b><br/>")
        for p in parents:
            parts.append(chunk_card_xml(p, -1, strategy))

    if children:
        parts.append("<br/><b>CHILDREN (embedded for search)</b><br/>")
        for i, c in enumerate(children):
            parts.append(chunk_card_xml(c, i, strategy))

    if regular:
        if strategy != "parent-child":
            parts.append("<br/><b>ALL CHUNKS</b><br/>")
        for i, c in enumerate(regular):
            parts.append(chunk_card_xml(c, i, strategy))

    return "".join(parts)


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="CoverTitle",
            fontSize=28,
            leading=32,
            textColor=colors.white,
            fontName="Helvetica-Bold",
        )
    )
    styles.add(
        ParagraphStyle(
            name="CoverSub",
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#b8c4d0"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="PageTitle",
            fontSize=16,
            leading=20,
            textColor=TEAL,
            fontName="Helvetica-Bold",
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ControlBar",
            fontSize=9,
            leading=12,
            textColor=INK,
            backColor=colors.HexColor("#f0eeea"),
            borderPadding=8,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SourceMono",
            fontSize=6,
            leading=7.5,
            fontName="Courier",
            textColor=INK,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ChunkPanel",
            fontSize=7,
            leading=9,
            textColor=INK,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Body",
            fontSize=11,
            leading=14,
            textColor=INK,
        )
    )
    return styles


def side_by_side_flow(
    styles,
    page_title: str,
    doc: dict,
    strategy: str,
    chunks: list[Chunk],
    options_note: str = "",
):
    s_label, s_desc = STRATEGY_INFO[strategy]
    searchable = searchable_chunks(chunks)
    parents = sum(1 for c in chunks if c.role == "parent")
    stats = f"{len(chunks)} total chunks * {len(searchable)} searchable (embedded)"
    if parents:
        stats += f" * {parents} parents (text only)"

    extra = f"<br/><i>{esc(options_note)}</i>" if options_note else ""
    control = (
        f"<b>Document:</b> {esc(doc['title'])} &nbsp;&nbsp; "
        f"<b>Strategy:</b> {esc(s_label)}<br/>"
        f"{esc(doc['description'])}<br/>"
        f"<i>{esc(s_desc)}</i>{extra}<br/>"
        f"<b><font color='#0a4f4c'>{esc(stats)}</font></b>"
    )

    source_xml = highlighted_source_xml(doc["content"], chunks)
    chunks_xml = chunks_panel_xml(chunks, strategy)

    col_width = (landscape(A4)[0] - 36 * mm) / 2 - 4 * mm

    table = Table(
        [
            [
                Paragraph("<b>Source document</b>", styles["Body"]),
                Paragraph("<b>Chunks</b>", styles["Body"]),
            ],
            [
                Paragraph(source_xml, styles["SourceMono"]),
                Paragraph(chunks_xml, styles["ChunkPanel"]),
            ],
        ],
        colWidths=[col_width, col_width],
    )
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOX", (0, 1), (0, 1), 0.5, colors.HexColor("#d8d2c8")),
                ("BOX", (1, 1), (1, 1), 0.5, colors.HexColor("#d8d2c8")),
                ("BACKGROUND", (0, 1), (0, 1), colors.white),
                ("BACKGROUND", (1, 1), (1, 1), PAPER),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 1), (-1, 1), 6),
                ("BOTTOMPADDING", (0, 1), (-1, 1), 6),
            ]
        )
    )

    return [
        Paragraph(esc(page_title), styles["PageTitle"]),
        Paragraph(control, styles["ControlBar"]),
        table,
        PageBreak(),
    ]


def build() -> Path:
    styles = build_styles()
    doc_map = {d["id"]: d for d in SAMPLE_DOCUMENTS}
    story: list = []

    # Cover
    story.append(Spacer(1, 50 * mm))
    story.append(Paragraph("SAMIAA LEARNING | RAG CHUNKING LAB", styles["CoverSub"]))
    story.append(Spacer(1, 8 * mm))
    story.append(
        Paragraph("Chunking Strategies<br/>Side-by-Side Guide", styles["CoverTitle"])
    )
    story.append(Spacer(1, 8 * mm))
    story.append(
        Paragraph(
            "Printable companion matching the Chunking Lab UI.<br/>"
            "Source document (left) * Chunks (right) * Same layout as the app.",
            styles["CoverSub"],
        )
    )
    story.append(PageBreak())

    # How to read
    story.append(Paragraph("How to read this guide", styles["PageTitle"]))
    story.append(
        Paragraph(
            "<b>LEFT</b> - Source document with color-coded highlights. "
            "Each color = one chunk.<br/><br/>"
            "<b>RIGHT</b> - Chunk cards with ID, labels, embedded status, char positions.<br/><br/>"
            "<b>Parent-child</b> pages show Parents (not embedded) and Children (embedded) separately.<br/><br/>"
            "Open the app: <font face='Courier'>cd frontend && npm run dev</font> "
            "-> http://localhost:5173",
            styles["Body"],
        )
    )
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("<b>Strategies covered</b>", styles["Body"]))
    for key, (label, desc) in STRATEGY_INFO.items():
        story.append(Paragraph(f"&#8226; <b>{esc(label)}</b> - {esc(desc)}", styles["Body"]))
    story.append(PageBreak())

    demos = [
        ("1. Recursive - Employee Handbook", "employee_handbook", "recursive",
         "Chunk size: 280 chars", {"chunk_size": 280}),
        ("2. Fixed-size - Employee Handbook (compare cuts)", "employee_handbook", "fixed-size",
         "Chunk size: 280 chars - notice mid-section cuts vs recursive", {"chunk_size": 280}),
        ("3. Parent-child - Employee Handbook", "employee_handbook", "parent-child", "", {}),
        ("4. Semantic - Employee Handbook", "employee_handbook", "semantic",
         "Similarity threshold: 0.25", {"similarity_threshold": 0.25}),
        ("5. Proposition - Benefits Policy", "benefits_policy", "proposition", "", {}),
        ("6. Fixed-size - Benefits Policy (compare)", "benefits_policy", "fixed-size",
         "Chunk size: 200 - multiple facts in one chunk", {"chunk_size": 200}),
        ("7. Semantic - Company Update (3 topics)", "company_update", "semantic",
         "Similarity threshold: 0.25 - launch / pricing / hiring", {"similarity_threshold": 0.25}),
        ("8. Fixed-size - Company Update (compare)", "company_update", "fixed-size",
         "Chunk size: 280 - topics may mix in one chunk", {"chunk_size": 280}),
        ("9. Overlap - Security FAQ", "security_faq", "overlap",
         "Chunk size: 200 * Overlap: 15%", {"chunk_size": 200, "overlap_pct": 15}),
    ]

    for title, doc_id, strategy, note, opts in demos:
        doc = dict(doc_map[doc_id])
        doc["content"] = PDF_EXCERPTS.get(doc_id, doc["content"])
        chunks = chunk_document(
            doc["content"],
            strategy,
            chunk_size=opts.get("chunk_size", 280),
            overlap_pct=opts.get("overlap_pct", 15),
            similarity_threshold=opts.get("similarity_threshold", 0.25),
            subject=doc["title"],
        )
        story.extend(side_by_side_flow(styles, title, doc, strategy, chunks, note))

    # Parent-child reference
    story.append(Paragraph("Parent-child: what gets embedded?", styles["PageTitle"]))
    ref_table = Table(
        [
            ["Piece", "Embedded?", "Stored where", "Used for"],
            ["Child (sentence)", "Yes", "Vector DB (later)", "Search"],
            ["Parent (section)", "No", "DB / doc store", "LLM context"],
        ],
        colWidths=[45 * mm, 25 * mm, 45 * mm, 45 * mm],
    )
    ref_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), TEAL),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
            ]
        )
    )
    story.append(ref_table)
    story.append(Spacer(1, 6 * mm))
    story.append(
        Paragraph(
            "<b>Retrieval flow:</b> Query -> search children -> read parent_id -> "
            "fetch parent text -> send to LLM<br/>"
            "<b>Mental model:</b> children = search snippets * parent = full page you open after the match",
            styles["Body"],
        )
    )
    story.append(PageBreak())

    # Comparison
    story.append(Paragraph("Strategy comparison", styles["PageTitle"]))
    cmp_table = Table(
        [
            ["Strategy", "Precision", "Context", "Best fit"],
            ["Fixed-size", "Medium", "Variable", "Prototypes, flat text"],
            ["Overlap", "Higher", "Better", "Narrative, policies"],
            ["Recursive", "High", "High", "Structured docs"],
            ["Semantic", "High", "High", "Mixed topics"],
            ["Parent-child", "Very high", "Very high", "Long manuals"],
            ["Proposition", "Very high", "Focused", "Factoid Q&A"],
        ],
        colWidths=[40 * mm, 28 * mm, 28 * mm, 60 * mm],
    )
    cmp_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), TEAL),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PAPER]),
            ]
        )
    )
    story.append(cmp_table)

    def add_page_num(canvas, doc_):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(MUTED)
        canvas.drawCentredString(
            landscape(A4)[0] / 2, 10 * mm,
            f"RAG Chunking Lab Guide  |  Page {canvas.getPageNumber()}",
        )
        canvas.restoreState()

    pdf = SimpleDocTemplate(
        str(OUT),
        pagesize=landscape(A4),
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="RAG Chunking Lab Guide",
    )
    pdf.build(story, onFirstPage=add_page_num, onLaterPages=add_page_num)
    return OUT


if __name__ == "__main__":
    path = build()
    print(f"Wrote PDF -> {path}")
