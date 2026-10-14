#!/usr/bin/env python3
"""Generate RAG Embeddings & Retrieval teaching deck (with worked examples)."""

from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# --- Palette (match chunking deck) ---
INK = RGBColor(0x14, 0x1E, 0x2A)
INK_SOFT = RGBColor(0x1E, 0x2C, 0x3C)
TEAL = RGBColor(0x0C, 0x7C, 0x7C)
TEAL_LIGHT = RGBColor(0xE6, 0xF4, 0xF4)
PAPER = RGBColor(0xF8, 0xF6, 0xF3)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
MUTED = RGBColor(0x5A, 0x66, 0x75)
ACCENT = RGBColor(0xD4, 0x7A, 0x2A)
DANGER = RGBColor(0xB5, 0x3A, 0x3A)
OK = RGBColor(0x2E, 0x7D, 0x4F)
LIGHT = RGBColor(0xB8, 0xC4, 0xD0)

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)
TOTAL = 34


def set_run(run, size, bold=False, color=INK, font="Calibri"):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = font


def add_text_box(slide, left, top, width, height, text, size=18, bold=False, color=INK, align=PP_ALIGN.LEFT, font="Calibri"):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    set_run(run, size, bold=bold, color=color, font=font)
    return box


def add_bullets(slide, left, top, width, height, items, size=16, color=INK, spacing=10):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.level = 0
        p.space_after = Pt(spacing)
        run = p.add_run()
        run.text = "•  " + item
        set_run(run, size, color=color)
    return box


def fill_shape(shape, color):
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()


def fill_cell(cell, color):
    cell.fill.solid()
    cell.fill.fore_color.rgb = color


def add_rect(slide, left, top, width, height, color):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    fill_shape(shape, color)
    return shape


def add_round_rect(slide, left, top, width, height, color, radius=0.1):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    fill_shape(shape, color)
    try:
        shape.adjustments[0] = radius
    except Exception:
        pass
    return shape


def accent_bar(slide, color=TEAL):
    add_rect(slide, Inches(0), Inches(0), Inches(0.18), SLIDE_H, color)


def footer(slide, page):
    add_text_box(
        slide, Inches(11.4), Inches(7.05), Inches(1.6), Inches(0.35),
        f"{page}  /  {TOTAL}", size=11, color=MUTED, align=PP_ALIGN.RIGHT
    )
    add_text_box(
        slide, Inches(0.55), Inches(7.05), Inches(5), Inches(0.35),
        "RAG · Embeddings & Retrieval", size=11, color=MUTED
    )


def section_label(slide, text, left=Inches(0.55), top=Inches(0.35)):
    add_text_box(slide, left, top, Inches(8), Inches(0.35), text.upper(), size=12, bold=True, color=TEAL)


def title_block(slide, title, subtitle=None):
    section_label(slide, "RAG Teaching Series")
    add_text_box(slide, Inches(0.55), Inches(0.7), Inches(12), Inches(0.7), title, size=30, bold=True, color=INK)
    if subtitle:
        add_text_box(slide, Inches(0.55), Inches(1.35), Inches(12), Inches(0.45), subtitle, size=15, color=MUTED)


def set_bg(slide, color):
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), SLIDE_W, SLIDE_H)
    fill_shape(bg, color)
    spTree = slide.shapes._spTree
    sp = bg._element
    spTree.remove(sp)
    spTree.insert(2, sp)


def add_table(slide, left, top, width, height, headers, rows, col_widths=None):
    cols = len(headers)
    table_shape = slide.shapes.add_table(len(rows) + 1, cols, left, top, width, height)
    table = table_shape.table
    if col_widths:
        for i, w in enumerate(col_widths):
            table.columns[i].width = w
    for i, h in enumerate(headers):
        cell = table.cell(0, i)
        cell.text = h
        for p in cell.text_frame.paragraphs:
            for run in p.runs:
                set_run(run, 11, bold=True, color=WHITE)
        fill_cell(cell, INK)
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            cell = table.cell(r + 1, c)
            cell.text = str(val)
            for p in cell.text_frame.paragraphs:
                for run in p.runs:
                    set_run(run, 11, bold=(c == 0), color=INK)
            fill_cell(cell, TEAL_LIGHT if r % 2 == 1 else WHITE)
    return table_shape


