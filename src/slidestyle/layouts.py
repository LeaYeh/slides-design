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
