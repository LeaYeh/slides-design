"""The 12 archetype builders. Each draws onto a blank slide."""
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from . import tokens as t
from . import text, shapes

def _accent_bar(slide, left, top, accent="blue", w=0.72, h=0.07):
    sp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                Inches(left), Inches(top), Inches(w), Inches(h))
    sp.adjustments[0] = 0.5
    sp.fill.solid(); sp.fill.fore_color.rgb = t.ramp(accent, "c600")
    sp.line.fill.background()
    return sp

def _full_bg(slide, color):
    sp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, t.SLIDE_W, t.SLIDE_H)
    sp.fill.solid(); sp.fill.fore_color.rgb = color; sp.line.fill.background()
    slide.shapes._spTree.remove(sp._element); slide.shapes._spTree.insert(2, sp._element)
    return sp

def cover(slide, accent="blue"):
    _accent_bar(slide, 0.9, 1.5, accent)
    text.kicker(slide, 0.9, 1.75, "Product Vision · 2026", accent)
    text.title(slide, 0.86, 2.2, 11, "Designing with clarity", "cover")
    text.body(slide, 0.9, 4.1, 9, "A minimalist system for professional decks")

def section(slide, accent="blue"):
    _full_bg(slide, t.ramp(accent, "c900"))
    text.textbox(slide, (0.9, 2.6, 3, 1), "02", size=20, bold=True, color=t.ramp(accent, "c300"))
    text.textbox(slide, (0.9, 3.1, 11, 1.6), "The Approach", size=40, bold=True, color=t.WHITE, tracking=-0.4)

def statement(slide, accent="blue"):
    text.textbox(slide, (1.2, 2.6, 11, 2.2),
                 "Professionalism comes from hierarchy, not decoration.",
                 size=t.TYPE["statement"][0], bold=True, color=t.INK,
                 align=t.ALIGN_CENTER, line=1.15, tracking=-0.4)

def heading_body(slide, accent="blue"):
    text.kicker(slide, 0.9, 0.9, "Overview", accent)
    text.title(slide, 0.86, 1.35, 11, "Heading sits here", "heading")
    text.body(slide, 0.9, 2.6, 7.5,
              "Body copy in Graphite, generous line-height. One idea per slide; "
              "keep supporting detail tight and scannable.")

def bullet_list(slide, accent="blue"):
    text.kicker(slide, 0.9, 0.9, "Principles", accent)
    text.title(slide, 0.86, 1.35, 11, "What guides the design", "heading")
    items = ["Hierarchy over decoration", "One idea per slide",
             "A single accent, used deliberately", "Whitespace is a feature"]
    y = 2.7
    for it in items:
        m = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.95), Inches(y+0.09),
                                   Inches(0.12), Inches(0.12))
        m.fill.solid(); m.fill.fore_color.rgb = t.ramp(accent, "c600"); m.line.fill.background()
        text.textbox(slide, (1.3, y, 10, 0.6), it, size=18, color=t.GRAPHITE)
        y += 0.75

def two_column(slide, accent="blue"):
    text.kicker(slide, 0.9, 0.9, "Comparison", accent)
    text.title(slide, 0.86, 1.35, 11, "Two columns", "heading")
    text.textbox(slide, (0.9, 2.7, 5.4, 0.5), "Left", size=18, bold=True, color=t.INK)
    text.body(slide, 0.9, 3.2, 5.4, "First column body content sits here.")
    text.textbox(slide, (7.0, 2.7, 5.4, 0.5), "Right", size=18, bold=True, color=t.INK)
    text.body(slide, 7.0, 3.2, 5.4, "Second column body content sits here.")

def color_cards(slide, accent="blue"):
    text.kicker(slide, 0.9, 0.9, "Metrics", accent)
    text.title(slide, 0.86, 1.35, 11, "Impact at a glance", "heading")
    data = [("3.2×", "faster to draft", accent), ("100%", "on-brand", None), ("12", "layouts", accent)]
    x = 0.9
    for number, label, acc in data:
        shapes.kpi_tile(slide, (x, 2.9, 3.6, 1.7), number, label, accent=acc)
        x += 3.9

def highlight(slide, accent="blue"):
    text.kicker(slide, 0.9, 0.9, "Key point", accent)
    text.title(slide, 0.86, 1.35, 11, "Highlight a term", "heading")
    # tint highlight block behind a key phrase
    hl = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(3.0),
                                Inches(5.2), Inches(1.0))
    hl.adjustments[0] = 0.12
    hl.fill.solid(); hl.fill.fore_color.rgb = t.ramp(accent, "c300"); hl.line.fill.background()
    from pptx.enum.text import MSO_ANCHOR as _A
    hl.text_frame.vertical_anchor = _A.MIDDLE
    p = hl.text_frame.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = "the one number that matters"
    r.font.name = "Helvetica Neue"; r.font.size = Pt(20); r.font.bold = True
    r.font.color.rgb = t.ramp(accent, "c900")
    text.body(slide, 0.9, 4.3, 10, "Supporting sentence explains why it matters.")

