#!/usr/bin/env python3
"""Export RAG Chunking Strategies deck to PDF (matches PPTX content)."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

OUT = Path(__file__).resolve().parent / "RAG_Chunking_Strategies.pdf"

SW = 13.333 * inch
SH = 7.5 * inch

INK = colors.HexColor("#141e2a")
INK_SOFT = colors.HexColor("#1e2c3c")
TEAL = colors.HexColor("#0c7c7c")
TEAL_LIGHT = colors.HexColor("#e6f4f4")
PAPER = colors.HexColor("#f8f6f3")
WHITE = colors.white
MUTED = colors.HexColor("#5a6675")
DANGER = colors.HexColor("#b53a3a")
OK = colors.HexColor("#2e7d4f")
ACCENT = colors.HexColor("#d47a2a")
LIGHT_TEXT = colors.HexColor("#b8c4d0")


def T(s: str) -> str:
    return (
        s.replace("\u2014", "-")
        .replace("\u2013", "-")
        .replace("\u2192", "->")
        .replace("\u00b7", " * ")
        .replace("\u2019", "'")
        .replace("\u2713", "Y")
        .replace("\u2717", "X")
    )


class Deck:
    def __init__(self, path: Path):
        self.c = canvas.Canvas(str(path), pagesize=(SW, SH))
        self.page = 0
        self.total = 32

    def save(self):
        self.c.save()

    def _footer(self):
        if 0 < self.page < self.total:
            self.c.setFont("Helvetica", 9)
            self.c.setFillColor(MUTED)
            self.c.drawString(0.55 * inch, 0.35 * inch, "RAG * Chunking Strategies")
            self.c.drawRightString(SW - 0.55 * inch, 0.35 * inch, f"{self.page}  /  {self.total}")

    def slide(self, bg=PAPER, dark=False):
        if self.page > 0:
            self.c.showPage()
        self.page += 1
        self.c.setFillColor(bg)
        self.c.rect(0, 0, SW, SH, fill=1, stroke=0)
        if not dark:
            self.c.setFillColor(TEAL)
            self.c.rect(0, 0, 0.18 * inch, SH, fill=1, stroke=0)
        self._footer()

    def title_block(self, title: str, subtitle: str = ""):
        self.c.setFont("Helvetica-Bold", 10)
        self.c.setFillColor(TEAL)
        self.c.drawString(0.55 * inch, SH - 0.55 * inch, T("RAG TEACHING SERIES"))
        self.c.setFont("Helvetica-Bold", 28)
        self.c.setFillColor(INK)
        self.c.drawString(0.55 * inch, SH - 1.05 * inch, T(title))
        if subtitle:
            self.c.setFont("Helvetica", 14)
            self.c.setFillColor(MUTED)
            self.c.drawString(0.55 * inch, SH - 1.45 * inch, T(subtitle))

    def text(self, x, y, text, size=12, bold=False, color=INK, font="Helvetica"):
        self.c.setFont(f"{font}-Bold" if bold else font, size)
        self.c.setFillColor(color)
        for line in T(text).split("\n"):
            self.c.drawString(x, y, line)
            y -= size + 4
        return y

    def bullets(self, x, y, items, size=11, color=INK, spacing=16):
        for item in items:
            self.text(x, y, f"-  {item}", size=size, color=color)
            y -= spacing
        return y

    def box(self, x, y, w, h, fill=WHITE, stroke=None):
        self.c.setFillColor(fill)
        if stroke:
            self.c.setStrokeColor(stroke)
            self.c.roundRect(x, y, w, h, 8, fill=1, stroke=1)
        else:
            self.c.roundRect(x, y, w, h, 8, fill=1, stroke=0)

    def table(self, x, y, headers, rows, col_w, row_h=22):
        for i, h in enumerate(headers):
            self.c.setFillColor(INK)
            self.c.rect(x + sum(col_w[:i]), y, col_w[i], row_h, fill=1, stroke=0)
            self.c.setFillColor(WHITE)
            self.c.setFont("Helvetica-Bold", 9)
            self.c.drawString(x + sum(col_w[:i]) + 4, y + 6, T(h)[:28])
        for r, row in enumerate(rows):
            ry = y - (r + 1) * row_h
            bg = WHITE if r % 2 == 0 else TEAL_LIGHT
            for i, cell in enumerate(row):
                self.c.setFillColor(bg)
                self.c.rect(x + sum(col_w[:i]), ry, col_w[i], row_h, fill=1, stroke=0)
                self.c.setFillColor(INK)
                self.c.setFont("Helvetica-Bold" if i == 0 else "Helvetica", 8)
                self.c.drawString(x + sum(col_w[:i]) + 4, ry + 6, T(str(cell))[:32])


def build() -> Path:
    d = Deck(OUT)

    # 1 Title
    d.slide(bg=INK, dark=True)
    d.c.setFillColor(TEAL)
    d.c.rect(0, 0, 0.25 * inch, SH, fill=1, stroke=0)
    d.text(0.7 * inch, 5.2 * inch, "TEACHING SERIES * INTRO TO AI SYSTEMS", 11, bold=True, color=TEAL)
    d.text(0.7 * inch, 4.5 * inch, "Retrieval-Augmented\nGeneration (RAG)", 36, bold=True, color=WHITE)
    d.text(0.7 * inch, 2.6 * inch, "Focus: Chunking Strategies - with examples & applications", 14, color=LIGHT_TEXT)
    d.text(0.7 * inch, 1.0 * inch, "For builders learning how to ground LLMs in real documents", 11, color=MUTED)

    # 2 Agenda
    d.slide()
    d.title_block("What we'll cover", "A practical path from RAG basics -> chunking craft")
    for i, (num, txt) in enumerate([
        ("01", "What RAG is and why it exists"),
        ("02", "Where chunking sits in the pipeline"),
        ("03", "Six chunking strategies with worked examples"),
        ("04", "How to choose a strategy for your data"),
        ("05", "Real applications + common failure modes"),
    ]):
        y = SH - 2.3 * inch - i * 0.72 * inch
        d.box(0.55 * inch, y, 12.2 * inch, 0.58 * inch)
        d.text(0.85 * inch, y + 0.2 * inch, num, 18, bold=True, color=TEAL)
        d.text(2.0 * inch, y + 0.18 * inch, txt, 14)

    # 3 What is RAG
    d.slide()
    d.title_block("What is RAG?", "Retrieve -> Augment -> Generate")
    for i, (t, b) in enumerate([
        ("1. Retrieve", "Search your knowledge base for passages related to the user question."),
        ("2. Augment", "Insert those passages into the LLM prompt as grounded context."),
        ("3. Generate", "The model answers using that context - not only its training memory."),
    ]):
        x = 0.55 * inch + i * 4.15 * inch
        y = SH - 2.5 * inch
        d.box(x, y, 3.9 * inch, 3.2 * inch)
        d.c.setFillColor(TEAL)
        d.c.rect(x, y + 3.08 * inch, 3.9 * inch, 0.12 * inch, fill=1, stroke=0)
        d.text(x + 0.2 * inch, y + 2.6 * inch, t, 16, bold=True, color=TEAL)
        d.text(x + 0.2 * inch, y + 2.1 * inch, b, 11, color=INK)

    # 4 Why RAG
    d.slide()
    d.title_block("Why RAG? LLMs alone are not enough", "Chunking only matters because retrieval quality decides answer quality")
    problems = [
        ("Hallucinations", "Models invent confident-sounding facts when knowledge is missing."),
        ("Stale knowledge", "Training cutoffs miss policies, prices, and last week's docs."),
        ("Private data", "Company wikis, tickets, and PDFs are never in the base model."),
        ("Citations", "Users need sources - RAG returns passages you can show."),
    ]
    for i, (t, b) in enumerate(problems):
        col, row = i % 2, i // 2
        x = 0.55 * inch + col * 6.3 * inch
        y = SH - 2.4 * inch - row * 1.9 * inch
        d.box(x, y, 6.0 * inch, 1.65 * inch)
        d.text(x + 0.25 * inch, y + 1.15 * inch, t, 14, bold=True)
        d.text(x + 0.25 * inch, y + 0.75 * inch, b, 10, color=MUTED)

    # 5 Pipeline
    d.slide()
    d.title_block("The RAG pipeline - and where chunking lives", "Indexing once; retrieval + generation per query")
    stages = [
        ("Documents", "PDFs, HTML, MD"),
        ("Chunk", "Split into units"),
        ("Embed", "Vectors + metadata"),
        ("Store", "Vector DB"),
        ("Retrieve", "Top-k for query"),
        ("Answer", "LLM + context"),
    ]
    for i, (t, b) in enumerate(stages):
        x = 0.4 * inch + i * 2.1 * inch
        y = SH - 3.0 * inch
        fill = TEAL if t == "Chunk" else WHITE
        tc = WHITE if t == "Chunk" else INK
        d.box(x, y, 1.85 * inch, 2.4 * inch, fill=fill)
        d.text(x + 0.1 * inch, y + 1.9 * inch, t, 11, bold=True, color=tc)
        d.text(x + 0.1 * inch, y + 1.5 * inch, b, 9, color=tc if t == "Chunk" else MUTED)
    d.box(0.55 * inch, 1.2 * inch, 12.2 * inch, 0.7 * inch, fill=TEAL_LIGHT)
    d.text(0.85 * inch, 1.45 * inch, "Teaching focus: Chunk is the design decision that makes or breaks retrieval.", 12, bold=True)

    # 6 Why chunking
    d.slide()
    d.title_block("Why chunking matters", "Embeddings retrieve chunks - not whole books")
    for title, items, col, bar in [
        ("Too large", ["Dilutes embedding signal", "Retrieves irrelevant text", "Burns context tokens", "Harder to focus"], 0.55, DANGER),
        ("Too small", ["Splits mid-idea", "Loses context", "Needs more chunks", "Noisy ranking"], 6.85, ACCENT),
    ]:
        x = col * inch
        y = SH - 2.5 * inch
        d.box(x, y, 5.9 * inch, 3.8 * inch)
        d.c.setFillColor(bar)
        d.c.rect(x, y + 3.68 * inch, 5.9 * inch, 0.1 * inch, fill=1, stroke=0)
        d.text(x + 0.3 * inch, y + 3.2 * inch, title, 16, bold=True, color=bar)
        d.bullets(x + 0.25 * inch, y + 2.7 * inch, items, 11)

    # 7 Strategy map
    d.slide()
    d.title_block("Six chunking strategies we'll unpack", "From simplest to more structure-aware")
    strats = [
        ("01", "Fixed-size", "Char / token windows"),
        ("02", "Overlap", "Sliding window"),
        ("03", "Recursive", "Headings & structure"),
        ("04", "Semantic", "Meaning shifts"),
        ("05", "Parent-child", "Search small, read large"),
        ("06", "Proposition", "Atomic facts"),
    ]
    for i, (n, t, b) in enumerate(strats):
        col, row = i % 3, i // 3
        x = 0.55 * inch + col * 4.2 * inch
        y = SH - 2.4 * inch - row * 2.0 * inch
        d.box(x, y, 3.95 * inch, 1.75 * inch)
        d.text(x + 0.2 * inch, y + 1.25 * inch, n, 14, bold=True, color=TEAL)
        d.text(x + 0.2 * inch, y + 0.95 * inch, t, 14, bold=True)
        d.text(x + 0.2 * inch, y + 0.65 * inch, b, 10, color=MUTED)

    # 8 Fixed-size
    d.slide()
    d.title_block("01 * Fixed-size chunking", "Split every N characters or tokens")
    d.box(0.55 * inch, SH - 5.0 * inch, 7.6 * inch, 3.8 * inch)
    d.text(0.9 * inch, SH - 2.5 * inch, "How it works", 12, bold=True, color=TEAL)
    d.bullets(0.85 * inch, SH - 2.9 * inch, [
        "Choose size: e.g. 500-1000 tokens",
        "Walk through document sequentially",
        "Break on whitespace near the limit",
        "Store chunk_id, source, offsets as metadata",
    ], 10)
    d.box(8.4 * inch, SH - 5.0 * inch, 4.35 * inch, 3.8 * inch, fill=INK)
    d.text(8.7 * inch, SH - 2.4 * inch, "Best for", 11, bold=True, color=TEAL)
    d.bullets(8.65 * inch, SH - 2.8 * inch, ["Homogeneous text", "Quick prototypes", "Weak structure"], 10, color=WHITE)

    # 9 Fixed example
    d.slide()
    d.title_block("Example * Fixed-size on a policy doc", "Size ~80 tokens, no overlap")
    d.box(0.55 * inch, SH - 2.6 * inch, 12.2 * inch, 1.1 * inch, fill=TEAL_LIGHT)
    src = "Employees may work remotely up to three days per week. Managers must approve schedules by Friday. Equipment stipends are $500 per year. Security training is mandatory before access is granted."
    d.text(0.85 * inch, SH - 2.15 * inch, "SOURCE PARAGRAPH", 9, bold=True, color=TEAL)
    d.text(0.85 * inch, SH - 2.45 * inch, src, 10)
    for i, (t, b) in enumerate([
        ("Chunk A", "Employees may work remotely... Managers must approve schedules by Friday."),
        ("Chunk B", "Equipment stipends are $500 per year. Security training is mandatory..."),
    ]):
        x = 0.55 * inch + i * 6.3 * inch
        d.box(x, SH - 4.4 * inch, 6.0 * inch, 1.8 * inch)
        d.text(x + 0.25 * inch, SH - 3.0 * inch, t, 11, bold=True, color=TEAL)
        d.text(x + 0.25 * inch, SH - 3.5 * inch, b, 10)

    # 10 Overlap
    d.slide()
    d.title_block("02 * Overlapping / sliding window", "Carry last N tokens into next chunk")
    d.box(0.55 * inch, SH - 5.0 * inch, 6.0 * inch, 3.8 * inch)
    d.text(0.9 * inch, SH - 2.4 * inch, "Why overlap?", 13, bold=True, color=TEAL)
    d.bullets(0.85 * inch, SH - 2.8 * inch, [
        "Questions span two adjacent chunks",
        "Overlap preserves bridging sentences",
        "Typical overlap: 10-20%",
        "Tradeoff: more storage + duplicates",
    ], 10)
    d.box(6.85 * inch, SH - 5.0 * inch, 5.9 * inch, 3.8 * inch, fill=INK)
    d.text(7.2 * inch, SH - 2.4 * inch, "Visual", 11, bold=True, color=TEAL)
    d.text(7.2 * inch, SH - 3.0 * inch, "Chunk 1 .......... [overlap]", 10, color=WHITE)
    d.text(8.5 * inch, SH - 3.6 * inch, "[overlap] .......... Chunk 2", 10, color=WHITE)

    # 11 Overlap example
    d.slide()
    d.title_block("Example * Overlap saves a multi-hop fact", 'Query: "Stipend + who approves remote days?"')
    d.box(0.55 * inch, SH - 2.5 * inch, 12.2 * inch, 0.85 * inch, fill=TEAL_LIGHT)
    d.text(0.85 * inch, SH - 2.15 * inch, "Without overlap, stipend and approval may land in different chunks.", 10)
    d.box(0.55 * inch, SH - 4.5 * inch, 6.0 * inch, 1.8 * inch)
    d.text(0.85 * inch, SH - 3.1 * inch, "Chunk 1 (with overlap)", 10, bold=True, color=TEAL)
    d.text(0.85 * inch, SH - 3.5 * inch, "...Managers must approve... Equipment stipends are $500 per year...", 10)
    d.box(6.85 * inch, SH - 4.5 * inch, 5.9 * inch, 1.8 * inch)
    d.bullets(7.1 * inch, SH - 3.1 * inch, [
        "Approval + stipend co-occur",
        "Single retrieval answers full question",
        'Fewer "only found half" failures',
    ], 10)

    # 12 Recursive
    d.slide()
    d.title_block("03 * Recursive / structure-aware", "Headings -> paragraphs -> sentences -> chars")
    d.box(0.55 * inch, SH - 5.0 * inch, 7.5 * inch, 3.8 * inch)
    d.bullets(0.85 * inch, SH - 2.5 * inch, [
        "1. Split on headings / markdown #",
        "2. If too big -> split on paragraphs",
        "3. Then sentences",
        "4. Last resort -> characters",
    ], 11)
    d.box(8.3 * inch, SH - 5.0 * inch, 4.45 * inch, 3.8 * inch, fill=INK)
    d.text(8.65 * inch, SH - 2.4 * inch, "Best for", 11, bold=True, color=TEAL)
    d.bullets(8.6 * inch, SH - 2.8 * inch, ["Docs with headings", "Markdown / Confluence", "API references", "Handbooks"], 10, color=WHITE)

    # 13 Recursive example
    d.slide()
    d.title_block("Example * Recursive keeps sections intact", "Bad: cut mid-section * Good: one chunk per heading")
    d.box(0.55 * inch, SH - 4.8 * inch, 5.9 * inch, 3.5 * inch)
    d.c.setFillColor(DANGER)
    d.c.rect(0.55 * inch, SH - 1.5 * inch, 5.9 * inch, 0.08 * inch, fill=1, stroke=0)
    d.text(0.9 * inch, SH - 2.0 * inch, "Naive fixed cut", 12, bold=True, color=DANGER)
    d.text(0.9 * inch, SH - 2.6 * inch, "## Refunds\n...\n## Shipping\nOrders ship within... [cut]", 10)
    d.box(6.85 * inch, SH - 4.8 * inch, 5.9 * inch, 3.5 * inch)
    d.c.setFillColor(OK)
    d.c.rect(6.85 * inch, SH - 1.5 * inch, 5.9 * inch, 0.08 * inch, fill=1, stroke=0)
    d.text(7.2 * inch, SH - 2.0 * inch, "Recursive", 12, bold=True, color=OK)
    d.text(7.2 * inch, SH - 2.6 * inch, "Chunk 1: ## Refunds + body\nChunk 2: ## Shipping + body", 10)

    # 14 Semantic
    d.slide()
    d.title_block("04 * Semantic chunking", "Split when meaning shifts - not when counter hits N")
    d.box(0.55 * inch, SH - 2.5 * inch, 12.2 * inch, 0.9 * inch, fill=TEAL_LIGHT)
    d.text(0.85 * inch, SH - 2.1 * inch, "Embed sentences. When similarity drops below threshold, start new chunk.", 11)
    cols = [("Idea", "Topic coherence"), ("Cost", "Extra embedding passes"), ("Win", "Mixed / narrative docs"), ("Watch", "Threshold tuning")]
    for i, (t, b) in enumerate(cols):
        x = 0.55 * inch + i * 3.15 * inch
        d.box(x, SH - 4.8 * inch, 3.0 * inch, 1.8 * inch)
        d.text(x + 0.15 * inch, SH - 3.3 * inch, t, 11, bold=True, color=TEAL)
        d.text(x + 0.15 * inch, SH - 3.7 * inch, b, 10)

    # 15 Semantic example
    d.slide()
    d.title_block("Example * Semantic split on a blog post", "One article, three topics -> three chunks")
    for i, (t, b) in enumerate([
        ("Chunk A * Product launch", "We shipped v2.0 with offline sync..."),
        ("Chunk B * Pricing change", "Starting May 1, Pro is $29/mo..."),
        ("Chunk C * Hiring", "We're hiring two backend engineers..."),
    ]):
        y = SH - 2.3 * inch - i * 1.35 * inch
        d.box(0.55 * inch, y, 12.2 * inch, 1.1 * inch)
        d.c.setFillColor(TEAL)
        d.c.rect(0.55 * inch, y + 0.95 * inch, 0.12 * inch, 0.15 * inch, fill=1, stroke=0)
        d.text(1.0 * inch, y + 0.65 * inch, t, 12, bold=True)
        d.text(1.0 * inch, y + 0.35 * inch, b, 10, color=MUTED)

    # 16 Parent-child intro
    d.slide()
    d.title_block("05 * Parent-child (small-to-big)", "Retrieve precise children; expand to parent for generation")
    d.box(0.55 * inch, SH - 5.0 * inch, 6.0 * inch, 3.8 * inch)
    d.bullets(0.85 * inch, SH - 2.5 * inch, [
        "Child: small for accurate search",
        "Parent: section for rich LLM context",
        "On hit: fetch parent_id -> inject parent",
        "Also: hierarchical / multi-granularity RAG",
    ], 10)
    d.box(6.85 * inch, SH - 5.0 * inch, 5.9 * inch, 3.8 * inch, fill=INK)
    d.text(7.2 * inch, SH - 2.4 * inch, "PARENT: Section 3 Security Policy", 10, bold=True, color=TEAL)
    for i, lbl in enumerate(["Child 3.1 MFA required", "Child 3.2 VPN only", "Child 3.3 Device wipe"]):
        d.text(7.6 * inch, SH - 3.0 * inch - i * 0.45 * inch, lbl, 9, color=WHITE)

    # 17 Proposition intro
    d.slide()
    d.title_block("06 * Proposition / atomic chunking", "Rewrite text into standalone facts, then embed each")
    d.box(0.55 * inch, SH - 2.5 * inch, 12.2 * inch, 0.95 * inch, fill=TEAL_LIGHT)
    d.text(0.85 * inch, SH - 2.1 * inch, 'Use LLM to extract self-contained facts (no "it / this"). Great for dense reports.', 11)
    d.box(0.55 * inch, SH - 4.6 * inch, 5.9 * inch, 1.8 * inch)
    d.text(0.9 * inch, SH - 3.2 * inch, "Original", 10, bold=True, color=MUTED)
    d.text(0.9 * inch, SH - 3.6 * inch, "Acme Plan covers dental after 6-month wait and vision after 90 days for full-time staff.", 10)
    d.box(6.85 * inch, SH - 4.6 * inch, 5.9 * inch, 1.8 * inch)
    d.text(7.2 * inch, SH - 3.2 * inch, "Propositions", 10, bold=True, color=TEAL)
    d.bullets(7.15 * inch, SH - 3.6 * inch, ["Dental after 6 months", "Vision after 90 days", "Full-time staff only"], 10)

    # 18 Parent-child why
    d.slide()
    d.title_block("Parent-child * Why it exists", "Stuck between two bad options - use both on purpose")
    for col, title, items, bar in [(0.55, "Big chunks", ["Easy to find topic", "Noisy embedding", "Too much context for LLM"], DANGER),
                                    (6.85, "Small chunks", ["Precise match", '"It expires" - what is it?', "Missing exceptions"], ACCENT)]:
        x = col * inch
        y = SH - 2.5 * inch
        d.box(x, y, 5.9 * inch, 3.5 * inch)
        d.c.setFillColor(bar)
        d.c.rect(x, y + 3.38 * inch, 5.9 * inch, 0.1 * inch, fill=1, stroke=0)
        d.text(x + 0.3 * inch, y + 2.95 * inch, title, 12, bold=True, color=bar)
        d.bullets(x + 0.25 * inch, y + 2.5 * inch, items, 10)
    d.box(0.55 * inch, 1.15 * inch, 12.2 * inch, 0.5 * inch, fill=TEAL_LIGHT)
    d.text(0.85 * inch, 1.35 * inch, "Fix: search with small children * answer with full parent section", 11, bold=True, color=TEAL)

    # 19 Parent-child example
    d.slide()
    d.title_block("Parent-child * Worked example", "Handbook Section 3 Remote Work - 1 parent, 4 children")
    d.box(0.55 * inch, SH - 2.5 * inch, 12.2 * inch, 1.2 * inch, fill=INK)
    d.text(0.85 * inch, SH - 2.15 * inch, "PARENT (not embedded)", 9, bold=True, color=TEAL)
    d.text(0.85 * inch, SH - 2.45 * inch, "Section 3: 3 days remote * approval by Friday * $500 stipend * security training", 10, color=WHITE)
    d.table(0.55 * inch, SH - 3.0 * inch, ["Child", "Embedded text", "parent_id"], [
        ["C1", "Remote work up to 3 days/week", "S3"],
        ["C2", "Manager approval by Friday", "S3"],
        ["C3", "Equipment stipend $500/year", "S3"],
        ["C4", "Security training before VPN", "S3"],
    ], [100, 280, 80])

    # 20 Parent-child flow
    d.slide()
    d.title_block('Parent-child * Retrieval flow', 'Query: "How much is the equipment stipend?"')
    for i, (n, t, det) in enumerate([
        ("1", "User question", "How much is the equipment stipend?"),
        ("2", "Vector search", "Matches child C3"),
        ("3", "Read parent_id", "C3 -> parent Section 3"),
        ("4", "Fetch parent", "Load full section into prompt"),
        ("5", "LLM answer", '"$500 per year"'),
    ]):
        y = SH - 2.2 * inch - i * 0.82 * inch
        d.box(0.55 * inch, y, 12.2 * inch, 0.68 * inch)
        d.c.setFillColor(TEAL)
        d.c.circle(0.95 * inch, y + 0.34 * inch, 0.18 * inch, fill=1, stroke=0)
        d.text(0.88 * inch, y + 0.28 * inch, n, 9, bold=True, color=WHITE)
        d.text(1.55 * inch, y + 0.35 * inch, t, 11, bold=True, color=TEAL)
        d.text(3.9 * inch, y + 0.35 * inch, det, 10)

    # 21 What gets embedded
    d.slide()
    d.title_block("Parent-child * What gets embedded?", "Embed children only * store parents as linked text")
    d.table(0.55 * inch, SH - 2.3 * inch, ["Piece", "Embedded?", "Stored where", "Used for"], [
        ["Child (sentence)", "Yes", "Vector DB", "Search"],
        ["Parent (section)", "No", "DB / doc store", "LLM context"],
    ], [200, 80, 120, 160])
    d.box(0.55 * inch, SH - 4.0 * inch, 12.2 * inch, 0.45 * inch, fill=TEAL_LIGHT)
    d.text(0.85 * inch, SH - 3.75 * inch, "Why not embed parents? Duplicate results, noisier search, unclear LLM input", 10)
    d.box(0.55 * inch, SH - 5.5 * inch, 6.0 * inch, 1.8 * inch)
    d.text(0.9 * inch, SH - 4.1 * inch, "Index time", 11, bold=True, color=TEAL)
    d.bullets(0.85 * inch, SH - 4.5 * inch, ["Save parent as text + parent_id", "Embed children with parent_id", "Parent not in vector index"], 9)
    d.box(6.85 * inch, SH - 5.5 * inch, 5.9 * inch, 1.8 * inch)
    d.text(7.2 * inch, SH - 4.1 * inch, "Query time", 11, bold=True, color=TEAL)
    d.bullets(7.15 * inch, SH - 4.5 * inch, ["Search children only", "Hit C3 -> fetch parent", "Send parent to LLM"], 9)

    # 22 Proposition why
    d.slide()
    d.title_block("Proposition * Why it exists", "Multiple facts and vague pronouns in one embedding")
    d.box(0.55 * inch, SH - 4.8 * inch, 6.0 * inch, 2.0 * inch)
    d.bullets(0.85 * inch, SH - 3.3 * inch, ["Several facts in one paragraph", 'Pronouns ("it") embed poorly', "User gets 3 unrelated facts"], 10)
    d.box(0.55 * inch, SH - 2.5 * inch, 6.0 * inch, 0.75 * inch, fill=TEAL_LIGHT)
    d.text(0.9 * inch, SH - 2.15 * inch, "Fix: one standalone fact per chunk", 11, bold=True, color=TEAL)
    d.box(6.85 * inch, SH - 4.8 * inch, 5.9 * inch, 3.5 * inch)
    for i, (m, t, c) in enumerate([
        ("X", "It covers dental after 6 months.", DANGER),
        ("Y", "Acme Plan covers dental after 6-month wait.", OK),
        ("X", "Vision is after 90 days for FT staff.", DANGER),
        ("Y", "Acme Plan covers vision after 90 days.", OK),
    ]):
        d.text(7.2 * inch, SH - 2.5 * inch - i * 0.55 * inch, f"{m}  {t}", 9, color=c)

    # 23 Proposition example
    d.slide()
    d.title_block('Proposition * Worked example', 'Query: "When does vision coverage start?"')
    d.box(0.55 * inch, SH - 2.5 * inch, 5.9 * inch, 1.1 * inch)
    d.text(0.9 * inch, SH - 2.15 * inch, "Original paragraph", 9, bold=True, color=MUTED)
    d.text(0.9 * inch, SH - 2.45 * inch, "Acme Plan covers dental after 6-month wait and vision after 90 days for full-time staff.", 9)
    props = ["P1: Dental after 6-month wait", "P2: Vision after 90-day wait", "P3: Full-time status required"]
    d.box(6.85 * inch, SH - 4.5 * inch, 5.9 * inch, 2.8 * inch)
    for i, p in enumerate(props):
        d.box(7.15 * inch, SH - 2.6 * inch - i * 0.75 * inch, 5.4 * inch, 0.6 * inch, fill=TEAL_LIGHT if i == 1 else WHITE)
        d.text(7.35 * inch, SH - 2.35 * inch - i * 0.75 * inch, p, 9, bold=(i == 1))
    d.box(0.55 * inch, SH - 4.8 * inch, 5.9 * inch, 2.5 * inch, fill=INK)
    d.text(0.9 * inch, SH - 3.0 * inch, "Retrieval returns P2 only", 10, bold=True, color=TEAL)
    d.bullets(0.85 * inch, SH - 3.4 * inch, ["Not P1 or P3 - less noise", 'Answer: "90 days"', "Fixed chunking returns whole paragraph"], 9, color=WHITE)

    # 24 Comparison
    d.slide()
    d.title_block("Strategy comparison at a glance", "Pick for quality first - optimize cost second")
    d.table(0.55 * inch, SH - 2.4 * inch, ["Strategy", "Precision", "Context", "Cost", "Best fit"], [
        ["Fixed-size", "Medium", "Variable", "Low", "Prototypes"],
        ["Overlap", "Higher", "Better", "Low+", "Policies"],
        ["Recursive", "High", "High", "Low", "Structured docs"],
        ["Semantic", "High", "High", "Med", "Mixed topics"],
        ["Parent-child", "Very high", "Very high", "Med", "Long manuals"],
        ["Proposition", "Very high", "Low-expand", "High", "Factoid Q&A"],
    ], [110, 70, 70, 55, 150])

    # 25 Decision guide
    d.slide()
    d.title_block("How to choose a strategy", "Start simple; upgrade when retrieval evals fail")
    for i, (q, a) in enumerate([
        ("Most docs have headings?", "-> Recursive (+ overlap)"),
        ("Long chapters, precise Qs?", "-> Parent-child"),
        ("Mixed topics in one file?", "-> Semantic"),
        ("Need exact factual answers?", "-> Proposition"),
        ("Shipping MVP this week?", "-> Fixed-size + 10-15% overlap"),
    ]):
        y = SH - 2.3 * inch - i * 0.72 * inch
        d.box(0.55 * inch, y, 12.2 * inch, 0.58 * inch)
        d.text(0.9 * inch, y + 0.18 * inch, q, 12, bold=True)
        d.text(7.5 * inch, y + 0.18 * inch, a, 12, color=TEAL)

    # 26 Applications
    d.slide()
    d.title_block("Applications * where chunking shows up", "Same RAG idea - different chunk designs")
    apps = [
        ("Customer support", "Recursive + overlap", "Cite article section"),
        ("Legal / compliance", "Parent-child", "Clause hits + context"),
        ("Codebase assistant", "Function / class chunks", "Don't split mid-function"),
        ("Research / papers", "Semantic by section", "Methods vs results"),
        ("HR policies", "Recursive + proposition", "Benefits factoid Qs"),
        ("Internal search", "Fixed + metadata", "Hybrid keyword + vector"),
    ]
    for i, (t, how, why) in enumerate(apps):
        col, row = i % 3, i // 3
        x = 0.55 * inch + col * 4.2 * inch
        y = SH - 2.4 * inch - row * 2.0 * inch
        d.box(x, y, 4.0 * inch, 1.75 * inch)
        d.text(x + 0.15 * inch, y + 1.35 * inch, t, 10, bold=True, color=TEAL)
        d.text(x + 0.15 * inch, y + 1.05 * inch, how, 9)
        d.text(x + 0.15 * inch, y + 0.7 * inch, why, 8, color=MUTED)

    # 27 Worked application
    d.slide()
    d.title_block("Worked application * Employee handbook Q&A", "One corpus, three query types")
    d.table(0.55 * inch, SH - 2.5 * inch, ["Query type", "Example", "Chunk strategy"], [
        ["Policy lookup", '"How many remote days?"', "Recursive by section"],
        ["Multi-fact", '"Stipend + approval?"', "Overlap or parent-child"],
        ["Benefits factoid", '"Vision wait period?"', "Proposition chunks"],
    ], [140, 200, 180])

    # 28 Pitfalls
    d.slide()
    d.title_block('Common pitfalls', 'Chunking bugs look like "the model is dumb"')
    pitfalls = [
        ("Ignoring metadata", "Store source, heading, page, timestamps."),
        ("One size for all", "PDFs != chat logs != code."),
        ("No evaluation set", "Build 20-50 questions; measure recall@k."),
        ("Wrong chunking time", "Index-time chunks must match query-time."),
        ("Orphan pronouns", '"It expires in 30 days" without what "it" is.'),
        ("Over-chunking tables", "Keep tables together or summarize."),
    ]
    for i, (t, b) in enumerate(pitfalls):
        col, row = i % 2, i // 2
        x = 0.55 * inch + col * 6.3 * inch
        y = SH - 2.4 * inch - row * 1.4 * inch
        d.box(x, y, 6.05 * inch, 1.2 * inch)
        d.text(x + 0.2 * inch, y + 0.75 * inch, t, 11, bold=True, color=DANGER)
        d.text(x + 0.2 * inch, y + 0.45 * inch, b, 9, color=MUTED)

    # 29 Checklist
    d.slide()
    d.title_block("Teaching checklist * best practices", "Use this as a lab rubric")
    checks = [
        "Match chunk size to embedding model (256-1024 tokens)",
        "Prefer structure-aware splits over blind cuts",
        "Add 10-20% overlap when answers span boundaries",
        "Attach rich metadata for filters and citations",
        "Evaluate with real user questions before tuning",
        "Re-chunk when document structure changes",
        "Log retrieved chunks during demos",
    ]
    for i, c in enumerate(checks):
        y = SH - 2.2 * inch - i * 0.58 * inch
        d.box(0.55 * inch, y, 12.2 * inch, 0.48 * inch)
        d.text(0.85 * inch, y + 0.15 * inch, "Y", 11, bold=True, color=OK)
        d.text(1.5 * inch, y + 0.15 * inch, c, 11)

    # 30 Lab
    d.slide()
    d.title_block("Classroom lab (30-45 min)", "Hands-on: same corpus, competing chunkers")
    for i, (n, t) in enumerate([
        ("1", "Pick a short handbook or README (~5-10 pages)"),
        ("2", "Build three indexes: fixed, recursive, parent-child"),
        ("3", "Write 10 questions (5 easy, 3 multi-hop, 2 adversarial)"),
        ("4", "Score recall@3 and answer correctness"),
        ("5", "Discuss: which strategy won - and why?"),
    ]):
        y = SH - 2.3 * inch - i * 0.72 * inch
        d.box(0.55 * inch, y, 12.2 * inch, 0.58 * inch)
        d.c.setFillColor(TEAL)
        d.c.circle(0.95 * inch, y + 0.29 * inch, 0.16 * inch, fill=1, stroke=0)
        d.text(0.88 * inch, y + 0.22 * inch, n, 9, bold=True, color=WHITE)
        d.text(1.6 * inch, y + 0.18 * inch, t, 12)

    # 31 Takeaways
    d.slide()
    d.title_block("Key takeaways", "What students should leave remembering")
    for i, (t, b) in enumerate([
        ("RAG grounds LLMs", "Retrieve -> Augment -> Generate"),
        ("Chunking is a product decision", "Not just preprocessing"),
        ("Structure beats blind cuts", "Headings, parents, propositions"),
        ("Measure, then upgrade", "Eval questions before fancy chunkers"),
    ]):
        col, row = i % 2, i // 2
        x = 0.55 * inch + col * 6.3 * inch
        y = SH - 2.4 * inch - row * 2.0 * inch
        d.box(x, y, 6.05 * inch, 1.65 * inch)
        d.c.setFillColor(TEAL)
        d.c.rect(x, y + 1.53 * inch, 0.12 * inch, 0.12 * inch, fill=1, stroke=0)
        d.text(x + 0.35 * inch, y + 1.1 * inch, t, 14, bold=True)
        d.text(x + 0.35 * inch, y + 0.7 * inch, b, 11, color=MUTED)

    # 32 Closing
    d.slide(bg=INK, dark=True)
    d.c.setFillColor(TEAL)
    d.c.rect(0, 0, 0.25 * inch, SH, fill=1, stroke=0)
    d.text(0.7 * inch, 4.5 * inch, "NEXT UP", 12, bold=True, color=TEAL)
    d.text(0.7 * inch, 3.6 * inch, "Embeddings, retrieval,\nand evaluation", 32, bold=True, color=WHITE)
    d.text(0.7 * inch, 2.2 * inch, "Questions? Try the lab - then we'll score your chunkers.", 14, color=LIGHT_TEXT)

    d.save()
    return OUT


if __name__ == "__main__":
    p = build()
    print(f"Wrote PDF slides -> {p}")
