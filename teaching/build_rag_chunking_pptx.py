#!/usr/bin/env python3
"""Generate RAG Chunking Strategies teaching deck."""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import nsmap
from lxml import etree

# --- Palette (ink + teal teaching theme) ---
INK = RGBColor(0x14, 0x1E, 0x2A)
INK_SOFT = RGBColor(0x1E, 0x2C, 0x3C)
TEAL = RGBColor(0x0C, 0x7C, 0x7C)
TEAL_LIGHT = RGBColor(0xE6, 0xF4, 0xF4)
PAPER = RGBColor(0xF8, 0xF6, 0xF3)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
MUTED = RGBColor(0x5A, 0x66, 0x75)
ACCENT = RGBColor(0xD4, 0x7A, 0x2A)  # amber for callouts
DANGER = RGBColor(0xB5, 0x3A, 0x3A)
OK = RGBColor(0x2E, 0x7D, 0x4F)
LINE = RGBColor(0xD8, 0xD2, 0xC8)

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)


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


def add_multiline(slide, left, top, width, height, lines, size=16, color=INK, bold_first=False, spacing=8):
    """lines: list of strings or (text, bold) tuples."""
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    for i, line in enumerate(lines):
        if isinstance(line, tuple):
            text, is_bold = line
        else:
            text, is_bold = line, (bold_first and i == 0)
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(spacing)
        run = p.add_run()
        run.text = text
        set_run(run, size, bold=is_bold, color=color)
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


def add_rect(slide, left, top, width, height, color):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    fill_shape(shape, color)
    return shape


def add_round_rect(slide, left, top, width, height, color, radius=0.1):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    fill_shape(shape, color)
    # soften corners via adjustments if available
    try:
        shape.adjustments[0] = radius
    except Exception:
        pass
    return shape


def accent_bar(slide, color=TEAL):
    add_rect(slide, Inches(0), Inches(0), Inches(0.18), SLIDE_H, color)


def footer(slide, page, total=18):
    add_text_box(
        slide, Inches(11.4), Inches(7.05), Inches(1.6), Inches(0.35),
        f"{page}  /  {total}", size=11, color=MUTED, align=PP_ALIGN.RIGHT
    )
    add_text_box(
        slide, Inches(0.55), Inches(7.05), Inches(4), Inches(0.35),
        "RAG · Chunking Strategies", size=11, color=MUTED
    )


def section_label(slide, text, left=Inches(0.55), top=Inches(0.35)):
    add_text_box(slide, left, top, Inches(6), Inches(0.35), text.upper(), size=12, bold=True, color=TEAL)


def title_block(slide, title, subtitle=None):
    section_label(slide, "RAG Teaching Series")
    add_text_box(slide, Inches(0.55), Inches(0.7), Inches(12), Inches(0.7), title, size=32, bold=True, color=INK)
    if subtitle:
        add_text_box(slide, Inches(0.55), Inches(1.35), Inches(12), Inches(0.45), subtitle, size=16, color=MUTED)


def set_bg(slide, color):
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), SLIDE_W, SLIDE_H)
    fill_shape(bg, color)
    # send to back
    spTree = slide.shapes._spTree
    sp = bg._element
    spTree.remove(sp)
    spTree.insert(2, sp)


def card(slide, left, top, width, height, title, body_lines, title_color=TEAL):
    add_round_rect(slide, left, top, width, height, WHITE)
    add_rect(slide, left, top, Inches(0.1), height, title_color)
    add_text_box(slide, left + Inches(0.25), top + Inches(0.2), width - Inches(0.4), Inches(0.4), title, size=15, bold=True, color=title_color)
    add_bullets(slide, left + Inches(0.2), top + Inches(0.65), width - Inches(0.35), height - Inches(0.85), body_lines, size=13, color=INK, spacing=6)