def build():
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H
    blank = prs.slide_layouts[6]
    page = 0

    def next_page():
        nonlocal page
        page += 1
        return page

    # ========== 1. Title ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, INK)
    add_rect(s, Inches(0), Inches(0), Inches(0.25), SLIDE_H, TEAL)
    add_rect(s, Inches(10.5), Inches(0), Inches(2.833), SLIDE_H, INK_SOFT)
    add_text_box(s, Inches(0.7), Inches(1.8), Inches(9), Inches(0.4),
                 "TEACHING SERIES · INTRO TO AI SYSTEMS", size=13, bold=True, color=TEAL)
    add_text_box(s, Inches(0.7), Inches(2.3), Inches(9.5), Inches(1.2),
                 "Retrieval-Augmented\nGeneration (RAG)", size=44, bold=True, color=WHITE)
    add_text_box(s, Inches(0.7), Inches(4.6), Inches(9), Inches(0.5),
                 "Focus: Embeddings & Retrieval — with worked examples", size=18, color=LIGHT)
    add_text_box(s, Inches(0.7), Inches(6.5), Inches(9), Inches(0.4),
                 "Part 2 · After chunking — how search actually finds the right text", size=13, color=MUTED)
    next_page()

    # ========== 2. Agenda ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "What we'll cover", "From vectors → search → better answers")
    items = [
        ("01", "What embeddings are (and a tiny numeric example)"),
        ("02", "Similarity: how \"near\" becomes \"relevant\""),
        ("03", "Indexing: embed chunks, store vectors + metadata"),
        ("04", "Retrieval: dense, hybrid, top-k, rerank — with examples"),
        ("05", "Failure modes, evaluation, and a classroom lab"),
    ]
    for i, (num, text) in enumerate(items):
        y = Inches(2.05) + Inches(i * 0.85)
        add_round_rect(s, Inches(0.55), y, Inches(12.2), Inches(0.72), WHITE)
        add_text_box(s, Inches(0.85), y + Inches(0.15), Inches(1), Inches(0.4), num, size=22, bold=True, color=TEAL)
        add_text_box(s, Inches(2.0), y + Inches(0.18), Inches(10), Inches(0.4), text, size=18, color=INK)
    footer(s, next_page())

    # ========== 3. Bridge from chunking ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Where we left off — and what's next", "Chunking decides the units. Embeddings + retrieval decide which units you get.")
    stages = [
        ("Documents", False),
        ("Chunk", False),
        ("Embed", True),
        ("Store", True),
        ("Retrieve", True),
        ("Answer", False),
    ]
    for i, (t, focus) in enumerate(stages):
        x = Inches(0.4) + Inches(i * 2.15)
        fill = TEAL if focus else WHITE
        tc = WHITE if focus else INK
        add_round_rect(s, x, Inches(2.5), Inches(1.95), Inches(2.0), fill)
        add_text_box(s, x + Inches(0.1), Inches(3.15), Inches(1.75), Inches(0.5), t, size=16, bold=True, color=tc, align=PP_ALIGN.CENTER)
        if i < len(stages) - 1:
            add_text_box(s, x + Inches(1.85), Inches(3.2), Inches(0.35), Inches(0.4), "→", size=20, bold=True, color=TEAL)
    add_round_rect(s, Inches(0.55), Inches(5.0), Inches(12.2), Inches(1.4), TEAL_LIGHT)
    add_text_box(s, Inches(0.85), Inches(5.25), Inches(11.6), Inches(0.9),
                 "Today's focus: turn chunks into vectors, store them, then find the best ones for a question.\n"
                 "Example corpus throughout: Employee Handbook (Remote Work, Benefits, Security).",
                 size=15, bold=True, color=INK)
    footer(s, next_page())

    # ========== 4. What is an embedding ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "What is an embedding?", "A list of numbers that captures meaning — so similar text lands near similar text")
    add_round_rect(s, Inches(0.55), Inches(2.15), Inches(6.0), Inches(4.2), WHITE)
    add_rect(s, Inches(0.55), Inches(2.15), Inches(0.1), Inches(4.2), TEAL)
    add_text_box(s, Inches(0.9), Inches(2.4), Inches(5.4), Inches(0.4), "In plain English", size=18, bold=True, color=TEAL)
    add_bullets(s, Inches(0.85), Inches(3.0), Inches(5.4), Inches(3.0), [
        "Input: a chunk of text (or a query)",
        "Model: an embedding model (not the chat LLM)",
        "Output: a vector, e.g. 384 or 1536 floats",
        "Property: meaning-near ⇒ vector-near",
        "Used for: similarity search, clustering, rerank features",
    ], size=14, spacing=8)

    add_round_rect(s, Inches(6.85), Inches(2.15), Inches(5.9), Inches(4.2), INK)
    add_text_box(s, Inches(7.2), Inches(2.45), Inches(5.3), Inches(0.4), "Mental model", size=16, bold=True, color=TEAL)
    add_text_box(s, Inches(7.2), Inches(3.1), Inches(5.3), Inches(2.8),
                 '"Equipment stipend is $500/year"\n'
                 "         ↓ embed\n"
                 "[ 0.12, -0.44, 0.91, … 0.03 ]\n\n"
                 "Same idea in different words\nlands nearby in that space.",
                 size=14, color=WHITE)
    footer(s, next_page())

    # ========== 5. Toy 2D example ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Example · Tiny 2D embedding space", "x and y here are a teaching picture — not the real embedding format")
    add_text_box(s, Inches(0.55), Inches(1.95), Inches(12.2), Inches(0.35),
                 "Closer points = more related meaning. Search needs coordinates so a computer can rank “near” vs “far.”", size=13, color=MUTED)

    # Hypothetical vs real callout
    add_round_rect(s, Inches(0.55), Inches(2.35), Inches(6.0), Inches(1.55), WHITE)
    add_rect(s, Inches(0.55), Inches(2.35), Inches(0.1), Inches(1.55), ACCENT)
    add_text_box(s, Inches(0.85), Inches(2.5), Inches(5.5), Inches(0.3), "On this slide (hypothetical)", size=13, bold=True, color=ACCENT)
    add_text_box(s, Inches(0.85), Inches(2.9), Inches(5.5), Inches(0.8),
                 "Each sentence is a fake 2D point (x, y)\nso we can draw “near” on a flat map.", size=12, color=INK)

    add_round_rect(s, Inches(6.85), Inches(2.35), Inches(5.9), Inches(1.55), WHITE)
    add_rect(s, Inches(6.85), Inches(2.35), Inches(0.1), Inches(1.55), TEAL)
    add_text_box(s, Inches(7.15), Inches(2.5), Inches(5.4), Inches(0.3), "In real RAG", size=13, bold=True, color=TEAL)
    add_text_box(s, Inches(7.15), Inches(2.9), Inches(5.4), Inches(0.8),
                 "Same idea, many more axes — e.g. 384 or 1536 numbers:\n[0.12, −0.44, 0.91, …]  (you don’t plot these by hand)", size=12, color=INK)

    points = [
        ("A  Remote work: 3 days/week", "Policy", TEAL, 0.55, 4.1),
        ("B  Manager approval by Friday", "Policy", TEAL, 0.55, 4.75),
        ("C  Equipment stipend $500", "Money", ACCENT, 0.55, 5.4),
        ("D  Vision coverage after 90 days", "Benefits", OK, 6.85, 4.1),
        ("E  MFA required for VPN", "Security", DANGER, 6.85, 4.75),
        ("Q  \"How much is the stipend?\"", "Query", INK, 6.85, 5.4),
    ]
    for text, tag, col, x, y in points:
        add_round_rect(s, Inches(x), Inches(y), Inches(5.9), Inches(0.55), WHITE)
        add_rect(s, Inches(x), Inches(y), Inches(0.1), Inches(0.55), col)
        add_text_box(s, Inches(x) + Inches(0.25), Inches(y) + Inches(0.08), Inches(4.2), Inches(0.4), text, size=12, bold=True, color=INK)
        add_text_box(s, Inches(x) + Inches(4.4), Inches(y) + Inches(0.1), Inches(1.3), Inches(0.35), tag, size=11, color=col)

    add_round_rect(s, Inches(0.55), Inches(6.1), Inches(12.2), Inches(0.7), TEAL_LIGHT)
    add_text_box(s, Inches(0.85), Inches(6.25), Inches(11.6), Inches(0.45),
                 "Takeaway: Q should land nearest to C. We need coordinates for search — x,y is just the 2D cartoon of that.", size=13, bold=True, color=INK)
    footer(s, next_page())

    # ========== 5b. Real RAG axes example ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Example · Real RAG axes (1536-D)", "Azure / OpenAI text-embedding-3-small style — first 12 numbers shown; 1524 more exist")
    add_text_box(s, Inches(0.55), Inches(1.95), Inches(12.2), Inches(0.35),
                 "Axes are NOT labeled “money / policy / security.” They are anonymous learned dimensions. Closeness still means related meaning.", size=13, color=MUTED)

    add_round_rect(s, Inches(0.55), Inches(2.4), Inches(12.2), Inches(1.15), INK)
    add_text_box(s, Inches(0.85), Inches(2.55), Inches(11.6), Inches(0.3),
                 'Q  "How much is the equipment stipend?"', size=14, bold=True, color=TEAL)
    add_text_box(s, Inches(0.85), Inches(2.95), Inches(11.6), Inches(0.4),
                 "q = [ 0.041, -0.128, 0.067, 0.203, -0.055, 0.019, 0.144, -0.082, 0.011, 0.176, -0.039, 0.092,  …  ×1524 more ]", size=12, color=WHITE)

    add_round_rect(s, Inches(0.55), Inches(3.75), Inches(12.2), Inches(1.15), WHITE)
    add_rect(s, Inches(0.55), Inches(3.75), Inches(0.1), Inches(1.15), OK)
    add_text_box(s, Inches(0.85), Inches(3.9), Inches(11.6), Inches(0.3),
                 "C  Equipment stipend is $500/year   ← should be nearest", size=14, bold=True, color=OK)
    add_text_box(s, Inches(0.85), Inches(4.3), Inches(11.6), Inches(0.4),
                 "c = [ 0.038, -0.121, 0.071, 0.198, -0.049, 0.022, 0.139, -0.077, 0.009, 0.171, -0.041, 0.088,  …  ×1524 more ]", size=12, color=INK)

    add_round_rect(s, Inches(0.55), Inches(5.1), Inches(12.2), Inches(1.0), WHITE)
    add_rect(s, Inches(0.55), Inches(5.1), Inches(0.1), Inches(1.0), DANGER)
    add_text_box(s, Inches(0.85), Inches(5.25), Inches(11.6), Inches(0.3),
                 "E  MFA required before VPN access   ← farther away", size=14, bold=True, color=DANGER)
    add_text_box(s, Inches(0.85), Inches(5.65), Inches(11.6), Inches(0.3),
                 "e = [ -0.112, 0.054, 0.189, -0.033, 0.147, -0.201, 0.028, 0.066, -0.155, 0.014, 0.093, -0.048,  …  ×1524 more ]", size=12, color=INK)

    add_round_rect(s, Inches(0.55), Inches(6.25), Inches(12.2), Inches(0.55), TEAL_LIGHT)
    add_text_box(s, Inches(0.85), Inches(6.35), Inches(11.6), Inches(0.35),
                 "Notice Q and C look similar number-by-number; E does not. Cosine uses all 1536 axes — not just x and y.", size=13, bold=True, color=INK)
    footer(s, next_page())

    # ========== 6. Cosine similarity ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Similarity: cosine (the usual default)", "Score from -1 to 1 (often 0–1 after normalization). Higher = more alike.")

    # Left: triangle geometry (why "cosine")
    add_round_rect(s, Inches(0.55), Inches(2.1), Inches(4.15), Inches(4.3), WHITE)
    add_text_box(s, Inches(0.8), Inches(2.3), Inches(3.7), Inches(0.35), "Geometry reminder", size=14, bold=True, color=TEAL)
    diagram = Path(__file__).resolve().parent / "assets" / "cosine_triangle_diagram.png"
    s.shapes.add_picture(str(diagram), Inches(0.85), Inches(2.7), width=Inches(3.5))
    add_text_box(s, Inches(0.8), Inches(5.85), Inches(3.7), Inches(0.4),
                 "Closer angle θ → larger cos(θ)", size=12, color=MUTED)

    # Middle: vector formula
    add_round_rect(s, Inches(4.9), Inches(2.1), Inches(4.0), Inches(4.3), WHITE)
    add_text_box(s, Inches(5.15), Inches(2.35), Inches(3.5), Inches(0.35), "In RAG (vectors)", size=14, bold=True, color=TEAL)
    add_text_box(s, Inches(5.15), Inches(2.9), Inches(3.5), Inches(1.1),
                 "cosine(q, d) =\n(q · d) / (|q| |d|)", size=16, bold=True, color=INK)
    add_text_box(s, Inches(5.15), Inches(4.2), Inches(3.5), Inches(0.7),
                 "Same idea: angle between query vector and chunk vector.", size=13, color=MUTED)
    add_bullets(s, Inches(5.1), Inches(5.0), Inches(3.6), Inches(1.2), [
        "1.0 nearly identical meaning",
        "0.7–0.9 strong match",
        "< 0.4 usually off-topic",
    ], size=13, spacing=6)

    # Right: why cosine
    add_round_rect(s, Inches(9.1), Inches(2.1), Inches(3.65), Inches(4.3), INK)
    add_text_box(s, Inches(9.35), Inches(2.4), Inches(3.2), Inches(0.4), "Why use it?", size=14, bold=True, color=TEAL)
    add_bullets(s, Inches(9.3), Inches(3.0), Inches(3.2), Inches(3.0), [
        "Ignores vector length",
        "Focuses on direction = meaning",
        "Embeddings often normalized",
        "Then cosine ≈ dot product",
        "Vector DBs optimize for this",
    ], size=13, color=WHITE, spacing=10)
    footer(s, next_page())

    # ========== 7. Numeric similarity example ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Example · Rank three chunks for one query", "Toy 3D vectors (made-up numbers) — same process at 1536-D")
    add_round_rect(s, Inches(0.55), Inches(2.0), Inches(12.2), Inches(0.75), TEAL_LIGHT)
    add_text_box(s, Inches(0.85), Inches(2.2), Inches(11.6), Inches(0.4),
                 'Query Q: "How much is the equipment stipend?"   →  q = [0.90, 0.20, 0.10]', size=14, bold=True, color=INK)

    add_table(
        s, Inches(0.55), Inches(3.0), Inches(12.2), Inches(2.8),
        ["Chunk", "Text (short)", "Vector", "Cosine ≈"],
        [
            ["C stipend", "Equipment stipend $500/year", "[0.88, 0.25, 0.08]", "0.99"],
            ["C remote", "Remote work up to 3 days/week", "[0.20, 0.85, 0.15]", "0.41"],
            ["C MFA", "MFA required before VPN access", "[0.10, 0.15, 0.90]", "0.22"],
        ],
        col_widths=[Inches(1.8), Inches(4.5), Inches(3.5), Inches(2.4)],
    )
    add_text_box(s, Inches(0.55), Inches(6.1), Inches(12.2), Inches(0.5),
                 "Retrieval returns C stipend first (top-1). Top-k=3 would still include weaker neighbors for the LLM to ignore.", size=14, color=MUTED)
    footer(s, next_page())

    # ========== 8. Embedding models ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Embedding models you'll meet", "Different sizes, languages, and price — same job: text → vector")
    models = [
        ("OpenAI / Azure text-embedding-3", "API · Foundry or OpenAI", "Small 1536 / Large 3072 dims", "Common prod default in Azure AI Foundry"),
        ("Cohere embed-v3", "API · strong retrieval", "1024 dims", "Good multilingual + search modes"),
        ("all-MiniLM-L6-v2", "Local · free", "384 dims", "Labs, demos, offline apps"),
        ("bge / e5 family", "Local or hosted", "768+ dims", "Strong open retrieval baselines"),
    ]
    for i, (name, kind, dims, note) in enumerate(models):
        col, row = i % 2, i // 2
        x = Inches(0.55) + Inches(col * 6.3)
        y = Inches(2.1) + Inches(row * 2.15)
        add_round_rect(s, x, y, Inches(6.05), Inches(1.95), WHITE)
        add_rect(s, x, y, Inches(0.1), Inches(1.95), TEAL)
        add_text_box(s, x + Inches(0.3), y + Inches(0.25), Inches(5.5), Inches(0.4), name, size=15, bold=True, color=INK)
        add_text_box(s, x + Inches(0.3), y + Inches(0.7), Inches(5.5), Inches(0.35), f"{kind}  ·  {dims}", size=12, color=TEAL)
        add_text_box(s, x + Inches(0.3), y + Inches(1.15), Inches(5.5), Inches(0.5), note, size=13, color=MUTED)
    footer(s, next_page())

    # ========== 8b. What dims means ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "What does “dims” mean?", "Dims = dimensions = how many numbers are in each embedding vector")
    add_round_rect(s, Inches(0.55), Inches(2.15), Inches(12.2), Inches(1.1), TEAL_LIGHT)
    add_text_box(s, Inches(0.85), Inches(2.45), Inches(11.6), Inches(0.55),
                 "Example: 1536 dims → each chunk/query becomes a list of 1536 numbers (a fingerprint of meaning).", size=15, bold=True, color=INK)

    dim_cards = [
        ("384 dims", "MiniLM-style", "Smaller · faster · fine for labs"),
        ("1536 dims", "embedding-3-small", "Common Azure / OpenAI default"),
        ("3072 dims", "embedding-3-large", "Richer fingerprint · heavier"),
    ]
    for i, (t, mid, b) in enumerate(dim_cards):
        x = Inches(0.55) + Inches(i * 4.2)
        add_round_rect(s, x, Inches(3.5), Inches(4.0), Inches(2.0), WHITE)
        add_rect(s, x, Inches(3.5), Inches(4.0), Inches(0.1), TEAL)
        add_text_box(s, x + Inches(0.25), Inches(3.8), Inches(3.5), Inches(0.4), t, size=18, bold=True, color=TEAL)
        add_text_box(s, x + Inches(0.25), Inches(4.35), Inches(3.5), Inches(0.35), mid, size=13, color=INK)
        add_text_box(s, x + Inches(0.25), Inches(4.85), Inches(3.5), Inches(0.4), b, size=13, color=MUTED)

    add_round_rect(s, Inches(0.55), Inches(5.8), Inches(12.2), Inches(0.7), WHITE)
    add_text_box(s, Inches(0.85), Inches(5.95), Inches(11.6), Inches(0.4),
                 "More dims can mean richer meaning — but also more storage, cost, and index size. Not always “bigger = must use.”", size=14, color=INK)
    footer(s, next_page())

    # ========== 8c. Azure Foundry small vs large ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Azure AI Foundry · Small vs Large embeddings", "Same job (text → vector). Different size, quality, and cost.")

    add_round_rect(s, Inches(0.55), Inches(2.1), Inches(6.0), Inches(3.5), WHITE)
    add_rect(s, Inches(0.55), Inches(2.1), Inches(6.0), Inches(0.1), TEAL)
    add_text_box(s, Inches(0.9), Inches(2.4), Inches(5.4), Inches(0.4), "Text Embedding Small", size=18, bold=True, color=TEAL)
    add_text_box(s, Inches(0.9), Inches(2.9), Inches(5.4), Inches(0.35), "Usually text-embedding-3-small", size=13, color=MUTED)
    add_bullets(s, Inches(0.85), Inches(3.4), Inches(5.4), Inches(2.0), [
        "Default dims: 1536",
        "Cheaper and faster enough for most RAG",
        "Great starting point for learning / prod",
        "Analogy: a clear phone photo",
    ], size=14, spacing=7)

    add_round_rect(s, Inches(6.85), Inches(2.1), Inches(5.9), Inches(3.5), WHITE)
    add_rect(s, Inches(6.85), Inches(2.1), Inches(5.9), Inches(0.1), ACCENT)
    add_text_box(s, Inches(7.2), Inches(2.4), Inches(5.3), Inches(0.4), "Text Embedding Large", size=18, bold=True, color=ACCENT)
    add_text_box(s, Inches(7.2), Inches(2.9), Inches(5.3), Inches(0.35), "Usually text-embedding-3-large", size=13, color=MUTED)
    add_bullets(s, Inches(7.15), Inches(3.4), Inches(5.3), Inches(2.0), [
        "Default dims: 3072",
        "Often better on hard retrieval questions",
        "Costs more; vectors use more storage",
        "Analogy: a higher-resolution photo",
    ], size=14, spacing=7)

    add_round_rect(s, Inches(0.55), Inches(5.85), Inches(12.2), Inches(0.7), TEAL_LIGHT)
    add_text_box(s, Inches(0.85), Inches(6.0), Inches(11.6), Inches(0.4),
                 "Rule: use the SAME model for indexing docs and embedding queries. Don’t mix Small docs + Large queries.", size=14, bold=True, color=INK)
    footer(s, next_page())

    # ========== 9. Choosing a model ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "How to choose an embedding model", "Start with a known retrieval model — then measure on your questions")
    rows = [
        ("Prototype / class lab", "MiniLM or Foundry Small", "Fast, cheap, good enough to learn"),
        ("Most Azure RAG apps", "text-embedding-3-small", "Cost vs quality sweet spot in Foundry"),
        ("Hard retrieval / high stakes", "text-embedding-3-large", "Try when Small misses too often"),
        ("Multilingual handbook", "Cohere / multilingual e5", "Don't assume English-only models"),
        ("Must stay on-prem", "Local bge / e5", "No API data leaving the building"),
    ]
    for i, (when, pick, why) in enumerate(rows):
        y = Inches(2.05) + Inches(i * 0.85)
        add_round_rect(s, Inches(0.55), y, Inches(12.2), Inches(0.72), WHITE)
        add_text_box(s, Inches(0.85), y + Inches(0.18), Inches(3.5), Inches(0.4), when, size=14, bold=True, color=INK)
        add_text_box(s, Inches(4.5), y + Inches(0.18), Inches(3.8), Inches(0.4), pick, size=14, color=TEAL)
        add_text_box(s, Inches(8.5), y + Inches(0.18), Inches(4.0), Inches(0.4), why, size=13, color=MUTED)
    footer(s, next_page())

    # ========== 10. Indexing pipeline ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Indexing: chunk → embed → store", "Runs once (or on every doc update). Queries never re-embed the whole corpus.")
    steps = [
        ("1. Chunk", "Split handbook into units\n(from Part 1)"),
        ("2. Embed", "Call embedding API /\nlocal model per chunk"),
        ("3. Attach meta", "source, section, page,\nparent_id, dates"),
        ("4. Upsert", "Write vector + meta\ninto vector store"),
    ]
    for i, (t, b) in enumerate(steps):
        x = Inches(0.55) + Inches(i * 3.15)
        add_round_rect(s, x, Inches(2.3), Inches(3.0), Inches(3.2), WHITE)
        add_rect(s, x, Inches(2.3), Inches(3.0), Inches(0.12), TEAL)
        add_text_box(s, x + Inches(0.2), Inches(2.7), Inches(2.6), Inches(0.5), t, size=18, bold=True, color=TEAL)
        add_text_box(s, x + Inches(0.2), Inches(3.5), Inches(2.6), Inches(1.6), b, size=14, color=INK)
    add_round_rect(s, Inches(0.55), Inches(5.8), Inches(12.2), Inches(0.7), TEAL_LIGHT)
    add_text_box(s, Inches(0.85), Inches(5.95), Inches(11.6), Inches(0.4),
                 "Rule: same embedding model at index time and query time. Mixing models breaks similarity.", size=14, bold=True, color=INK)
    footer(s, next_page())

    # ========== 11. Indexing worked example ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Example · Indexing three handbook chunks", "What actually gets written to the store")
    add_table(
        s, Inches(0.55), Inches(2.05), Inches(12.2), Inches(3.6),
        ["id", "text", "section", "vector (abbrev)", "embedded?"],
        [
            ["c1", "Remote work up to 3 days/week", "Remote", "[0.21, 0.84, …]", "Yes"],
            ["c2", "Equipment stipend is $500/year", "Remote", "[0.88, 0.24, …]", "Yes"],
            ["c3", "MFA required before VPN access", "Security", "[0.11, 0.14, …]", "Yes"],
            ["p_remote", "Full Section 3 body (parent)", "Remote", "—", "No*"],
        ],
        col_widths=[Inches(1.5), Inches(4.2), Inches(1.6), Inches(2.8), Inches(2.1)],
    )
    add_text_box(s, Inches(0.55), Inches(5.9), Inches(12.2), Inches(0.6),
                 "* Parent-child reminder: parents may be stored as plain text only; children carry the vectors used for search.", size=13, color=MUTED)
    footer(s, next_page())

    # ========== 12. Vector stores ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "What is a vector store?", "A database optimized to find nearest neighbors among many vectors")
    cards = [
        ("Stores", "Vectors + payload (metadata + often the text)"),
        ("Searches", "ANN: approximate nearest neighbor (HNSW, IVF…)"),
        ("Filters", "\"section = Security\" before/after ANN"),
        ("Examples", "Pinecone, Weaviate, Qdrant, pgvector, Chroma"),
    ]
    for i, (t, b) in enumerate(cards):
        col, row = i % 2, i // 2
        x = Inches(0.55) + Inches(col * 6.3)
        y = Inches(2.15) + Inches(row * 2.1)
        add_round_rect(s, x, y, Inches(6.05), Inches(1.9), WHITE)
        add_text_box(s, x + Inches(0.35), y + Inches(0.35), Inches(5.4), Inches(0.4), t, size=18, bold=True, color=TEAL)
        add_text_box(s, x + Inches(0.35), y + Inches(0.95), Inches(5.4), Inches(0.6), b, size=15, color=INK)
    footer(s, next_page())

    # ========== 13. Metadata example ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Example · Metadata filters save bad hits", 'Query: "VPN login rules" — without filters, Benefits chunks can sneak in')
    add_round_rect(s, Inches(0.55), Inches(2.15), Inches(6.0), Inches(4.2), WHITE)
    add_rect(s, Inches(0.55), Inches(2.15), Inches(6.0), Inches(0.1), DANGER)
    add_text_box(s, Inches(0.9), Inches(2.5), Inches(5.4), Inches(0.4), "No filter (top-3)", size=16, bold=True, color=DANGER)
    add_bullets(s, Inches(0.85), Inches(3.2), Inches(5.4), Inches(2.8), [
        "1. MFA required before VPN  ✓",
        "2. Vision coverage after 90 days  ✗",
        "3. Device wipe on offboarding  ~",
        "Problem: \"access\" words confuse Benefits",
    ], size=14, spacing=8)

    add_round_rect(s, Inches(6.85), Inches(2.15), Inches(5.9), Inches(4.2), WHITE)
    add_rect(s, Inches(6.85), Inches(2.15), Inches(5.9), Inches(0.1), OK)
    add_text_box(s, Inches(7.2), Inches(2.5), Inches(5.3), Inches(0.4), 'Filter: section = "Security"', size=16, bold=True, color=OK)
    add_bullets(s, Inches(7.15), Inches(3.2), Inches(5.3), Inches(2.8), [
        "1. MFA required before VPN  ✓",
        "2. VPN only on company devices  ✓",
        "3. Device wipe on offboarding  ✓",
        "Same query — cleaner context for the LLM",
    ], size=14, spacing=8)
    footer(s, next_page())

    # ========== 14. Query-time flow ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Query time: retrieve → (optional) rerank → prompt", "This path runs on every user question")
    flow = [
        ("1", "User asks", '"How much is the equipment stipend?"'),
        ("2", "Embed query", "Same model as index → q vector"),
        ("3", "ANN search", "Top-k nearest chunk vectors"),
        ("4", "Optional rerank", "Cross-encoder rescoring"),
        ("5", "Build prompt", "Stuff top passages + ask LLM"),
        ("6", "Answer + cite", "Return text + source ids"),
    ]
    for i, (n, t, d) in enumerate(flow):
        y = Inches(2.0) + Inches(i * 0.75)
        add_round_rect(s, Inches(0.55), y, Inches(12.2), Inches(0.65), WHITE)
        add_round_rect(s, Inches(0.75), y + Inches(0.12), Inches(0.42), Inches(0.42), TEAL)
        add_text_box(s, Inches(0.82), y + Inches(0.18), Inches(0.35), Inches(0.35), n, size=14, bold=True, color=WHITE)
        add_text_box(s, Inches(1.5), y + Inches(0.15), Inches(3.2), Inches(0.4), t, size=15, bold=True, color=TEAL)
        add_text_box(s, Inches(4.9), y + Inches(0.15), Inches(7.5), Inches(0.4), d, size=14, color=INK)
    footer(s, next_page())

    # ========== 15. Dense retrieval E2E example ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Example · Dense retrieval end-to-end", "One question, three scored neighbors, one answer")
    add_round_rect(s, Inches(0.55), Inches(2.0), Inches(12.2), Inches(0.7), INK)
    add_text_box(s, Inches(0.85), Inches(2.15), Inches(11.6), Inches(0.4),
                 'Q: "How much is the equipment stipend?"', size=15, bold=True, color=WHITE)

    hits = [
        ("#1  score 0.91", "c2  Equipment stipend is $500/year", OK),
        ("#2  score 0.62", "c1  Remote work up to 3 days/week", ACCENT),
        ("#3  score 0.41", "c4  Managers approve schedules by Friday", MUTED),
    ]
    for i, (sc, txt, col) in enumerate(hits):
        x = Inches(0.55) + Inches(i * 4.2)
        add_round_rect(s, x, Inches(2.95), Inches(4.0), Inches(2.0), WHITE)
        add_rect(s, x, Inches(2.95), Inches(4.0), Inches(0.1), col)
        add_text_box(s, x + Inches(0.2), Inches(3.25), Inches(3.6), Inches(0.4), sc, size=14, bold=True, color=col)
        add_text_box(s, x + Inches(0.2), Inches(3.8), Inches(3.6), Inches(0.9), txt, size=13, color=INK)

    add_round_rect(s, Inches(0.55), Inches(5.25), Inches(12.2), Inches(1.2), TEAL_LIGHT)
    add_text_box(s, Inches(0.85), Inches(5.45), Inches(11.6), Inches(0.8),
                 "Prompt gets #1–#3. LLM answers: \"$500 per year\" and can cite c2.\n"
                 "If you only passed #2–#3 (bad top-k), the model may guess or say it doesn't know.",
                 size=14, bold=True, color=INK)
    footer(s, next_page())

    # ========== 16. Top-k ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Top-k: how many chunks to fetch?", "Too few misses context; too many wastes tokens and adds noise")
    for title, items, x, bar in [
        ("k too small (e.g. 1–2)", [
            "Miss second fact in multi-hop Qs",
            "Brittle if #1 is slightly wrong",
            "Good for ultra-precise factoids",
        ], 0.55, DANGER),
        ("k balanced (e.g. 4–8)", [
            "Room for related neighbors",
            "Fits most chat context budgets",
            "Default starting point for labs",
        ], 4.7, TEAL),
        ("k too large (e.g. 20+)", [
            "Noise dilutes the prompt",
            "Higher cost / latency",
            "Rerank becomes almost required",
        ], 8.85, ACCENT),
    ]:
        add_round_rect(s, Inches(x), Inches(2.2), Inches(3.9), Inches(4.1), WHITE)
        add_rect(s, Inches(x), Inches(2.2), Inches(3.9), Inches(0.1), bar)
        add_text_box(s, Inches(x) + Inches(0.25), Inches(2.55), Inches(3.4), Inches(0.6), title, size=15, bold=True, color=bar)
        add_bullets(s, Inches(x) + Inches(0.2), Inches(3.4), Inches(3.5), Inches(2.6), items, size=14, spacing=10)
    footer(s, next_page())

    # ========== 17. Top-k example ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, 'Example · Same query, different k', 'Q: "Stipend amount and who approves remote days?"')
    add_round_rect(s, Inches(0.55), Inches(2.15), Inches(6.0), Inches(4.2), WHITE)
    add_text_box(s, Inches(0.9), Inches(2.45), Inches(5.4), Inches(0.4), "k = 1", size=18, bold=True, color=DANGER)
    add_bullets(s, Inches(0.85), Inches(3.1), Inches(5.4), Inches(2.8), [
        "Returns only stipend chunk",
        "LLM knows $500",
        "Misses \"manager approval by Friday\"",
        "Half-answer — looks like a model bug",
    ], size=14, spacing=8)

    add_round_rect(s, Inches(6.85), Inches(2.15), Inches(5.9), Inches(4.2), WHITE)
    add_text_box(s, Inches(7.2), Inches(2.45), Inches(5.3), Inches(0.4), "k = 4 (+ overlap/parent)", size=18, bold=True, color=OK)
    add_bullets(s, Inches(7.15), Inches(3.1), Inches(5.3), Inches(2.8), [
        "Stipend + approval both present",
        "Full answer possible in one shot",
        "Still small enough for a clean prompt",
        "Fix was retrieval design, not a bigger LLM",
    ], size=14, spacing=8)
    footer(s, next_page())

    # ========== 18. Hybrid search ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Hybrid search: vectors + keywords", "Dense finds paraphrase; sparse finds exact IDs, codes, names")
    add_round_rect(s, Inches(0.55), Inches(2.15), Inches(6.0), Inches(4.2), WHITE)
    add_rect(s, Inches(0.55), Inches(2.15), Inches(0.1), Inches(4.2), TEAL)
    add_text_box(s, Inches(0.9), Inches(2.45), Inches(5.4), Inches(0.4), "Dense (embeddings)", size=16, bold=True, color=TEAL)
    add_bullets(s, Inches(0.85), Inches(3.1), Inches(5.4), Inches(2.8), [
        "Great at synonyms & paraphrase",
        '"pay for laptop" ≈ "equipment stipend"',
        "Weak at rare tokens / SKUs",
        "Needs a good embedding model",
    ], size=14, spacing=8)

    add_round_rect(s, Inches(6.85), Inches(2.15), Inches(5.9), Inches(4.2), WHITE)
    add_rect(s, Inches(6.85), Inches(2.15), Inches(0.1), Inches(4.2), ACCENT)
    add_text_box(s, Inches(7.2), Inches(2.45), Inches(5.3), Inches(0.4), "Sparse (BM25 / keyword)", size=16, bold=True, color=ACCENT)
    add_bullets(s, Inches(7.15), Inches(3.1), Inches(5.3), Inches(2.8), [
        "Great at exact strings",
        "Policy-ID-442, error codes, names",
        "Weak when wording differs a lot",
        "Often free / already in your search stack",
    ], size=14, spacing=8)
    footer(s, next_page())

    # ========== 19. Hybrid example ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Example · Why hybrid wins on IDs", 'Q: "What does policy RW-12 say about stipends?"')
    add_table(
        s, Inches(0.55), Inches(2.1), Inches(12.2), Inches(3.2),
        ["Method", "Top hit", "Why"],
        [
            ["Dense only", "Generic stipend paragraph", "Misses rare token RW-12"],
            ["BM25 only", "Doc titled RW-12", "May miss paraphrased body"],
            ["Hybrid (fuse)", "RW-12 section with $500 text", "ID match + meaning match"],
        ],
        col_widths=[Inches(2.4), Inches(4.8), Inches(5.0)],
    )
    add_round_rect(s, Inches(0.55), Inches(5.6), Inches(12.2), Inches(0.9), TEAL_LIGHT)
    add_text_box(s, Inches(0.85), Inches(5.8), Inches(11.6), Inches(0.5),
                 "Common fuse: Reciprocal Rank Fusion (RRF) — merge ranked lists without fragile score calibration.", size=14, bold=True, color=INK)
    footer(s, next_page())

    # ========== 20. Reranking ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Reranking: a second, smarter sort", "Retrieve broad (cheap), then rescore top candidates (precise)")
    steps = [
        ("Retrieve", "Fetch k=20 with ANN / hybrid", TEAL),
        ("Rerank", "Cross-encoder scores (query, chunk) pairs", ACCENT),
        ("Keep", "Pass top 3–5 to the LLM", OK),
    ]
    for i, (t, b, col) in enumerate(steps):
        x = Inches(0.55) + Inches(i * 4.2)
        add_round_rect(s, x, Inches(2.3), Inches(4.0), Inches(2.6), WHITE)
        add_rect(s, x, Inches(2.3), Inches(4.0), Inches(0.12), col)
        add_text_box(s, x + Inches(0.25), Inches(2.7), Inches(3.5), Inches(0.5), t, size=20, bold=True, color=col)
        add_text_box(s, x + Inches(0.25), Inches(3.5), Inches(3.5), Inches(1.1), b, size=15, color=INK)
    add_round_rect(s, Inches(0.55), Inches(5.3), Inches(12.2), Inches(1.15), TEAL_LIGHT)
    add_text_box(s, Inches(0.85), Inches(5.55), Inches(11.6), Inches(0.7),
                 "Why it helps: bi-encoders embed query & doc separately (fast). Cross-encoders read both together (accurate, slower).\n"
                 "Use when first-stage recall is good but precision@5 is messy.",
                 size=14, color=INK)
    footer(s, next_page())

    # ========== 21. Rerank example ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Example · Rerank fixes a near-miss", 'Q: "Is security training required before VPN?"')
    add_round_rect(s, Inches(0.55), Inches(2.15), Inches(6.0), Inches(4.2), WHITE)
    add_text_box(s, Inches(0.9), Inches(2.45), Inches(5.4), Inches(0.4), "After ANN (k=5 order)", size=15, bold=True, color=MUTED)
    add_bullets(s, Inches(0.85), Inches(3.1), Inches(5.4), Inches(2.8), [
        "1. VPN only on company devices",
        "2. MFA required before VPN",
        "3. Security training before access  ← true answer",
        "4. Remote work 3 days/week",
        "5. Device wipe policy",
    ], size=13, spacing=7)

    add_round_rect(s, Inches(6.85), Inches(2.15), Inches(5.9), Inches(4.2), WHITE)
    add_text_box(s, Inches(7.2), Inches(2.45), Inches(5.3), Inches(0.4), "After cross-encoder rerank", size=15, bold=True, color=OK)
    add_bullets(s, Inches(7.15), Inches(3.1), Inches(5.3), Inches(2.8), [
        "1. Security training before access  ✓",
        "2. MFA required before VPN",
        "3. VPN only on company devices",
        "…",
        "LLM now sees the decisive sentence first",
    ], size=13, spacing=7)
    footer(s, next_page())

    # ========== 22. MMR diversity ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Diversity: MMR (Maximal Marginal Relevance)", "Avoid sending five near-duplicate chunks about the same sentence")
    add_round_rect(s, Inches(0.55), Inches(2.15), Inches(6.0), Inches(4.2), WHITE)
    add_text_box(s, Inches(0.9), Inches(2.45), Inches(5.4), Inches(0.4), "Without MMR", size=16, bold=True, color=DANGER)
    add_bullets(s, Inches(0.85), Inches(3.1), Inches(5.4), Inches(2.8), [
        "Top hits all paraphrase \"$500 stipend\"",
        "Approval rule never appears",
        "Wastes context window",
        "Multi-hop answers fail quietly",
    ], size=14, spacing=8)

    add_round_rect(s, Inches(6.85), Inches(2.15), Inches(5.9), Inches(4.2), WHITE)
    add_text_box(s, Inches(7.2), Inches(2.45), Inches(5.3), Inches(0.4), "With MMR", size=16, bold=True, color=OK)
    add_bullets(s, Inches(7.15), Inches(3.1), Inches(5.3), Inches(2.8), [
        "Keeps best stipend chunk",
        "Prefers a different but still relevant chunk",
        "Approval + stipend both in prompt",
        "Trade a bit of pure similarity for coverage",
    ], size=14, spacing=8)
    footer(s, next_page())

    # ========== 23. Failure modes ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Common retrieval failures (with fixes)", 'These look like "the LLM is dumb" — usually it never saw the right text')
    fails = [
        ("Wrong embedding model mix", "Re-index with one model end-to-end"),
        ("Chunk too big / too small", "Revisit Part 1 strategies"),
        ("No metadata filters", "Filter by product, locale, section"),
        ("k too low for multi-hop", "Raise k or use parent-child"),
        ("Exact ID queries", "Add BM25 / hybrid"),
        ("Good recall, bad order", "Add a reranker"),
    ]
    for i, (t, b) in enumerate(fails):
        col, row = i % 2, i // 2
        x = Inches(0.55) + Inches(col * 6.3)
        y = Inches(2.1) + Inches(row * 1.4)
        add_round_rect(s, x, y, Inches(6.05), Inches(1.2), WHITE)
        add_text_box(s, x + Inches(0.25), y + Inches(0.2), Inches(5.5), Inches(0.35), t, size=14, bold=True, color=DANGER)
        add_text_box(s, x + Inches(0.25), y + Inches(0.65), Inches(5.5), Inches(0.35), b, size=13, color=MUTED)
    footer(s, next_page())

    # ========== 24. Evaluation ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Evaluate retrieval before blaming the LLM", "Build 20–50 labeled questions; score the search step alone")
    metrics = [
        ("Recall@k", "Was the needed chunk in the top-k?", "Must-have for RAG"),
        ("MRR", "How high was the first relevant hit?", "Order quality"),
        ("nDCG", "Graded relevance across the list", "When multiple goods exist"),
        ("Answer accuracy", "Did the final LLM answer match gold?", "End-to-end check"),
    ]
    for i, (t, b, note) in enumerate(metrics):
        y = Inches(2.1) + Inches(i * 1.05)
        add_round_rect(s, Inches(0.55), y, Inches(12.2), Inches(0.9), WHITE)
        add_text_box(s, Inches(0.9), y + Inches(0.25), Inches(2.5), Inches(0.4), t, size=16, bold=True, color=TEAL)
        add_text_box(s, Inches(3.6), y + Inches(0.25), Inches(5.5), Inches(0.4), b, size=14, color=INK)
        add_text_box(s, Inches(9.3), y + Inches(0.25), Inches(3.2), Inches(0.4), note, size=13, color=MUTED)
    footer(s, next_page())

    # ========== 25. Eval example ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Example · Scoring three strategies on 10 questions", "Same handbook corpus — only retrieval setup changes")
    add_table(
        s, Inches(0.55), Inches(2.15), Inches(12.2), Inches(3.4),
        ["Setup", "Recall@5", "MRR", "What happened"],
        [
            ["Dense, k=5", "0.70", "0.55", "Missed RW-12 ID questions"],
            ["Hybrid, k=5", "0.85", "0.68", "IDs fixed; still some order noise"],
            ["Hybrid + rerank", "0.90", "0.82", "Best precision for the prompt"],
        ],
        col_widths=[Inches(2.8), Inches(1.8), Inches(1.5), Inches(6.1)],
    )
    add_text_box(s, Inches(0.55), Inches(5.9), Inches(12.2), Inches(0.55),
                 "Teaching takeaway: measure retrieval first. Don't swap LLMs until Recall@k is healthy.", size=14, bold=True, color=INK)
    footer(s, next_page())

    # ========== 26. Comparison ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Retrieval toolkit at a glance", "Layer techniques as quality needs grow")
    add_table(
        s, Inches(0.55), Inches(2.1), Inches(12.2), Inches(4.2),
        ["Technique", "Helps with", "Cost", "Start here?"],
        [
            ["Dense ANN", "Paraphrase / meaning", "Low–Med", "Yes"],
            ["Metadata filters", "Wrong-section noise", "Low", "Yes"],
            ["Hybrid + RRF", "IDs, codes, names", "Med", "Often"],
            ["Reranker", "Precision of top-5", "Med–High", "When noisy"],
            ["MMR", "Duplicate neighbors", "Low", "Multi-hop"],
            ["Parent expand", "Thin children", "Low", "Long manuals"],
        ],
        col_widths=[Inches(2.6), Inches(3.8), Inches(2.4), Inches(3.4)],
    )
    footer(s, next_page())

    # ========== 27. Decision guide ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "How to choose a retrieval setup", "Start simple; upgrade when evals fail a specific way")
    guide = [
        ("Shipping a class demo this week?", "→ Dense + k=5 + citations"),
        ("Users type product IDs / error codes?", "→ Add hybrid (BM25 + dense)"),
        ("Top-k has the answer but buried?", "→ Add reranker"),
        ("Answers need a whole section?", "→ Parent-child expand after hit"),
        ("Many near-duplicate chunks?", "→ MMR or better chunking"),
        ("Wrong department docs appear?", "→ Metadata filters first"),
    ]
    for i, (q, a) in enumerate(guide):
        y = Inches(2.0) + Inches(i * 0.72)
        add_round_rect(s, Inches(0.55), y, Inches(12.2), Inches(0.6), WHITE)
        add_text_box(s, Inches(0.85), y + Inches(0.12), Inches(6.5), Inches(0.4), q, size=14, bold=True, color=INK)
        add_text_box(s, Inches(7.5), y + Inches(0.12), Inches(5.0), Inches(0.4), a, size=14, color=TEAL)
    footer(s, next_page())

    # ========== 28. Applications ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Applications · retrieval patterns in the wild", "Same embedding idea — different retrieval recipes")
    apps = [
        ("Support bot", "Hybrid + filters by product", "Cite help-center URL"),
        ("HR handbook Q&A", "Dense + parent expand", "Policy section in prompt"),
        ("Code assistant", "Code embeddings + path filters", "Don't mix random files"),
        ("Legal search", "Hybrid + rerank", "Clause IDs must hit"),
        ("Research papers", "Dense + section metadata", "Methods vs results"),
        ("Internal wiki", "Hybrid + recency boost", "Prefer newer pages"),
    ]
    for i, (t, how, why) in enumerate(apps):
        col, row = i % 3, i // 3
        x = Inches(0.55) + Inches(col * 4.2)
        y = Inches(2.15) + Inches(row * 2.15)
        add_round_rect(s, x, y, Inches(4.0), Inches(1.95), WHITE)
        add_text_box(s, x + Inches(0.2), y + Inches(0.25), Inches(3.6), Inches(0.4), t, size=15, bold=True, color=TEAL)
        add_text_box(s, x + Inches(0.2), y + Inches(0.75), Inches(3.6), Inches(0.4), how, size=13, color=INK)
        add_text_box(s, x + Inches(0.2), y + Inches(1.25), Inches(3.6), Inches(0.4), why, size=12, color=MUTED)
    footer(s, next_page())

    # ========== 29. Lab ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Classroom lab (40–50 min)", "Same corpus as chunking lab — now score retrieval")
    steps = [
        ("1", "Reuse the handbook chunks from Part 1 (or re-chunk once)"),
        ("2", "Embed with one model; store vectors + metadata"),
        ("3", "Write 12 questions: 4 easy, 4 paraphrase, 2 ID, 2 multi-hop"),
        ("4", "Run dense-only vs hybrid; measure Recall@5"),
        ("5", "Optional: add rerank; compare MRR and answer quality"),
        ("6", "Discuss: which failure was retrieval vs chunking vs LLM?"),
    ]
    for i, (n, t) in enumerate(steps):
        y = Inches(2.0) + Inches(i * 0.72)
        add_round_rect(s, Inches(0.55), y, Inches(12.2), Inches(0.6), WHITE)
        add_round_rect(s, Inches(0.75), y + Inches(0.1), Inches(0.4), Inches(0.4), TEAL)
        add_text_box(s, Inches(0.85), y + Inches(0.15), Inches(0.3), Inches(0.35), n, size=13, bold=True, color=WHITE)
        add_text_box(s, Inches(1.5), y + Inches(0.12), Inches(10.9), Inches(0.4), t, size=14, color=INK)
    footer(s, next_page())

    # ========== 30. Takeaways + closing ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Key takeaways", "What students should leave remembering")
    takes = [
        ("Embeddings = meaning as numbers", "Same model at index + query"),
        ("Retrieval is a product decision", "k, filters, hybrid, rerank"),
        ("Measure search separately", "Recall@k before swapping LLMs"),
        ("Examples beat slogans", "Always debug with a real question"),
    ]
    for i, (t, b) in enumerate(takes):
        col, row = i % 2, i // 2
        x = Inches(0.55) + Inches(col * 6.3)
        y = Inches(2.15) + Inches(row * 2.15)
        add_round_rect(s, x, y, Inches(6.05), Inches(1.95), WHITE)
        add_rect(s, x, y, Inches(0.12), Inches(1.95), TEAL)
        add_text_box(s, x + Inches(0.35), y + Inches(0.4), Inches(5.4), Inches(0.5), t, size=16, bold=True, color=INK)
        add_text_box(s, x + Inches(0.35), y + Inches(1.05), Inches(5.4), Inches(0.5), b, size=14, color=MUTED)
    footer(s, next_page())

    # Closing
    s = prs.slides.add_slide(blank)
    set_bg(s, INK)
    add_rect(s, Inches(0), Inches(0), Inches(0.25), SLIDE_H, TEAL)
    add_text_box(s, Inches(0.7), Inches(2.4), Inches(11), Inches(0.4), "NEXT UP", size=14, bold=True, color=TEAL)
    add_text_box(s, Inches(0.7), Inches(3.0), Inches(11), Inches(1.4),
                 "Augmenting prompts,\ncitations, and RAG evaluation", size=36, bold=True, color=WHITE)
    add_text_box(s, Inches(0.7), Inches(5.0), Inches(11), Inches(0.6),
                 "Questions? Run the lab — then we'll grade your retrievers, not just your prompts.", size=16, color=LIGHT)
    next_page()

    out = Path(__file__).resolve().parent / "RAG_Embeddings_and_Retrieval.pptx"
    prs.save(str(out))
    return out, page


if __name__ == "__main__":
    path, n = build()
    print(f"Wrote {n} slides -> {path}")
