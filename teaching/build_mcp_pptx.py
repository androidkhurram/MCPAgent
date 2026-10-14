#!/usr/bin/env python3
"""Generate a visual, example-driven MCP teaching deck with end-to-end flow."""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# --- Palette (ink + teal teaching theme — matches RAG decks) ---
INK = RGBColor(0x14, 0x1E, 0x2A)
TEAL = RGBColor(0x0C, 0x7C, 0x7C)
TEAL_LIGHT = RGBColor(0xE6, 0xF4, 0xF4)
PAPER = RGBColor(0xF8, 0xF6, 0xF3)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
MUTED = RGBColor(0x5A, 0x66, 0x75)
ACCENT = RGBColor(0xD4, 0x7A, 0x2A)
OK = RGBColor(0x2E, 0x7D, 0x4F)
DANGER = RGBColor(0xB5, 0x3A, 0x3A)
BLUE = RGBColor(0x2F, 0x5D, 0x8A)
PURPLE = RGBColor(0x5B, 0x4B, 0x8A)  # used sparingly for 3rd role only

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)


def set_run(run, size, bold=False, color=INK, font="Calibri"):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = font


def add_text_box(slide, left, top, width, height, text, size=18, bold=False, color=INK, align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    set_run(run, size, bold=bold, color=color)
    return box


def add_bullets(slide, left, top, width, height, items, size=16, color=INK, spacing=10):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
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


def add_round_rect(slide, left, top, width, height, color, radius=0.12):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    fill_shape(shape, color)
    try:
        shape.adjustments[0] = radius
    except Exception:
        pass
    return shape


def add_oval(slide, left, top, width, height, color):
    shape = slide.shapes.add_shape(MSO_SHAPE.OVAL, left, top, width, height)
    fill_shape(shape, color)
    return shape


def accent_bar(slide, color=TEAL):
    add_rect(slide, Inches(0), Inches(0), Inches(0.18), SLIDE_H, color)


def set_bg(slide, color):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def footer(slide, page, total):
    add_text_box(slide, Inches(11.4), Inches(7.05), Inches(1.6), Inches(0.35),
                 f"{page}  /  {total}", size=11, color=MUTED, align=PP_ALIGN.RIGHT)
    add_text_box(slide, Inches(0.55), Inches(7.05), Inches(6), Inches(0.35),
                 "MCP · Visual End-to-End Guide", size=11, color=MUTED)


def section_label(slide, text):
    add_text_box(slide, Inches(0.55), Inches(0.28), Inches(10), Inches(0.3),
                 text.upper(), size=11, bold=True, color=TEAL)


def title_block(slide, title, subtitle=None):
    section_label(slide, "Learning module")
    add_text_box(slide, Inches(0.55), Inches(0.55), Inches(12), Inches(0.55),
                 title, size=28, bold=True, color=INK)
    if subtitle:
        add_text_box(slide, Inches(0.55), Inches(1.15), Inches(12), Inches(0.35),
                     subtitle, size=15, color=MUTED)


def pill(slide, left, top, width, height, text, bg, fg=WHITE, size=13):
    add_round_rect(slide, left, top, width, height, bg, radius=0.5)
    add_text_box(slide, left, top + Inches(0.06), width, height - Inches(0.05),
                 text, size=size, bold=True, color=fg, align=PP_ALIGN.CENTER)


def arrow(slide, left, top, text="→"):
    add_text_box(slide, left, top, Inches(0.55), Inches(0.4),
                 text, size=22, bold=True, color=TEAL, align=PP_ALIGN.CENTER)


def step_chip(slide, left, top, num, color=TEAL):
    add_oval(slide, left, top, Inches(0.42), Inches(0.42), color)
    add_text_box(slide, left, top + Inches(0.04), Inches(0.42), Inches(0.35),
                 str(num), size=13, bold=True, color=WHITE, align=PP_ALIGN.CENTER)


def flow_box(slide, left, top, width, height, title, lines, header_color=TEAL):
    add_round_rect(slide, left, top, width, height, WHITE)
    add_rect(slide, left, top, width, Inches(0.42), header_color)
    add_text_box(slide, left + Inches(0.1), top + Inches(0.05), width - Inches(0.2), Inches(0.35),
                 title, size=13, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    y = top + Inches(0.55)
    for line in lines:
        add_text_box(slide, left + Inches(0.15), y, width - Inches(0.3), Inches(0.32),
                     line, size=12, color=MUTED, align=PP_ALIGN.CENTER)
        y += Inches(0.3)


def build():
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H
    blank = prs.slide_layouts[6]

    # ========== 1. Title ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, INK)
    add_rect(s, Inches(0), Inches(0), Inches(0.28), SLIDE_H, TEAL)
    add_text_box(s, Inches(0.7), Inches(1.6), Inches(11), Inches(0.35),
                 "VISUAL LEARNING DECK", size=13, bold=True, color=TEAL)
    add_text_box(s, Inches(0.7), Inches(2.15), Inches(12), Inches(1.1),
                 "Model Context Protocol", size=42, bold=True, color=WHITE)
    add_text_box(s, Inches(0.7), Inches(3.35), Inches(11.5), Inches(0.55),
                 "See the whole end-to-end flow — with a real flight-finder example", size=18, color=RGBColor(0xB8, 0xC4, 0xD0))

    # mini visual strip
    for i, (label, col) in enumerate([("Host", TEAL), ("Client", ACCENT), ("Server", OK), ("Tools", BLUE)]):
        x = Inches(0.7) + Inches(i * 2.9)
        add_round_rect(s, x, Inches(4.6), Inches(2.6), Inches(0.7), col)
        add_text_box(s, x, Inches(4.72), Inches(2.6), Inches(0.45), label, size=16, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        if i < 3:
            add_text_box(s, x + Inches(2.5), Inches(4.7), Inches(0.5), Inches(0.4), "→", size=18, bold=True, color=WHITE)

    add_text_box(s, Inches(0.7), Inches(5.8), Inches(11), Inches(0.35),
                 "Samiaa Learning  ·  Agents · Tools · Azure Foundry path", size=13, color=MUTED)

    # ========== 2. Agenda visual ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Today’s journey", "From confusion → clear mental model → end-to-end demo story")
    journey = [
        ("A", "Problem", "Why integrations hurt"),
        ("B", "Picture", "Host · Client · Server"),
        ("C", "Primitives", "Tools · Resources · Prompts"),
        ("D", "E2E story", "Flight finder walkthrough"),
        ("E", "Compare", "RAG vs MCP"),
        ("F", "Practice", "Design lab"),
    ]
    for i, (letter, title, sub) in enumerate(journey):
        x = Inches(0.45) + Inches(i * 2.1)
        add_round_rect(s, x, Inches(2.4), Inches(1.95), Inches(3.6), WHITE)
        add_oval(s, x + Inches(0.6), Inches(2.7), Inches(0.75), Inches(0.75), TEAL)
        add_text_box(s, x + Inches(0.6), Inches(2.85), Inches(0.75), Inches(0.45), letter, size=18, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        add_text_box(s, x + Inches(0.1), Inches(3.7), Inches(1.75), Inches(0.7), title, size=15, bold=True, color=INK, align=PP_ALIGN.CENTER)
        add_text_box(s, x + Inches(0.1), Inches(4.5), Inches(1.75), Inches(1.0), sub, size=12, color=MUTED, align=PP_ALIGN.CENTER)
        if i < 5:
            add_text_box(s, x + Inches(1.85), Inches(3.9), Inches(0.35), Inches(0.4), "›", size=20, bold=True, color=TEAL)

    # ========== 3. The messy world ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Without MCP: the spaghetti problem", "Every AI app builds a custom plug for every tool")

    apps = ["Cursor", "Foundry\nAgent", "Custom\nPython bot"]
    tools = ["GitHub", "Flights\nAPI", "Files", "Slack"]
    for i, a in enumerate(apps):
        y = Inches(2.3) + Inches(i * 1.35)
        add_round_rect(s, Inches(0.6), y, Inches(2.4), Inches(1.1), DANGER)
        add_text_box(s, Inches(0.6), y + Inches(0.25), Inches(2.4), Inches(0.7), a, size=14, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    for j, t in enumerate(tools):
        x = Inches(6.8) + Inches((j % 2) * 2.9)
        y = Inches(2.3) + Inches((j // 2) * 1.8)
        add_round_rect(s, x, y, Inches(2.6), Inches(1.3), INK)
        add_text_box(s, x, y + Inches(0.35), Inches(2.6), Inches(0.7), t, size=14, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

    # messy lines as text labels
    add_round_rect(s, Inches(3.3), Inches(3.5), Inches(3.1), Inches(1.6), TEAL_LIGHT)
    add_text_box(s, Inches(3.4), Inches(3.75), Inches(2.9), Inches(1.2),
                 "12 custom\nintegrations\nN apps × M tools", size=15, bold=True, color=DANGER, align=PP_ALIGN.CENTER)

    # ========== 4. With MCP ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "With MCP: one standard plug", "Build the server once — many hosts can use it")

    for i, a in enumerate(["Cursor", "Foundry Agent", "Python bot"]):
        x = Inches(0.55) + Inches(i * 2.7)
        add_round_rect(s, x, Inches(2.3), Inches(2.45), Inches(1.0), TEAL)
        add_text_box(s, x, Inches(2.5), Inches(2.45), Inches(0.6), a, size=14, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

    add_text_box(s, Inches(3.8), Inches(3.45), Inches(2), Inches(0.4), "↓  MCP protocol  ↓", size=14, bold=True, color=TEAL, align=PP_ALIGN.CENTER)

    add_round_rect(s, Inches(2.5), Inches(3.95), Inches(8.2), Inches(0.85), ACCENT)
    add_text_box(s, Inches(2.5), Inches(4.1), Inches(8.2), Inches(0.55),
                 "Standard MCP interface  (JSON-RPC)", size=16, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

    for i, t in enumerate(["GitHub\nserver", "Flights\nserver", "Files\nserver", "Slack\nserver"]):
        x = Inches(0.7) + Inches(i * 3.15)
        add_round_rect(s, x, Inches(5.15), Inches(2.9), Inches(1.2), OK)
        add_text_box(s, x, Inches(5.4), Inches(2.9), Inches(0.8), t, size=14, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

    # ========== 5. One liner ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, INK)
    add_rect(s, Inches(0), Inches(0), Inches(0.28), SLIDE_H, TEAL)
    add_text_box(s, Inches(0.7), Inches(2.3), Inches(11), Inches(0.4), "REMEMBER THIS", size=13, bold=True, color=TEAL)
    add_text_box(s, Inches(0.7), Inches(2.9), Inches(12), Inches(1.8),
                 "MCP = USB-C for AI tools.\nOne plug shape. Many devices.", size=34, bold=True, color=WHITE)
    add_text_box(s, Inches(0.7), Inches(5.1), Inches(11), Inches(0.5),
                 "Hosts speak MCP. Servers expose capabilities. Agents get superpowers.", size=16, color=RGBColor(0xB8, 0xC4, 0xD0))

    # ========== 6. Architecture big picture ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "The 3 roles — visual map", "Every MCP setup has these pieces")

    # Host big box
    add_round_rect(s, Inches(0.5), Inches(2.0), Inches(5.4), Inches(4.5), WHITE)
    add_rect(s, Inches(0.5), Inches(2.0), Inches(5.4), Inches(0.55), TEAL)
    add_text_box(s, Inches(0.5), Inches(2.1), Inches(5.4), Inches(0.4), "HOST  =  AI Application", size=16, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_text_box(s, Inches(0.75), Inches(2.75), Inches(5), Inches(0.4), "Examples: Cursor, Claude Desktop, your app", size=13, color=MUTED)
    # clients inside host
    for i, name in enumerate(["Client A", "Client B", "Client C"]):
        y = Inches(3.35) + Inches(i * 0.9)
        add_round_rect(s, Inches(1.0), y, Inches(4.2), Inches(0.75), TEAL_LIGHT)
        add_text_box(s, Inches(1.15), y + Inches(0.18), Inches(3.9), Inches(0.45),
                     f"MCP {name}  →  one connection", size=14, bold=True, color=INK, align=PP_ALIGN.CENTER)

    # arrow
    add_text_box(s, Inches(5.9), Inches(3.8), Inches(0.7), Inches(0.5), "→", size=28, bold=True, color=TEAL, align=PP_ALIGN.CENTER)

    # Servers
    add_round_rect(s, Inches(6.7), Inches(2.0), Inches(6.0), Inches(4.5), WHITE)
    add_rect(s, Inches(6.7), Inches(2.0), Inches(6.0), Inches(0.55), OK)
    add_text_box(s, Inches(6.7), Inches(2.1), Inches(6.0), Inches(0.4), "SERVERS  =  Capability providers", size=16, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    for i, (name, detail) in enumerate([
        ("Flights MCP", "tools: search_flights, rank"),
        ("Files MCP", "resources: policy.md"),
        ("GitHub MCP", "tools: create_issue"),
    ]):
        y = Inches(2.85) + Inches(i * 1.1)
        add_round_rect(s, Inches(7.05), y, Inches(5.3), Inches(0.95), TEAL_LIGHT)
        add_text_box(s, Inches(7.25), y + Inches(0.12), Inches(5), Inches(0.35), name, size=15, bold=True, color=INK)
        add_text_box(s, Inches(7.25), y + Inches(0.48), Inches(5), Inches(0.35), detail, size=13, color=MUTED)

    # ========== 7. Primitives visual ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Three primitives (what servers expose)", "Think: Do · Read · Template")

    prims = [
        ("TOOLS", "Do something", "Model decides to call", "search_flights()\ncreate_issue()\nsend_slack()", TEAL, "⚡"),
        ("RESOURCES", "Read context", "App loads into prompt", "file://policy.md\ndb://schema\ndoc://faq", ACCENT, "📄"),
        ("PROMPTS", "Start a workflow", "User clicks / selects", "“Find best flight”\n“Summarize PRs”\n“Draft email”", OK, "📋"),
    ]
    for i, (title, job, who, ex, color, icon) in enumerate(prims):
        x = Inches(0.5) + Inches(i * 4.2)
        add_round_rect(s, x, Inches(1.95), Inches(4.0), Inches(4.6), WHITE)
        add_rect(s, x, Inches(1.95), Inches(4.0), Inches(1.1), color)
        add_text_box(s, x, Inches(2.05), Inches(4.0), Inches(0.4), icon + "  " + title, size=18, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        add_text_box(s, x, Inches(2.5), Inches(4.0), Inches(0.4), job, size=14, color=WHITE, align=PP_ALIGN.CENTER)
        add_text_box(s, x + Inches(0.25), Inches(3.3), Inches(3.5), Inches(0.35), "Who triggers?", size=12, bold=True, color=TEAL)
        add_text_box(s, x + Inches(0.25), Inches(3.65), Inches(3.5), Inches(0.4), who, size=14, color=INK)
        add_text_box(s, x + Inches(0.25), Inches(4.25), Inches(3.5), Inches(0.35), "Examples", size=12, bold=True, color=TEAL)
        add_text_box(s, x + Inches(0.25), Inches(4.65), Inches(3.5), Inches(1.4), ex, size=15, color=MUTED)

    # ========== 8. Story intro ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, INK)
    add_rect(s, Inches(0), Inches(0), Inches(0.28), SLIDE_H, ACCENT)
    add_text_box(s, Inches(0.7), Inches(2.0), Inches(11), Inches(0.4), "END-TO-END EXAMPLE", size=14, bold=True, color=ACCENT)
    add_text_box(s, Inches(0.7), Inches(2.6), Inches(12), Inches(1.4),
                 "Flight Finder Agent\nwith MCP", size=40, bold=True, color=WHITE)
    add_text_box(s, Inches(0.7), Inches(4.5), Inches(11.5), Inches(0.8),
                 "User asks for the best flight  →  agent uses MCP tools  →  ranked answer with sources",
                 size=17, color=RGBColor(0xB8, 0xC4, 0xD0))

    # ========== 9. Scenario ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Scenario", "One clear user goal")

    add_round_rect(s, Inches(0.55), Inches(2.0), Inches(12.2), Inches(1.5), TEAL_LIGHT)
    add_text_box(s, Inches(0.9), Inches(2.25), Inches(11.5), Inches(0.4), "USER SAYS", size=12, bold=True, color=TEAL)
    add_text_box(s, Inches(0.9), Inches(2.7), Inches(11.5), Inches(0.55),
                 "“Find the best flight from Islamabad to Jeddah next Friday — prefer fewest stops, under $700.”",
                 size=18, bold=True, color=INK)

    # pieces involved
    pieces = [
        ("Host", "Travel Agent UI\n(or Cursor / Foundry)", TEAL),
        ("MCP Server", "flights-mcp\n+ optional files-mcp", OK),
        ("Tools", "search_flights\nrank_flights", ACCENT),
        ("Resource", "baggage_policy.md\n(airline rules)", BLUE),
    ]
    for i, (t, b, c) in enumerate(pieces):
        x = Inches(0.55) + Inches(i * 3.2)
        add_round_rect(s, x, Inches(3.9), Inches(3.0), Inches(2.4), WHITE)
        add_rect(s, x, Inches(3.9), Inches(3.0), Inches(0.5), c)
        add_text_box(s, x, Inches(3.98), Inches(3.0), Inches(0.4), t, size=14, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        add_text_box(s, x + Inches(0.15), Inches(4.7), Inches(2.7), Inches(1.3), b, size=14, color=INK, align=PP_ALIGN.CENTER)

    # ========== 10. E2E flow overview ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "End-to-end flow (bird’s eye)", "8 steps from question → answer")

    steps = [
        ("1", "User\nasks"),
        ("2", "Host\nplans"),
        ("3", "List\ntools"),
        ("4", "Call\nsearch"),
        ("5", "API\nresults"),
        ("6", "Rank\nbest"),
        ("7", "Read\npolicy"),
        ("8", "Answer\n+ why"),
    ]
    for i, (n, label) in enumerate(steps):
        x = Inches(0.35) + Inches(i * 1.6)
        add_oval(s, x + Inches(0.4), Inches(2.5), Inches(0.7), Inches(0.7), TEAL)
        add_text_box(s, x + Inches(0.4), Inches(2.62), Inches(0.7), Inches(0.45), n, size=16, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        add_round_rect(s, x, Inches(3.5), Inches(1.45), Inches(1.5), WHITE)
        add_text_box(s, x, Inches(3.75), Inches(1.45), Inches(1.1), label, size=13, bold=True, color=INK, align=PP_ALIGN.CENTER)
        if i < 7:
            add_text_box(s, x + Inches(1.35), Inches(2.6), Inches(0.35), Inches(0.4), "→", size=16, bold=True, color=TEAL)

    add_round_rect(s, Inches(0.55), Inches(5.4), Inches(12.2), Inches(1.1), TEAL_LIGHT)
    add_text_box(s, Inches(0.85), Inches(5.65), Inches(11.6), Inches(0.6),
                 "Next slides zoom into each step with the actual messages & example data.",
                 size=16, color=INK)

    # ========== 11. Steps 1-2 ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Steps 1–2 · Ask & plan", "Host receives the request and decides it needs tools")

    flow_box(s, Inches(0.5), Inches(2.0), Inches(5.8), Inches(4.4), "① USER → HOST",
             ["", "Chat message arrives", "", "ISB → JED", "Friday", "max $700", "prefer nonstop"], TEAL)
    arrow(s, Inches(6.35), Inches(3.8))
    flow_box(s, Inches(6.9), Inches(2.0), Inches(5.8), Inches(4.4), "② HOST (LLM) THINKS",
             ["", "I need live flight data", "", "I should call:", "search_flights", "then rank_flights", "then check baggage policy"], ACCENT)

    # ========== 12. Steps 3-4 ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Steps 3–4 · Discover & call tools", "Client talks MCP to the Flights server")

    flow_box(s, Inches(0.5), Inches(2.0), Inches(5.8), Inches(4.4), "③ tools/list",
             ["", "Client asks server:", "“What can you do?”", "", "Server replies:", "• search_flights", "• rank_flights"], TEAL)
    arrow(s, Inches(6.35), Inches(3.8))
    flow_box(s, Inches(6.9), Inches(2.0), Inches(5.8), Inches(4.4), "④ tools/call",
             ["", "search_flights({", "  from: \"ISB\",", "  to: \"JED\",", "  date: \"2026-10-17\",", "  max_price: 700", "})"], ACCENT)

    # ========== 13. Step 5 results visual ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Step 5 · Tool returns structured data", "Not a web page — clean JSON the model can reason over")

    flights = [
        ("SV723", "Saudia", "Nonstop", "5h 10m", "$640", OK),
        ("PA270", "Airblue", "Nonstop", "5h 20m", "$590", TEAL),
        ("EK612+SV", "Emirates", "1 stop", "9h 40m", "$520", ACCENT),
    ]
    # header
    add_round_rect(s, Inches(0.55), Inches(2.0), Inches(12.2), Inches(0.55), INK)
    for i, h in enumerate(["Flight", "Airline", "Stops", "Duration", "Price", "Note"]):
        add_text_box(s, Inches(0.7) + Inches(i * 2.0), Inches(2.1), Inches(1.9), Inches(0.4),
                     h, size=13, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    for r, row in enumerate(flights):
        y = Inches(2.7) + Inches(r * 1.0)
        add_round_rect(s, Inches(0.55), y, Inches(12.2), Inches(0.85), WHITE)
        for i, val in enumerate(row[:5]):
            add_text_box(s, Inches(0.7) + Inches(i * 2.0), y + Inches(0.22), Inches(1.9), Inches(0.4),
                         val, size=15, bold=(i == 0), color=INK, align=PP_ALIGN.CENTER)
        pill(s, Inches(10.7), y + Inches(0.2), Inches(1.7), Inches(0.45), "from API", row[5], size=11)

    add_text_box(s, Inches(0.55), Inches(5.9), Inches(12), Inches(0.5),
                 "This is why MCP + APIs beat “browse the web and hope” for flight search.",
                 size=15, color=MUTED)

    # ========== 14. Steps 6-7 ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Steps 6–7 · Rank + read a resource", "Action tool + read-only context")

    flow_box(s, Inches(0.5), Inches(2.0), Inches(5.8), Inches(4.4), "⑥ tools/call rank_flights",
             ["", "weights:", "price 40%", "duration 30%", "stops 30%", "", "Winner: PA270", "score: 0.91"], TEAL)
    arrow(s, Inches(6.35), Inches(3.8))
    flow_box(s, Inches(6.9), Inches(2.0), Inches(5.8), Inches(4.4), "⑦ resources/read",
             ["", "URI:", "file://baggage_policy.md", "", "“Airblue ISB-JED:", "23kg checked included", "on economy.”"], ACCENT)

    # ========== 15. Step 8 final answer ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Step 8 · Final answer to the user", "Grounded in tool results + policy resource")

    add_round_rect(s, Inches(0.55), Inches(1.95), Inches(12.2), Inches(4.6), WHITE)
    add_rect(s, Inches(0.55), Inches(1.95), Inches(0.15), Inches(4.6), OK)
    add_text_box(s, Inches(1.0), Inches(2.2), Inches(11), Inches(0.4), "AGENT REPLY", size=12, bold=True, color=OK)
    add_text_box(s, Inches(1.0), Inches(2.7), Inches(11.2), Inches(3.4),
                 "Best match: Airblue PA270 — nonstop ISB→JED, ~5h 20m, $590.\n\n"
                 "Why this wins: under your $700 budget, zero stops, strong duration.\n"
                 "Runner-up: Saudia SV723 ($640) if you prefer that airline.\n\n"
                 "Baggage note (from policy): 23kg checked included on economy.\n"
                 "I can compare return dates next if you want.",
                 size=17, color=INK)

    # ========== 16. Sequence swimlane ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Sequence view (who talks to whom)", "Same story as a swimlane")

    lanes = [("User", MUTED), ("Host / LLM", TEAL), ("MCP Client", ACCENT), ("Flights Server", OK), ("Flight API", BLUE)]
    for i, (name, col) in enumerate(lanes):
        x = Inches(0.4) + Inches(i * 2.55)
        add_round_rect(s, x, Inches(1.9), Inches(2.4), Inches(0.55), col)
        add_text_box(s, x, Inches(2.0), Inches(2.4), Inches(0.4), name, size=12, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        add_rect(s, x + Inches(1.1), Inches(2.5), Inches(0.06), Inches(4.0), RGBColor(0xD8, 0xD2, 0xC8))

    # message chips across
    msgs = [
        (0, 1, "Ask for best flight", 2.7),
        (1, 2, "Need search_flights", 3.35),
        (2, 3, "tools/call", 4.0),
        (3, 4, "HTTP GET /flights", 4.65),
        (4, 3, "JSON results", 5.3),
        (3, 2, "tool result", 5.95),
        (1, 0, "Ranked answer", 6.55),
    ]
    for a, b, text, y in msgs:
        x1 = Inches(0.4) + Inches(a * 2.55) + Inches(1.1)
        x2 = Inches(0.4) + Inches(b * 2.55) + Inches(1.1)
        left = min(x1, x2)
        width = abs(x2 - x1)
        if width < Inches(1.5):
            width = Inches(2.0)
            left = left - Inches(0.3)
        add_round_rect(s, left, Inches(y), width, Inches(0.38), TEAL_LIGHT)
        add_text_box(s, left, Inches(y + 0.02), width, Inches(0.32), text, size=11, bold=True, color=INK, align=PP_ALIGN.CENTER)

    # ========== 17. Where code lives ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "What you build vs what MCP standardizes", "Concrete ownership in the flight example")

    cols = [
        ("You build", [
            "flights-mcp server",
            "search_flights tool",
            "rank_flights tool",
            "API key / auth",
            "baggage_policy.md resource",
        ], TEAL),
        ("MCP standardizes", [
            "How host discovers tools",
            "How tools are called",
            "JSON schemas / results",
            "How resources are read",
            "Same pattern in every app",
        ], ACCENT),
        ("Host provides", [
            "Chat UI",
            "LLM reasoning",
            "Tool-calling loop",
            "User approvals",
            "Guardrails / safety",
        ], OK),
    ]
    for i, (title, items, col) in enumerate(cols):
        x = Inches(0.5) + Inches(i * 4.2)
        add_round_rect(s, x, Inches(1.95), Inches(4.0), Inches(4.6), WHITE)
        add_rect(s, x, Inches(1.95), Inches(4.0), Inches(0.6), col)
        add_text_box(s, x, Inches(2.05), Inches(4.0), Inches(0.45), title, size=16, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        add_bullets(s, x + Inches(0.3), Inches(2.85), Inches(3.4), Inches(3.4), items, size=15, spacing=12)

    # ========== 18. Mini code visual ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Example: tool definition (concept)", "What the Flights MCP server advertises")

    add_round_rect(s, Inches(0.55), Inches(1.95), Inches(6.0), Inches(4.6), INK)
    add_text_box(s, Inches(0.85), Inches(2.2), Inches(5.4), Inches(0.35), "tools/list → search_flights", size=14, bold=True, color=TEAL)
    add_text_box(s, Inches(0.85), Inches(2.7), Inches(5.4), Inches(3.5),
                 '{\n'
                 '  "name": "search_flights",\n'
                 '  "description": "Find flights",\n'
                 '  "inputSchema": {\n'
                 '    "from": "string",\n'
                 '    "to": "string",\n'
                 '    "date": "YYYY-MM-DD",\n'
                 '    "max_price": "number"\n'
                 '  }\n'
                 '}',
                 size=15, color=WHITE)

    add_round_rect(s, Inches(6.9), Inches(1.95), Inches(5.9), Inches(4.6), WHITE)
    add_text_box(s, Inches(7.2), Inches(2.2), Inches(5.3), Inches(0.4), "Why this matters", size=16, bold=True, color=TEAL)
    add_bullets(s, Inches(7.2), Inches(2.85), Inches(5.3), Inches(3.3),
                [
                    "Model sees a clear contract",
                    "Host validates arguments",
                    "Same schema in Cursor or Foundry",
                    "You can swap the API behind it",
                    "No scraping brittle HTML",
                ], size=15, spacing=12)

    # ========== 19. RAG vs MCP visual ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "RAG vs MCP — same user, different jobs", "Visual contrast with our travel agent")

    # RAG side
    add_round_rect(s, Inches(0.5), Inches(1.95), Inches(6.0), Inches(4.6), WHITE)
    add_rect(s, Inches(0.5), Inches(1.95), Inches(6.0), Inches(0.6), BLUE)
    add_text_box(s, Inches(0.5), Inches(2.05), Inches(6.0), Inches(0.4), "RAG  ·  Knowledge", size=16, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    rag_flow = ["PDF / handbook", "→ chunk + embed", "→ AI Search", "→ top chunks", "→ “23kg baggage rule”"]
    for i, line in enumerate(rag_flow):
        y = Inches(2.85) + Inches(i * 0.55)
        add_round_rect(s, Inches(1.0), y, Inches(5.0), Inches(0.45), TEAL_LIGHT)
        add_text_box(s, Inches(1.0), y + Inches(0.05), Inches(5.0), Inches(0.35), line, size=14, bold=True, color=INK, align=PP_ALIGN.CENTER)

    # MCP side
    add_round_rect(s, Inches(6.85), Inches(1.95), Inches(6.0), Inches(4.6), WHITE)
    add_rect(s, Inches(6.85), Inches(1.95), Inches(6.0), Inches(0.6), TEAL)
    add_text_box(s, Inches(6.85), Inches(2.05), Inches(6.0), Inches(0.4), "MCP  ·  Tools & systems", size=16, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    mcp_flow = ["User question", "→ tools/call", "→ Flight API", "→ live prices", "→ “PA270 is best”"]
    for i, line in enumerate(mcp_flow):
        y = Inches(2.85) + Inches(i * 0.55)
        add_round_rect(s, Inches(7.35), y, Inches(5.0), Inches(0.45), TEAL_LIGHT)
        add_text_box(s, Inches(7.35), y + Inches(0.05), Inches(5.0), Inches(0.35), line, size=14, bold=True, color=INK, align=PP_ALIGN.CENTER)

    # ========== 20. Combined architecture ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Pro move: RAG + MCP together", "One agent, two powers")

    add_round_rect(s, Inches(4.5), Inches(1.95), Inches(4.3), Inches(1.0), TEAL)
    add_text_box(s, Inches(4.5), Inches(2.15), Inches(4.3), Inches(0.6), "Travel Agent (Host)", size=16, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

    # two branches
    add_text_box(s, Inches(2.8), Inches(3.1), Inches(1), Inches(0.4), "↙", size=22, bold=True, color=TEAL, align=PP_ALIGN.CENTER)
    add_text_box(s, Inches(9.3), Inches(3.1), Inches(1), Inches(0.4), "↘", size=22, bold=True, color=TEAL, align=PP_ALIGN.CENTER)

    add_round_rect(s, Inches(0.6), Inches(3.5), Inches(5.5), Inches(2.7), WHITE)
    add_rect(s, Inches(0.6), Inches(3.5), Inches(5.5), Inches(0.5), BLUE)
    add_text_box(s, Inches(0.6), Inches(3.58), Inches(5.5), Inches(0.35), "MCP tool: search_docs (RAG)", size=14, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_text_box(s, Inches(0.9), Inches(4.3), Inches(5), Inches(1.5),
                 "Azure AI Search\nEmployee / airline policy PDFs\n“What’s the baggage rule?”",
                 size=15, color=INK, align=PP_ALIGN.CENTER)

    add_round_rect(s, Inches(7.2), Inches(3.5), Inches(5.5), Inches(2.7), WHITE)
    add_rect(s, Inches(7.2), Inches(3.5), Inches(5.5), Inches(0.5), OK)
    add_text_box(s, Inches(7.2), Inches(3.58), Inches(5.5), Inches(0.35), "MCP tool: search_flights (API)", size=14, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_text_box(s, Inches(7.5), Inches(4.3), Inches(5), Inches(1.5),
                 "Amadeus / Duffel / mock API\nLive fares & schedules\n“What’s the best flight?”",
                 size=15, color=INK, align=PP_ALIGN.CENTER)

    # ========== 21. Cursor example ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Same pattern in Cursor (you already use this)", "Cursor = Host · your MCP servers = superpowers")

    steps_c = [
        ("1", "You configure an MCP server in Cursor"),
        ("2", "Cursor starts a Client connection to that server"),
        ("3", "Agent lists tools (browser, Figma, custom API…)"),
        ("4", "You ask in chat → model picks a tool"),
        ("5", "Client calls tools/call → server executes"),
        ("6", "Result returns → model finishes the answer"),
    ]
    for i, (n, t) in enumerate(steps_c):
        y = Inches(1.9) + Inches(i * 0.75)
        add_round_rect(s, Inches(0.55), y, Inches(12.2), Inches(0.65), WHITE)
        step_chip(s, Inches(0.8), y + Inches(0.12), n)
        add_text_box(s, Inches(1.5), y + Inches(0.15), Inches(10.8), Inches(0.4), t, size=16, color=INK)

    # ========== 22. Security visual ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Safety checkpoints in the flow", "Where humans and guardrails intervene")

    checkpoints = [
        ("Before tool call", "User approval for writes / bookings", ACCENT),
        ("Inside server", "Least-privilege API keys only", TEAL),
        ("On the host", "Foundry guardrails / jailbreak block", OK),
        ("After result", "Don’t leak secrets into chat logs", DANGER),
    ]
    for i, (t, b, c) in enumerate(checkpoints):
        x = Inches(0.5) + Inches((i % 2) * 6.4)
        y = Inches(2.0) + Inches((i // 2) * 2.3)
        add_round_rect(s, x, y, Inches(6.1), Inches(2.05), WHITE)
        add_rect(s, x, y, Inches(0.15), Inches(2.05), c)
        add_text_box(s, x + Inches(0.45), y + Inches(0.4), Inches(5.3), Inches(0.45), t, size=18, bold=True, color=INK)
        add_text_box(s, x + Inches(0.45), y + Inches(1.05), Inches(5.3), Inches(0.55), b, size=15, color=MUTED)

    # ========== 23. Lab ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Lab · Draw your own E2E flow", "30–40 minutes")

    lab = [
        ("1", "Write 1 user question for your agent"),
        ("2", "Box the Host, Client, and Server on paper"),
        ("3", "List 2 Tools + 1 Resource + 1 Prompt"),
        ("4", "Number the arrows 1→8 like our flight story"),
        ("5", "Circle where human approval is required"),
        ("6", "Bonus: mark one step that could use RAG"),
    ]
    for i, (n, t) in enumerate(lab):
        y = Inches(1.85) + Inches(i * 0.75)
        add_round_rect(s, Inches(0.55), y, Inches(12.2), Inches(0.65), WHITE)
        step_chip(s, Inches(0.8), y + Inches(0.12), n)
        add_text_box(s, Inches(1.5), y + Inches(0.15), Inches(10.8), Inches(0.4), t, size=16, color=INK)

    # ========== 24. Takeaways ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, PAPER)
    accent_bar(s)
    title_block(s, "Key takeaways", "Pin these four pictures in your head")
    takes = [
        ("USB-C for AI", "One protocol, many tools"),
        ("Host → Client → Server", "App connects; server delivers"),
        ("Do · Read · Template", "Tools · Resources · Prompts"),
        ("E2E = tool loop", "Ask → call → result → answer"),
    ]
    for i, (t, b) in enumerate(takes):
        x = Inches(0.55) + Inches((i % 2) * 6.3)
        y = Inches(1.95) + Inches((i // 2) * 2.25)
        add_round_rect(s, x, y, Inches(6.05), Inches(2.05), WHITE)
        add_rect(s, x, y, Inches(0.15), Inches(2.05), TEAL)
        add_text_box(s, x + Inches(0.45), y + Inches(0.45), Inches(5.3), Inches(0.5), t, size=20, bold=True, color=INK)
        add_text_box(s, x + Inches(0.45), y + Inches(1.15), Inches(5.3), Inches(0.5), b, size=15, color=MUTED)

    # ========== 25. Closing ==========
    s = prs.slides.add_slide(blank)
    set_bg(s, INK)
    add_rect(s, Inches(0), Inches(0), Inches(0.28), SLIDE_H, TEAL)
    add_text_box(s, Inches(0.7), Inches(2.0), Inches(11), Inches(0.4), "NEXT BUILD", size=14, bold=True, color=TEAL)
    add_text_box(s, Inches(0.7), Inches(2.6), Inches(12), Inches(1.5),
                 "Implement search_flights\nas a real MCP tool", size=36, bold=True, color=WHITE)
    add_text_box(s, Inches(0.7), Inches(4.6), Inches(11.5), Inches(0.9),
                 "Then wire it into Cursor or an Azure Foundry agent — same flow you just learned.",
                 size=17, color=RGBColor(0xB8, 0xC4, 0xD0))
    add_text_box(s, Inches(0.7), Inches(5.8), Inches(11), Inches(0.4),
                 "Docs: modelcontextprotocol.io", size=14, color=MUTED)

    n = len(prs.slides)
    for i in range(1, n - 1):
        footer(prs.slides[i], i + 1, n)

    out = "/Users/khurramnaqi/Documents/Samiaa Learning/teaching/MCP_Model_Context_Protocol.pptx"
    prs.save(out)
    return out, n


if __name__ == "__main__":
    path, count = build()
    print(f"Wrote {count} slides → {path}")