def build():
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H
    blank = prs.slide_layouts[6]

    # ========== 1. Title ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, INK)
    add_rect(s, Inches(0), Inches(0), Inches(0.25), SLIDE_H, TEAL)
    add_rect(s, Inches(10.5), Inches(0), Inches(2.833), SLIDE_H, INK_SOFT)
    add_text_box(s, Inches(0.7), Inches(1.8), Inches(9), Inches(0.4), "TEACHING SERIES · INTRO TO AI SYSTEMS", size=13, bold=True, color=TEAL)
    add_text_box(s, Inches(0.7), Inches(2.3), Inches(9.5), Inches(1.2), "Retrieval-Augmented\nGeneration (RAG)", size=44, bold=True, color=WHITE)
    add_text_box(s, Inches(0.7), Inches(4.6), Inches(9), Inches(0.5), "Focus: Chunking Strategies — with examples & applications", size=18, color=RGBColor(0xB8, 0xC4, 0xD0))
    add_text_box(s, Inches(0.7), Inches(6.5), Inches(9), Inches(0.4), "For builders learning how to ground LLMs in real documents", size=13, color=MUTED)

    # ========== 2. Agenda ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "What we'll cover", "A practical path from RAG basics → chunking craft")
    items = [
        ("01", "What RAG is and why it exists"),
        ("02", "Where chunking sits in the pipeline"),
        ("03", "Six chunking strategies with worked examples"),
        ("04", "How to choose a strategy for your data"),
        ("05", "Real applications + common failure modes"),
    ]
    for i, (num, text) in enumerate(items):
        y = Inches(2.1) + Inches(i * 0.85)
        add_round_rect(s, Inches(0.55), y, Inches(12.2), Inches(0.7), WHITE)
        add_text_box(s, Inches(0.85), y + Inches(0.15), Inches(1), Inches(0.4), num, size=22, bold=True, color=TEAL)
        add_text_box(s, Inches(2.0), y + Inches(0.18), Inches(10), Inches(0.4), text, size=20, color=INK)

    # ========== 3. What is RAG ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "What is RAG?", "Retrieve relevant knowledge → Augment the prompt → Generate an answer")
    steps = [
        ("1. Retrieve", "Search your knowledge base for passages related to the user question."),
        ("2. Augment", "Insert those passages into the LLM prompt as grounded context."),
        ("3. Generate", "The model answers using that context — not only its training memory."),
    ]
    for i, (t, b) in enumerate(steps):
        x = Inches(0.55) + Inches(i * 4.15)
        add_round_rect(s, x, Inches(2.2), Inches(3.9), Inches(3.6), WHITE)
        add_rect(s, x, Inches(2.2), Inches(3.9), Inches(0.12), TEAL)
        add_text_box(s, x + Inches(0.3), Inches(2.6), Inches(3.3), Inches(0.5), t, size=22, bold=True, color=TEAL)
        add_text_box(s, x + Inches(0.3), Inches(3.4), Inches(3.3), Inches(2.0), b, size=16, color=INK)

    # ========== 4. Why RAG ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Why RAG? LLMs alone are not enough", "Chunking only matters because retrieval quality decides answer quality")
    problems = [
        ("Hallucinations", "Models invent confident-sounding facts when knowledge is missing."),
        ("Stale knowledge", "Training cutoffs miss policies, prices, and last week's docs."),
        ("Private data", "Company wikis, tickets, and PDFs are never in the base model."),
        ("Citations", "Users need sources — RAG returns passages you can show."),
    ]
    for i, (t, b) in enumerate(problems):
        row, col = divmod(i, 2)
        x = Inches(0.55) + Inches(col * 6.3)
        y = Inches(2.15) + Inches(row * 2.15)
        add_round_rect(s, x, y, Inches(6.0), Inches(1.9), WHITE)
        add_text_box(s, x + Inches(0.35), y + Inches(0.35), Inches(5.3), Inches(0.45), t, size=20, bold=True, color=INK)
        add_text_box(s, x + Inches(0.35), y + Inches(0.95), Inches(5.3), Inches(0.7), b, size=15, color=MUTED)

    # ========== 5. Pipeline ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "The RAG pipeline — and where chunking lives", "Indexing happens once; retrieval + generation happen per query")
    stages = [
        ("Documents", "PDFs, HTML,\nMD, tickets"),
        ("Chunk", "Split into\nretrievable units"),
        ("Embed", "Vectors +\nmetadata"),
        ("Store", "Vector DB /\nsearch index"),
        ("Retrieve", "Top-k for\nthe query"),
        ("Answer", "LLM + context\n+ citations"),
    ]
    for i, (t, b) in enumerate(stages):
        x = Inches(0.4) + Inches(i * 2.15)
        fill = TEAL if t == "Chunk" else WHITE
        tc = WHITE if t == "Chunk" else INK
        bc = TEAL_LIGHT if t == "Chunk" else MUTED
        add_round_rect(s, x, Inches(2.5), Inches(1.95), Inches(2.8), fill)
        add_text_box(s, x + Inches(0.1), Inches(2.8), Inches(1.75), Inches(0.5), t, size=16, bold=True, color=tc, align=PP_ALIGN.CENTER)
        add_text_box(s, x + Inches(0.1), Inches(3.5), Inches(1.75), Inches(1.4), b, size=13, color=bc if t == "Chunk" else MUTED, align=PP_ALIGN.CENTER)
        if i < len(stages) - 1:
            add_text_box(s, x + Inches(1.85), Inches(3.5), Inches(0.35), Inches(0.4), "→", size=20, bold=True, color=TEAL)
    add_round_rect(s, Inches(0.55), Inches(5.7), Inches(12.2), Inches(0.9), TEAL_LIGHT)
    add_text_box(s, Inches(0.85), Inches(5.9), Inches(11.6), Inches(0.55),
                 "Teaching focus: Chunk is the design decision that most often makes or breaks retrieval.", size=16, bold=True, color=INK)

    # ========== 6. Why chunking ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Why chunking matters", "Embeddings retrieve chunks — not whole books")
    add_round_rect(s, Inches(0.55), Inches(2.15), Inches(5.9), Inches(4.2), WHITE)
    add_text_box(s, Inches(0.9), Inches(2.4), Inches(5.2), Inches(0.45), "Too large", size=22, bold=True, color=DANGER)
    add_bullets(s, Inches(0.85), Inches(3.1), Inches(5.3), Inches(3.0), [
        "Dilutes the embedding signal",
        "Retrieves lots of irrelevant text",
        "Burns context window tokens",
        "Harder for the model to focus",
    ], size=16, spacing=12)

    add_round_rect(s, Inches(6.85), Inches(2.15), Inches(5.9), Inches(4.2), WHITE)
    add_text_box(s, Inches(7.2), Inches(2.4), Inches(5.2), Inches(0.45), "Too small", size=22, bold=True, color=ACCENT)
    add_bullets(s, Inches(7.15), Inches(3.1), Inches(5.3), Inches(3.0), [
        "Splits mid-idea / mid-sentence",
        "Loses surrounding context",
        "Needs more chunks to answer",
        "Noisy ranking / fragmented cites",
    ], size=16, spacing=12)

    # ========== 7. Strategy map ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Six chunking strategies we'll unpack", "From simplest to more structure-aware")
    strategies = [
        ("01", "Fixed-size", "Character / token windows"),
        ("02", "Overlap", "Sliding window continuity"),
        ("03", "Recursive", "Respect headings & structure"),
        ("04", "Semantic", "Split on meaning shifts"),
        ("05", "Parent–child", "Retrieve small, read large"),
        ("06", "Proposition", "Atomic fact-level chunks"),
    ]
    for i, (n, t, b) in enumerate(strategies):
        row, col = divmod(i, 3)
        x = Inches(0.55) + Inches(col * 4.2)
        y = Inches(2.2) + Inches(row * 2.2)
        add_round_rect(s, x, y, Inches(3.95), Inches(1.95), WHITE)
        add_text_box(s, x + Inches(0.25), y + Inches(0.3), Inches(1), Inches(0.4), n, size=18, bold=True, color=TEAL)
        add_text_box(s, x + Inches(0.25), y + Inches(0.8), Inches(3.4), Inches(0.4), t, size=20, bold=True, color=INK)
        add_text_box(s, x + Inches(0.25), y + Inches(1.3), Inches(3.4), Inches(0.4), b, size=14, color=MUTED)

    # ========== 8. Fixed-size ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "01 · Fixed-size chunking", "Split every N characters or tokens — simple, predictable, often good enough")
    add_round_rect(s, Inches(0.55), Inches(2.15), Inches(7.6), Inches(4.3), WHITE)
    add_text_box(s, Inches(0.9), Inches(2.4), Inches(7), Inches(0.4), "How it works", size=16, bold=True, color=TEAL)
    add_bullets(s, Inches(0.85), Inches(2.95), Inches(7), Inches(3.2), [
        "Choose size: e.g. 500–1000 tokens (depends on embedding model)",
        "Walk through the document sequentially",
        "Optionally break on whitespace / sentence ends near the limit",
        "Store chunk_id, source, page, start/end offsets as metadata",
    ], size=15, spacing=10)
    add_round_rect(s, Inches(8.4), Inches(2.15), Inches(4.35), Inches(4.3), INK)
    add_text_box(s, Inches(8.7), Inches(2.5), Inches(3.8), Inches(0.4), "Best for", size=14, bold=True, color=TEAL)
    add_bullets(s, Inches(8.65), Inches(3.1), Inches(3.8), Inches(3.0), [
        "Homogeneous text (blogs, emails)",
        "Quick prototypes / MVPs",
        "When structure is weak",
    ], size=14, color=WHITE, spacing=12)

    # ========== 9. Fixed-size example ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Example · Fixed-size on a policy doc", "Size = ~80 tokens  ·  no overlap")
    source = (
        "Employees may work remotely up to three days per week. Managers must "
        "approve schedules by Friday. Equipment stipends are $500 per year. "
        "Security training is mandatory before access is granted."
    )
    add_round_rect(s, Inches(0.55), Inches(2.05), Inches(12.2), Inches(1.35), TEAL_LIGHT)
    add_text_box(s, Inches(0.85), Inches(2.2), Inches(11.6), Inches(0.3), "SOURCE PARAGRAPH", size=11, bold=True, color=TEAL)
    add_text_box(s, Inches(0.85), Inches(2.55), Inches(11.6), Inches(0.7), source, size=14, color=INK)

    chunks = [
        ("Chunk A", "Employees may work remotely up to three days per week. Managers must approve schedules by Friday."),
        ("Chunk B", "Equipment stipends are $500 per year. Security training is mandatory before access is granted."),
    ]
    for i, (t, b) in enumerate(chunks):
        x = Inches(0.55) + Inches(i * 6.3)
        add_round_rect(s, x, Inches(3.65), Inches(6.0), Inches(2.5), WHITE)
        add_text_box(s, x + Inches(0.3), Inches(3.85), Inches(5.4), Inches(0.35), t, size=14, bold=True, color=TEAL)
        add_text_box(s, x + Inches(0.3), Inches(4.35), Inches(5.4), Inches(1.5), b, size=14, color=INK)

    # ========== 10. Overlap ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "02 · Overlapping / sliding window", "Carry the last N tokens into the next chunk so ideas don't die at the boundary")
    add_round_rect(s, Inches(0.55), Inches(2.15), Inches(6.0), Inches(4.3), WHITE)
    add_text_box(s, Inches(0.9), Inches(2.45), Inches(5.4), Inches(0.4), "Why overlap?", size=18, bold=True, color=TEAL)
    add_bullets(s, Inches(0.85), Inches(3.1), Inches(5.4), Inches(3.0), [
        "Questions often span two adjacent chunks",
        "Overlap preserves bridging sentences",
        "Typical overlap: 10–20% of chunk size",
        "Tradeoff: more storage + possible duplicates",
    ], size=15, spacing=12)

    # visual diagram of overlapping chunks
    add_round_rect(s, Inches(6.9), Inches(2.15), Inches(5.85), Inches(4.3), INK)
    add_text_box(s, Inches(7.25), Inches(2.45), Inches(5.2), Inches(0.35), "Visual", size=14, bold=True, color=TEAL)
    add_round_rect(s, Inches(7.25), Inches(3.2), Inches(5.1), Inches(0.7), TEAL)
    add_text_box(s, Inches(7.4), Inches(3.35), Inches(4.8), Inches(0.4), "Chunk 1 .................... [overlap]", size=13, bold=True, color=WHITE)
    add_round_rect(s, Inches(8.5), Inches(4.2), Inches(5.1), Inches(0.7), RGBColor(0x1A, 0x9A, 0x9A))
    add_text_box(s, Inches(8.65), Inches(4.35), Inches(4.8), Inches(0.4), "[overlap] .................... Chunk 2", size=13, bold=True, color=WHITE)
    add_text_box(s, Inches(7.25), Inches(5.3), Inches(5.2), Inches(0.8), "Shared region keeps continuity across the cut.", size=14, color=RGBColor(0xB8, 0xC4, 0xD0))

    # ========== 11. Overlap example ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Example · Overlap saves a multi-hop fact", "Query: \"How much is the stipend and who approves remote days?\"")
    add_round_rect(s, Inches(0.55), Inches(2.1), Inches(12.2), Inches(1.1), TEAL_LIGHT)
    add_text_box(s, Inches(0.85), Inches(2.35), Inches(11.6), Inches(0.6),
                 "Without overlap, stipend and approval rules can land in different chunks — retrieval may miss one half.", size=15, color=INK)

    add_round_rect(s, Inches(0.55), Inches(3.45), Inches(6.0), Inches(2.9), WHITE)
    add_text_box(s, Inches(0.85), Inches(3.65), Inches(5.4), Inches(0.35), "Chunk 1 (with overlap)", size=14, bold=True, color=TEAL)
    add_text_box(s, Inches(0.85), Inches(4.15), Inches(5.4), Inches(1.9),
                 "…Managers must approve schedules by Friday. Equipment stipends are $500 per year.…", size=14, color=INK)

    add_round_rect(s, Inches(6.85), Inches(3.45), Inches(5.9), Inches(2.9), WHITE)
    add_text_box(s, Inches(7.15), Inches(3.65), Inches(5.4), Inches(0.35), "Why it helps", size=14, bold=True, color=TEAL)
    add_bullets(s, Inches(7.1), Inches(4.2), Inches(5.4), Inches(1.9), [
        "Approval + stipend co-occur in one chunk",
        "Single retrieval can answer the full question",
        "Fewer \"I only found half the policy\" failures",
    ], size=14, spacing=10)

    # ========== 12. Recursive ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "03 · Recursive / structure-aware chunking", "Prefer natural boundaries: sections → paragraphs → sentences → words")
    add_round_rect(s, Inches(0.55), Inches(2.15), Inches(7.5), Inches(4.3), WHITE)
    add_text_box(s, Inches(0.9), Inches(2.45), Inches(7), Inches(0.4), "Split hierarchy (typical)", size=16, bold=True, color=TEAL)
    levels = [
        "1. Split on headings / markdown #",
        "2. If still too big → split on paragraphs (\\n\\n)",
        "3. Then sentences (. ! ?)",
        "4. Last resort → characters / tokens",
    ]
    add_bullets(s, Inches(0.85), Inches(3.1), Inches(6.9), Inches(3.0), levels, size=16, spacing=14)

    add_round_rect(s, Inches(8.3), Inches(2.15), Inches(4.45), Inches(4.3), INK)
    add_text_box(s, Inches(8.65), Inches(2.5), Inches(3.9), Inches(0.4), "Best for", size=14, bold=True, color=TEAL)
    add_bullets(s, Inches(8.6), Inches(3.15), Inches(3.9), Inches(3.0), [
        "Docs with headings",
        "Markdown / Notion / Confluence",
        "API references",
        "Handbooks & manuals",
    ], size=14, color=WHITE, spacing=12)

    # ========== 13. Recursive example ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Example · Recursive keeps sections intact", "Bad: cut mid-section  ·  Good: one chunk per heading block")
    add_round_rect(s, Inches(0.55), Inches(2.15), Inches(5.9), Inches(4.3), WHITE)
    add_rect(s, Inches(0.55), Inches(2.15), Inches(5.9), Inches(0.12), DANGER)
    add_text_box(s, Inches(0.9), Inches(2.5), Inches(5.2), Inches(0.4), "Naive fixed cut", size=16, bold=True, color=DANGER)
    add_text_box(s, Inches(0.9), Inches(3.1), Inches(5.2), Inches(3.0),
                 "## Refunds\nCustomers may request a refund within 30 days.\n## Shipping\nOrders ship within…  ← cut here mid-thought",
                 size=14, color=INK)

    add_round_rect(s, Inches(6.85), Inches(2.15), Inches(5.9), Inches(4.3), WHITE)
    add_rect(s, Inches(6.85), Inches(2.15), Inches(5.9), Inches(0.12), OK)
    add_text_box(s, Inches(7.2), Inches(2.5), Inches(5.2), Inches(0.4), "Recursive (structure-aware)", size=16, bold=True, color=OK)
    add_text_box(s, Inches(7.2), Inches(3.1), Inches(5.2), Inches(3.0),
                 "Chunk 1 → ## Refunds + body\n\nChunk 2 → ## Shipping + body\n\nEach retrieval returns a complete topic.",
                 size=14, color=INK)

    # ========== 14. Semantic ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "04 · Semantic chunking", "Split when meaning shifts — not when a counter hits N")
    add_round_rect(s, Inches(0.55), Inches(2.15), Inches(12.2), Inches(1.3), TEAL_LIGHT)
    add_text_box(s, Inches(0.9), Inches(2.45), Inches(11.5), Inches(0.7),
                 "Embed consecutive sentences. When cosine similarity drops below a threshold, start a new chunk.", size=16, color=INK)

    cols = [
        ("Idea", "Group by topic coherence"),
        ("Cost", "Extra embedding passes at index time"),
        ("Win", "Better units for mixed / narrative docs"),
        ("Watch", "Threshold tuning is data-dependent"),
    ]
    for i, (t, b) in enumerate(cols):
        x = Inches(0.55) + Inches(i * 3.15)
        add_round_rect(s, x, Inches(3.7), Inches(3.0), Inches(2.5), WHITE)
        add_text_box(s, x + Inches(0.2), Inches(4.0), Inches(2.6), Inches(0.4), t, size=16, bold=True, color=TEAL)
        add_text_box(s, x + Inches(0.2), Inches(4.55), Inches(2.6), Inches(1.3), b, size=14, color=INK)

    # ========== 15. Semantic example ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Example · Semantic split on a blog post", "One article, three topics → three chunks")
    topics = [
        ("Chunk A · Product launch", "We shipped v2.0 with offline sync…"),
        ("Chunk B · Pricing change", "Starting May 1, Pro is $29/mo…"),
        ("Chunk C · Hiring", "We're hiring two backend engineers…"),
    ]
    for i, (t, b) in enumerate(topics):
        y = Inches(2.2) + Inches(i * 1.45)
        add_round_rect(s, Inches(0.55), y, Inches(12.2), Inches(1.25), WHITE)
        add_rect(s, Inches(0.55), y, Inches(0.15), Inches(1.25), TEAL)
        add_text_box(s, Inches(1.0), y + Inches(0.25), Inches(11), Inches(0.35), t, size=16, bold=True, color=INK)
        add_text_box(s, Inches(1.0), y + Inches(0.7), Inches(11), Inches(0.35), b, size=14, color=MUTED)

    # ========== 16. Parent-child ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "05 · Parent–child (small-to-big)", "Retrieve precise child chunks; expand to parent for generation")
    add_round_rect(s, Inches(0.55), Inches(2.15), Inches(6.0), Inches(4.3), WHITE)
    add_text_box(s, Inches(0.9), Inches(2.45), Inches(5.4), Inches(0.4), "Pattern", size=16, bold=True, color=TEAL)
    add_bullets(s, Inches(0.85), Inches(3.05), Inches(5.4), Inches(3.1), [
        "Child: small (sentence / paragraph) for accurate search",
        "Parent: section / page for rich LLM context",
        "On hit: fetch parent_id → inject full parent",
        "Also called hierarchical / multi-granularity RAG",
    ], size=15, spacing=12)

    add_round_rect(s, Inches(6.85), Inches(2.15), Inches(5.9), Inches(4.3), INK)
    add_text_box(s, Inches(7.2), Inches(2.5), Inches(5.2), Inches(0.4), "Example layout", size=14, bold=True, color=TEAL)
    add_round_rect(s, Inches(7.2), Inches(3.2), Inches(5.2), Inches(1.0), TEAL)
    add_text_box(s, Inches(7.4), Inches(3.45), Inches(4.8), Inches(0.5), "PARENT · §3 Security Policy (full section)", size=13, bold=True, color=WHITE)
    for i, label in enumerate(["Child 3.1 MFA required", "Child 3.2 VPN only", "Child 3.3 Device wipe"]):
        y = Inches(4.45) + Inches(i * 0.55)
        add_round_rect(s, Inches(7.6), y, Inches(4.4), Inches(0.45), INK_SOFT)
        add_text_box(s, Inches(7.8), y + Inches(0.05), Inches(4.0), Inches(0.35), label, size=12, color=WHITE)

    # ========== 17. Proposition ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "06 · Proposition / atomic chunking", "Rewrite text into standalone facts, then embed each fact")
    add_round_rect(s, Inches(0.55), Inches(2.15), Inches(12.2), Inches(1.4), TEAL_LIGHT)
    add_text_box(s, Inches(0.9), Inches(2.45), Inches(11.5), Inches(0.85),
                 "Use an LLM to extract propositions that are self-contained (no \"it / this / the above\"). Great for Q&A over dense reports.", size=16, color=INK)

    add_round_rect(s, Inches(0.55), Inches(3.8), Inches(5.9), Inches(2.6), WHITE)
    add_text_box(s, Inches(0.9), Inches(4.05), Inches(5.3), Inches(0.35), "Original", size=14, bold=True, color=MUTED)
    add_text_box(s, Inches(0.9), Inches(4.55), Inches(5.3), Inches(1.5),
                 "The Acme Plan covers dental after a 6-month wait and vision after 90 days for full-time staff.", size=14, color=INK)

    add_round_rect(s, Inches(6.85), Inches(3.8), Inches(5.9), Inches(2.6), WHITE)
    add_text_box(s, Inches(7.2), Inches(4.05), Inches(5.3), Inches(0.35), "Propositions", size=14, bold=True, color=TEAL)
    add_bullets(s, Inches(7.15), Inches(4.5), Inches(5.3), Inches(1.7), [
        "Acme Plan: dental after 6 months",
        "Acme Plan: vision after 90 days",
        "Eligibility: full-time staff only",
    ], size=14, spacing=8)
    # ========== 17b. Parent-child — the problem ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Parent–child · Why it exists", "You are stuck between two bad options — this strategy uses both on purpose")
    add_round_rect(s, Inches(0.55), Inches(2.15), Inches(5.9), Inches(4.3), WHITE)
    add_rect(s, Inches(0.55), Inches(2.15), Inches(5.9), Inches(0.12), DANGER)
    add_text_box(s, Inches(0.9), Inches(2.5), Inches(5.2), Inches(0.4), "Big chunks (whole section)", size=17, bold=True, color=DANGER)
    add_bullets(s, Inches(0.85), Inches(3.15), Inches(5.3), Inches(2.8), [
        "Easy to find the right topic area",
        "Too much noise in the embedding",
        "LLM gets 2 pages when it needed 1 sentence",
        "Retrieval rank is diluted by extra text",
    ], size=14, spacing=10)

    add_round_rect(s, Inches(6.85), Inches(2.15), Inches(5.9), Inches(4.3), WHITE)
    add_rect(s, Inches(6.85), Inches(2.15), Inches(5.9), Inches(0.12), ACCENT)
    add_text_box(s, Inches(7.2), Inches(2.5), Inches(5.2), Inches(0.4), "Small chunks (one sentence)", size=17, bold=True, color=ACCENT)
    add_bullets(s, Inches(7.15), Inches(3.15), Inches(5.3), Inches(2.8), [
        "Very precise vector match",
        "\"It expires in 30 days\" — what is \"it\"?",
        "Missing definitions and exceptions",
        "Hard to cite a meaningful source block",
    ], size=14, spacing=10)

    add_round_rect(s, Inches(0.55), Inches(6.55), Inches(12.2), Inches(0.55), TEAL_LIGHT)
    add_text_box(s, Inches(0.85), Inches(6.65), Inches(11.6), Inches(0.35),
                 "Fix: search with small children · answer with the full parent section", size=15, bold=True, color=TEAL)

    # ========== 17c. Parent-child — worked example ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Parent–child · Worked example", "Handbook §3 Remote Work — one parent, four searchable children")
    add_round_rect(s, Inches(0.55), Inches(2.05), Inches(12.2), Inches(1.55), INK)
    add_text_box(s, Inches(0.85), Inches(2.2), Inches(11.6), Inches(0.3), "PARENT (stored for generation, not embedded)", size=11, bold=True, color=TEAL)
    add_text_box(s, Inches(0.85), Inches(2.55), Inches(11.6), Inches(0.95),
                 "§3 Remote Work: up to 3 days/week remote · manager approval by Friday · $500/yr equipment stipend · security training before VPN access.",
                 size=14, color=WHITE)

    children_pc = [
        ("C1", "Remote work allowed up to 3 days per week", "§3"),
        ("C2", "Manager must approve remote schedule by Friday", "§3"),
        ("C3", "Equipment stipend is $500 per year", "§3"),
        ("C4", "Security training required before VPN access", "§3"),
    ]
    headers_pc = ["Child", "Embedded text (search index)", "parent_id"]
    for i, h in enumerate(headers_pc):
        x = Inches(0.55) + Inches(i * 4.2)
        add_rect(s, x, Inches(3.85), Inches(4.0), Inches(0.45), TEAL)
        add_text_box(s, x + Inches(0.1), Inches(3.92), Inches(3.8), Inches(0.3), h, size=12, bold=True, color=WHITE)
    for r, row in enumerate(children_pc):
        y = Inches(4.35) + Inches(r * 0.62)
        bgc = WHITE if r % 2 == 0 else TEAL_LIGHT
        for i, cell in enumerate(row):
            x = Inches(0.55) + Inches(i * 4.2)
            add_rect(s, x, y, Inches(4.0), Inches(0.58), bgc)
            add_text_box(s, x + Inches(0.1), y + Inches(0.12), Inches(3.8), Inches(0.35), cell, size=12, bold=(i == 0), color=INK)

    add_round_rect(s, Inches(0.55), Inches(6.85), Inches(12.2), Inches(0.35), TEAL_LIGHT)
    add_text_box(s, Inches(0.85), Inches(6.9), Inches(11.6), Inches(0.25),
                 "Analogy: children = book index entries · parent = the full page you actually read", size=13, color=INK)

    # ========== 17d. Parent-child — retrieval flow ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Parent–child · Retrieval flow", "Query: \"How much is the equipment stipend?\"")
    flow_pc = [
        ("1", "User question", "How much is the equipment stipend?"),
        ("2", "Vector search", "Matches child C3 — highest similarity score"),
        ("3", "Read parent_id", "C3 points to parent §3 Remote Work"),
        ("4", "Fetch parent", "Load full §3 section (all 4 rules) into the prompt"),
        ("5", "LLM answer", "\"$500 per year\" — with policy context if needed"),
    ]
    for i, (num, title, detail) in enumerate(flow_pc):
        y = Inches(2.05) + Inches(i * 0.95)
        add_round_rect(s, Inches(0.55), y, Inches(12.2), Inches(0.82), WHITE)
        add_ellipse = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.85), y + Inches(0.18), Inches(0.45), Inches(0.45))
        fill_shape(add_ellipse, TEAL)
        add_text_box(s, Inches(0.85), y + Inches(0.23), Inches(0.45), Inches(0.35), num, size=13, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        add_text_box(s, Inches(1.55), y + Inches(0.12), Inches(2.2), Inches(0.35), title, size=14, bold=True, color=TEAL)
        add_text_box(s, Inches(3.9), y + Inches(0.12), Inches(8.5), Inches(0.55), detail, size=14, color=INK)
        if i < len(flow_pc) - 1:
            add_text_box(s, Inches(1.0), y + Inches(0.78), Inches(0.4), Inches(0.25), "↓", size=14, bold=True, color=MUTED)

    add_round_rect(s, Inches(0.55), Inches(6.85), Inches(12.2), Inches(0.35), TEAL_LIGHT)
    add_text_box(s, Inches(0.85), Inches(6.9), Inches(11.6), Inches(0.25),
                 "Best for: long manuals, policies, API docs — precise search + rich answers", size=13, bold=True, color=INK)

    # ========== 17d2. Parent-child — what gets embedded ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Parent–child · What gets embedded?", "Usually: embed children only · store parents as linked text (not in the search index)")

    embed_headers = ["Piece", "Embedded?", "Stored where", "Used for"]
    embed_rows = [
        ["Child (sentence / paragraph)", "Yes ✓", "Vector DB", "Search — find best match"],
        ["Parent (full section)", "No ✗ (typical)", "DB / doc store", "Context — sent to LLM after hit"],
    ]
    y0 = Inches(2.05)
    col_w = [Inches(3.5), Inches(1.5), Inches(2.5), Inches(4.2)]
    col_x = [Inches(0.55)]
    for w in col_w[:-1]:
        col_x.append(col_x[-1] + w)
    for i, h in enumerate(embed_headers):
        add_rect(s, col_x[i], y0, col_w[i], Inches(0.48), INK)
        add_text_box(s, col_x[i] + Inches(0.08), y0 + Inches(0.1), col_w[i] - Inches(0.12), Inches(0.3), h, size=12, bold=True, color=WHITE)
    for r, row in enumerate(embed_rows):
        y = y0 + Inches(0.48) + Inches(r * 0.72)
        bgc = WHITE if r == 0 else TEAL_LIGHT
        for i, cell in enumerate(row):
            add_rect(s, col_x[i], y, col_w[i], Inches(0.68), bgc)
            tc = OK if "Yes" in cell else (DANGER if "No" in cell else INK)
            add_text_box(s, col_x[i] + Inches(0.08), y + Inches(0.15), col_w[i] - Inches(0.12), Inches(0.45), cell, size=12, bold=(i == 1), color=tc if i == 1 else INK)

    add_round_rect(s, Inches(0.55), Inches(3.35), Inches(12.2), Inches(0.55), TEAL_LIGHT)
    add_text_box(s, Inches(0.85), Inches(3.45), Inches(11.6), Inches(0.35),
                 "Why not embed parents too? Duplicate results · noisier search · unclear whether to send parent or child to the LLM",
                 size=13, color=INK)

    add_round_rect(s, Inches(0.55), Inches(4.05), Inches(6.0), Inches(2.55), WHITE)
    add_text_box(s, Inches(0.9), Inches(4.25), Inches(5.4), Inches(0.35), "Index time", size=14, bold=True, color=TEAL)
    add_bullets(s, Inches(0.85), Inches(4.7), Inches(5.4), Inches(1.7), [
        "Save parent §3 as text + parent_id",
        "Embed children C1–C4; each stores parent_id = §3",
        "Parent is not added to the vector search index",
    ], size=13, spacing=8)

    add_round_rect(s, Inches(6.85), Inches(4.05), Inches(5.9), Inches(2.55), WHITE)
    add_text_box(s, Inches(7.2), Inches(4.25), Inches(5.2), Inches(0.35), "Query time", size=14, bold=True, color=TEAL)
    add_bullets(s, Inches(7.15), Inches(4.7), Inches(5.2), Inches(1.7), [
        "Vector search runs on children only",
        "Hit child C3 → read parent_id → fetch parent text",
        "Send full parent section to the LLM (best practice)",
    ], size=13, spacing=8)

    add_round_rect(s, Inches(0.55), Inches(6.75), Inches(12.2), Inches(0.45), INK)
    add_text_box(s, Inches(0.85), Inches(6.82), Inches(11.6), Inches(0.3),
                 "Mental model: children = search snippets · parent = full page you open after the match", size=14, bold=True, color=WHITE)

    # ========== 17e. Proposition — the problem ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Proposition · Why it exists", "Normal chunks still pack multiple facts and vague pronouns into one embedding")
    add_round_rect(s, Inches(0.55), Inches(2.15), Inches(6.0), Inches(2.2), WHITE)
    add_text_box(s, Inches(0.9), Inches(2.4), Inches(5.4), Inches(0.35), "Problems with normal chunks", size=15, bold=True, color=DANGER)
    add_bullets(s, Inches(0.85), Inches(2.9), Inches(5.4), Inches(1.2), [
        "Several facts in one paragraph → noisy retrieval",
        "Pronouns (\"it\", \"this\") embed poorly",
        "User asks about 1 fact, gets 3 unrelated facts",
    ], size=14, spacing=8)

    add_round_rect(s, Inches(0.55), Inches(4.55), Inches(6.0), Inches(2.0), TEAL_LIGHT)
    add_text_box(s, Inches(0.9), Inches(4.75), Inches(5.4), Inches(0.35), "The fix", size=15, bold=True, color=TEAL)
    add_text_box(s, Inches(0.9), Inches(5.2), Inches(5.4), Inches(1.1),
                 "Rewrite each fact as a standalone sentence. One fact = one chunk. No pronouns without a named subject.",
                 size=14, color=INK)

    add_round_rect(s, Inches(6.85), Inches(2.15), Inches(5.9), Inches(4.4), WHITE)
    add_text_box(s, Inches(7.2), Inches(2.4), Inches(5.2), Inches(0.35), "Bad vs good proposition", size=15, bold=True, color=TEAL)
    examples_prop = [
        ("✗", "It covers dental after 6 months.", DANGER),
        ("✓", "Acme Plan covers dental after a 6-month wait.", OK),
        ("✗", "Vision is after 90 days for FT staff.", DANGER),
        ("✓", "Acme Plan covers vision after 90 days for full-time employees.", OK),
    ]
    for i, (mark, text, col) in enumerate(examples_prop):
        y = Inches(2.95) + Inches(i * 0.95)
        add_text_box(s, Inches(7.2), y, Inches(0.35), Inches(0.35), mark, size=14, bold=True, color=col)
        add_text_box(s, Inches(7.65), y, Inches(4.8), Inches(0.75), text, size=13, color=INK)

    # ========== 17f. Proposition — worked example + retrieval ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Proposition · Worked example + retrieval", "Query: \"When does vision coverage start?\"")
    add_round_rect(s, Inches(0.55), Inches(2.05), Inches(5.9), Inches(1.35), WHITE)
    add_text_box(s, Inches(0.9), Inches(2.25), Inches(5.3), Inches(0.3), "Original paragraph", size=12, bold=True, color=MUTED)
    add_text_box(s, Inches(0.9), Inches(2.6), Inches(5.3), Inches(0.65),
                 "The Acme Plan covers dental after a 6-month wait and vision after 90 days for full-time staff.",
                 size=14, color=INK)

    props = [
        "P1: Acme Plan provides dental coverage after a 6-month waiting period.",
        "P2: Acme Plan provides vision coverage after a 90-day waiting period.",
        "P3: Acme Plan benefits require full-time employee status.",
    ]
    add_round_rect(s, Inches(6.85), Inches(2.05), Inches(5.9), Inches(3.5), WHITE)
    add_text_box(s, Inches(7.2), Inches(2.25), Inches(5.3), Inches(0.3), "Atomic propositions (each embedded separately)", size=12, bold=True, color=TEAL)
    for i, p in enumerate(props):
        y = Inches(2.75) + Inches(i * 0.95)
        add_round_rect(s, Inches(7.15), y, Inches(5.4), Inches(0.78), TEAL_LIGHT if i == 1 else WHITE)
        add_text_box(s, Inches(7.35), y + Inches(0.18), Inches(5.0), Inches(0.45), p, size=13, bold=(i == 1), color=INK)

    add_round_rect(s, Inches(0.55), Inches(3.65), Inches(5.9), Inches(2.9), INK)
    add_text_box(s, Inches(0.9), Inches(3.9), Inches(5.3), Inches(0.35), "What retrieval returns", size=14, bold=True, color=TEAL)
    add_bullets(s, Inches(0.85), Inches(4.4), Inches(5.3), Inches(2.0), [
        "Vector search hits P2 only (vision wait period)",
        "Not P1 (dental) or P3 (eligibility) — less noise",
        "LLM answers: \"90 days after start\"",
        "Normal chunking would return the whole paragraph",
    ], size=13, color=WHITE, spacing=10)

    add_round_rect(s, Inches(0.55), Inches(6.75), Inches(12.2), Inches(0.45), TEAL_LIGHT)
    add_text_box(s, Inches(0.85), Inches(6.82), Inches(11.6), Inches(0.3),
                 "Index time: often use an LLM to extract propositions · Best for: benefits FAQs, compliance rules, product specs", size=13, color=INK)

    # ========== 18. Comparison ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Strategy comparison at a glance", "Pick for quality first — optimize cost second")
    headers = ["Strategy", "Precision", "Context", "Cost", "Best fit"]
    rows = [
        ["Fixed-size", "Medium", "Variable", "Low", "Prototypes, flat text"],
        ["Overlap", "Higher", "Better", "Low+", "Narrative / policies"],
        ["Recursive", "High", "High", "Low", "Structured docs"],
        ["Semantic", "High", "High", "Med", "Mixed topics"],
        ["Parent–child", "Very high", "Very high", "Med", "Long manuals"],
        ["Proposition", "Very high", "Low→expand", "High", "Factoid Q&A"],
    ]
    # header row
    y0 = Inches(2.1)
    for i, h in enumerate(headers):
        x = Inches(0.55) + Inches(i * 2.45)
        w = Inches(2.35)
        add_rect(s, x, y0, w, Inches(0.5), INK)
        add_text_box(s, x + Inches(0.1), y0 + Inches(0.1), w - Inches(0.15), Inches(0.35), h, size=13, bold=True, color=WHITE)
    for r, row in enumerate(rows):
        y = y0 + Inches(0.5) + Inches(r * 0.65)
        bgc = WHITE if r % 2 == 0 else TEAL_LIGHT
        for i, cell in enumerate(row):
            x = Inches(0.55) + Inches(i * 2.45)
            add_rect(s, x, y, Inches(2.35), Inches(0.65), bgc)
            add_text_box(s, x + Inches(0.1), y + Inches(0.15), Inches(2.15), Inches(0.4), cell, size=12, bold=(i == 0), color=INK)

    # Update total — we have more slides. Let me recount and continue with more slides.
    # Actually I'll continue adding application slides and fix footer numbers at the end.
    # Better: keep building and set total dynamically at save... For now continue with correct numbering.

    # ========== 19. Decision guide ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "How to choose a strategy", "Start simple; upgrade when retrieval evals fail")
    rules = [
        ("Most docs have headings?", "→ Recursive (+ light overlap)"),
        ("Long chapters, precise Qs?", "→ Parent–child"),
        ("Mixed topics in one file?", "→ Semantic"),
        ("Need exact factual answers?", "→ Proposition / atomic"),
        ("Shipping an MVP this week?", "→ Fixed-size + 10–15% overlap"),
    ]
    for i, (q, a) in enumerate(rules):
        y = Inches(2.15) + Inches(i * 0.85)
        add_round_rect(s, Inches(0.55), y, Inches(12.2), Inches(0.75), WHITE)
        add_text_box(s, Inches(0.9), y + Inches(0.18), Inches(6.5), Inches(0.45), q, size=16, bold=True, color=INK)
        add_text_box(s, Inches(7.5), y + Inches(0.18), Inches(5), Inches(0.45), a, size=16, color=TEAL)

    # ========== 20. Applications ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Applications · where chunking shows up", "Same RAG idea — different chunk designs")
    apps = [
        ("Customer support bot", "Recursive on help center +\noverlap on long articles", "Retrieve article section → cite URL"),
        ("Legal / compliance", "Parent–child on contracts;\nclause = child", "Precise clause hits + full section context"),
        ("Codebase assistant", "Chunk by function / class\n(+ file as parent)", "Don't split mid-function"),
        ("Research / papers", "Semantic by section; keep\nabstracts whole", "Methods vs results stay separate"),
        ("HR policies", "Recursive by heading +\nproposition for benefits tables", "\"Does dental cover…?\" style Qs"),
        ("Internal search", "Fixed + metadata filters\n(team, date, product)", "Hybrid keyword + vector"),
    ]
    for i, (t, how, why) in enumerate(apps):
        row, col = divmod(i, 3)
        x = Inches(0.55) + Inches(col * 4.2)
        y = Inches(2.15) + Inches(row * 2.35)
        add_round_rect(s, x, y, Inches(4.0), Inches(2.15), WHITE)
        add_text_box(s, x + Inches(0.2), y + Inches(0.2), Inches(3.6), Inches(0.35), t, size=14, bold=True, color=TEAL)
        add_text_box(s, x + Inches(0.2), y + Inches(0.65), Inches(3.6), Inches(0.7), how, size=12, color=INK)
        add_text_box(s, x + Inches(0.2), y + Inches(1.45), Inches(3.6), Inches(0.5), why, size=11, color=MUTED)

    # ========== 21. Worked application ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Worked application · Employee handbook Q&A", "One corpus, three query types → three chunk tactics")
    rows2 = [
        ("Query type", "Example", "Chunk strategy"),
        ("Policy lookup", "\"How many remote days?\"", "Recursive by section"),
        ("Multi-fact", "\"Stipend + approval owner?\"", "Overlap or parent–child"),
        ("Benefits factoid", "\"Vision wait period?\"", "Proposition chunks"),
    ]
    for r, row in enumerate(rows2):
        y = Inches(2.2) + Inches(r * 1.05)
        bgc = INK if r == 0 else WHITE
        tc = WHITE if r == 0 else INK
        for i, cell in enumerate(row):
            x = Inches(0.55) + Inches(i * 4.2)
            add_round_rect(s, x, y, Inches(4.0), Inches(0.9), bgc)
            add_text_box(s, x + Inches(0.2), y + Inches(0.25), Inches(3.6), Inches(0.45), cell, size=14, bold=(r == 0 or i == 0), color=tc)

    # ========== 22. Pitfalls ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Common pitfalls", "Chunking bugs look like \"the model is dumb\"")
    pitfalls = [
        ("Ignoring metadata", "Always store source, heading path, page, timestamps."),
        ("One size for all file types", "PDFs ≠ chat logs ≠ code. Specialize per source."),
        ("No evaluation set", "Build 20–50 real questions; measure recall@k."),
        ("Chunking at generation time", "Index-time chunks must match query-time retrieval."),
        ("Orphan pronouns", "\"It expires in 30 days\" without what \"it\" is."),
        ("Over-chunking tables", "Keep tables / lists together or summarize them."),
    ]
    for i, (t, b) in enumerate(pitfalls):
        row, col = divmod(i, 2)
        x = Inches(0.55) + Inches(col * 6.3)
        y = Inches(2.15) + Inches(row * 1.5)
        add_round_rect(s, x, y, Inches(6.05), Inches(1.35), WHITE)
        add_text_box(s, x + Inches(0.3), y + Inches(0.25), Inches(5.5), Inches(0.35), t, size=15, bold=True, color=DANGER)
        add_text_box(s, x + Inches(0.3), y + Inches(0.7), Inches(5.5), Inches(0.45), b, size=13, color=MUTED)

    # ========== 23. Best practices ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Teaching checklist · best practices", "Use this as a lab rubric")
    checks = [
        "Match chunk size to embedding model context (often 256–1024 tokens)",
        "Prefer structure-aware splits over blind character cuts",
        "Add 10–20% overlap when answers span boundaries",
        "Attach rich metadata for filters and citations",
        "Evaluate with real user questions before tuning prompts",
        "Re-chunk when document structure or product domain changes",
        "Log retrieved chunks during demos — teach with evidence",
    ]
    for i, c in enumerate(checks):
        y = Inches(2.1) + Inches(i * 0.65)
        add_round_rect(s, Inches(0.55), y, Inches(12.2), Inches(0.55), WHITE)
        add_text_box(s, Inches(0.85), y + Inches(0.1), Inches(0.5), Inches(0.35), "✓", size=16, bold=True, color=OK)
        add_text_box(s, Inches(1.5), y + Inches(0.1), Inches(10.8), Inches(0.35), c, size=15, color=INK)

    # ========== 24. Lab exercise ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Classroom lab (30–45 min)", "Hands-on: same corpus, competing chunkers")
    steps_lab = [
        ("1", "Pick a short handbook or README (~5–10 pages)"),
        ("2", "Build three indexes: fixed, recursive, parent–child"),
        ("3", "Write 10 questions (5 easy, 3 multi-hop, 2 adversarial)"),
        ("4", "Score recall@3 and answer correctness"),
        ("5", "Discuss: which strategy won — and why for which query?"),
    ]
    for i, (n, t) in enumerate(steps_lab):
        y = Inches(2.15) + Inches(i * 0.85)
        add_round_rect(s, Inches(0.55), y, Inches(12.2), Inches(0.75), WHITE)
        add_ellipse = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.85), y + Inches(0.15), Inches(0.45), Inches(0.45))
        fill_shape(add_ellipse, TEAL)
        add_text_box(s, Inches(0.85), y + Inches(0.2), Inches(0.45), Inches(0.4), n, size=14, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        add_text_box(s, Inches(1.6), y + Inches(0.18), Inches(10.8), Inches(0.45), t, size=17, color=INK)

    # ========== 25. Key takeaways ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Key takeaways", "What students should leave remembering")
    takes = [
        ("RAG grounds LLMs", "Retrieve → Augment → Generate"),
        ("Chunking is a product decision", "Not just a preprocessing detail"),
        ("Structure beats blind cuts", "Headings, parents, propositions"),
        ("Measure, then upgrade", "Eval questions before fancy chunkers"),
    ]
    for i, (t, b) in enumerate(takes):
        x = Inches(0.55) + Inches((i % 2) * 6.3)
        y = Inches(2.2) + Inches((i // 2) * 2.2)
        add_round_rect(s, x, y, Inches(6.05), Inches(1.95), WHITE)
        add_rect(s, x, y, Inches(0.15), Inches(1.95), TEAL)
        add_text_box(s, x + Inches(0.45), y + Inches(0.45), Inches(5.3), Inches(0.45), t, size=20, bold=True, color=INK)
        add_text_box(s, x + Inches(0.45), y + Inches(1.1), Inches(5.3), Inches(0.5), b, size=15, color=MUTED)

    # ========== 26. Closing ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, INK)
    add_rect(s, Inches(0), Inches(0), Inches(0.25), SLIDE_H, TEAL)
    add_text_box(s, Inches(0.7), Inches(2.3), Inches(11), Inches(0.5), "NEXT UP", size=14, bold=True, color=TEAL)
    add_text_box(s, Inches(0.7), Inches(2.9), Inches(11.5), Inches(1.2), "Embeddings, retrieval,\nand evaluation", size=40, bold=True, color=WHITE)
    add_text_box(s, Inches(0.7), Inches(5.0), Inches(11), Inches(0.6),
                 "Questions? Try the lab — then we'll score your chunkers.", size=18, color=RGBColor(0xB8, 0xC4, 0xD0))

    n = len(prs.slides)
    for i in range(1, n - 1):
        footer(prs.slides[i], i + 1, n)

    out = "/Users/khurramnaqi/Documents/Samiaa Learning/teaching/RAG_Chunking_Strategies.pptx"
    prs.save(out)
    return out, n


if __name__ == "__main__":
    path, n = build()
    print(f"Wrote {n} slides → {path}")