def arch_flow(slide, accent="blue"):
    """Pattern A — horizontal flow, one focus node."""
    text.kicker(slide, 0.9, 0.9, "Architecture", accent)
    text.title(slide, 0.86, 1.35, 11, "How a deck is generated", "heading")
    nodes = [("Content", "title · body · concept", "plain"),
             ("Style template", "theme + 12 layouts", "focus"),
             ("Claude", "python-pptx", "plain"),
             (".pptx deck", "editable", "plain")]
    x, y, w, h = 0.9, 3.1, 2.5, 1.2
    prev = None
    for label, sub, kind in nodes:
        shapes.box(slide, (x, y, w, h), label, kind=kind, accent=accent, sub=sub)
        if prev is not None:
            shapes.arrow(slide, prev, y + h/2, x, y + h/2)
        prev = x + w
        x += w + 0.55

def arch_layered(slide, accent="blue"):
    """Pattern B — layered stack, three accents as categories."""
    text.kicker(slide, 0.9, 0.9, "System", accent)
    text.title(slide, 0.86, 1.35, 11, "Platform layers", "heading")
    rows = [("Presentation · UI", "Serve", "orange"),
            ("Application · services & logic", "Process", "teal"),
            ("Data · storage & ingest", "Ingest", "blue")]
    y = 2.8
    for label, tag, acc in rows:
        shapes.band(slide, (0.9, y, 11.5, 1.05), label, tag, acc)
        y += 1.25

def arch_nested(slide, accent="blue"):
    """Pattern C — nested container holding sub-nodes."""
    text.kicker(slide, 0.9, 0.9, "Architecture", accent)
    text.title(slide, 0.86, 1.35, 11, "Service boundary", "heading")
    cont = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(2.8),
                                  Inches(11.5), Inches(2.6))
    cont.adjustments[0] = 0.05
    cont.fill.solid(); cont.fill.fore_color.rgb = t.MIST; cont.line.color.rgb = t.HAIRLINE
    cont.line.width = Pt(1.5)
    text.textbox(slide, (1.15, 3.0, 6, 0.4), "CORE SERVICE", size=12, bold=True,
                 color=t.SLATE, upper=True, tracking=t.KICKER_TRACK_PT)
    subs = [("API gateway", "plain"), ("Engine", "focus"), ("Cache", "plain")]
    x = 1.2
    for label, kind in subs:
        shapes.box(slide, (x, 3.6, 3.4, 1.3), label, kind=kind, accent=accent)
        x += 3.7

def image_caption(slide, accent="blue"):
    text.kicker(slide, 0.9, 0.9, "Visual", accent)
    text.title(slide, 0.86, 1.35, 6, "Image + caption", "heading")
    ph = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.3),
                                Inches(5.6), Inches(4.6))
    ph.adjustments[0] = 0.03
    ph.fill.solid(); ph.fill.fore_color.rgb = t.MIST; ph.line.color.rgb = t.HAIRLINE
    ph.line.width = Pt(1.5)
    p = ph.text_frame.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = "[ image ]"; r.font.name = "Helvetica Neue"
    r.font.size = Pt(14); r.font.color.rgb = t.SILVER
    text.body(slide, 0.9, 2.7, 5.4, "Body sits left; image fills the right half.")
    text.caption(slide, 6.8, 6.0, 5.6, "Figure 1 — caption in Slate")

def quote(slide, accent="blue"):
    text.textbox(slide, (1.2, 2.4, 11, 2),
                 "“Good design is as little design as possible.”",
                 size=36, bold=True, color=t.INK, align=t.ALIGN_CENTER, line=1.2, tracking=-0.4)
    text.textbox(slide, (1.2, 4.4, 11, 0.5), "— Dieter Rams",
                 size=16, color=t.SLATE, align=t.ALIGN_CENTER)

def closing(slide, accent="blue"):
    _accent_bar(slide, 6.13, 2.7, accent)  # roughly centered
    text.textbox(slide, (1.2, 3.0, 11, 1), "Thank you", size=30, bold=True,
                 color=t.INK, align=t.ALIGN_CENTER)
    text.textbox(slide, (1.2, 4.0, 11, 0.5), "questions → hello@example.com",
                 size=16, color=t.SLATE, align=t.ALIGN_CENTER)
