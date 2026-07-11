"""Shape kit — the locked-style architecture/diagram building blocks."""
from pptx.util import Inches, Pt, Emu
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from . import tokens as t

def _fill(shape, color):
    shape.fill.solid(); shape.fill.fore_color.rgb = color

def _line(shape, color, width_pt=1.5):
    shape.line.color.rgb = color; shape.line.width = Pt(width_pt)

def _no_line(shape):
    shape.line.fill.background()

def box(slide, pos, text, *, kind="plain", accent="blue", sub=None):
    """pos=(left,top,width,height) in inches. kind: plain|focus|neutral."""
    left, top, width, height = (Inches(v) for v in pos)
    sp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    sp.adjustments[0] = 0.08  # ~10px radius
    if kind == "focus":
        _fill(sp, t.ramp(accent, "c100")); _line(sp, t.ramp(accent, "c600"), 1.75)
        txt_color = t.ramp(accent, "c800")
    elif kind == "neutral":
        _fill(sp, t.MIST); _no_line(sp); txt_color = t.GRAPHITE
    else:  # plain
        _fill(sp, t.WHITE); _line(sp, t.HAIRLINE, 1.5); txt_color = t.GRAPHITE
    tf = sp.text_frame; tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = text
    r.font.name = "Helvetica Neue"; r.font.size = Pt(14); r.font.bold = True
    r.font.color.rgb = txt_color
    if sub:
        p2 = tf.add_paragraph(); p2.alignment = PP_ALIGN.CENTER
        r2 = p2.add_run(); r2.text = sub
        r2.font.name = "Helvetica Neue"; r2.font.size = Pt(11); r2.font.color.rgb = t.SLATE
    return sp

def arrow(slide, x1, y1, x2, y2):
    """Thin connector with an arrowhead, Silver."""
    cn = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,
                                    Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    cn.line.color.rgb = t.SILVER; cn.line.width = Pt(1.5)
    # add end arrowhead via XML
    ln = cn.line._get_or_add_ln()
    from pptx.oxml.ns import qn
    tail = ln.makeelement(qn("a:tailEnd"), {"type": "triangle", "w": "med", "len": "med"})
    ln.append(tail)
    return cn

def band(slide, pos, label, tag, accent):
    """Horizontal layer band (Route A pattern B)."""
    left, top, width, height = (Inches(v) for v in pos)
    sp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    sp.adjustments[0] = 0.06
    _fill(sp, t.ramp(accent, "c100")); _line(sp, t.ramp(accent, "c600"), 1.75)
    tf = sp.text_frame; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.LEFT
    r = p.add_run(); r.text = "   " + label
    r.font.name = "Helvetica Neue"; r.font.size = Pt(16); r.font.bold = True
    r.font.color.rgb = t.ramp(accent, "c800")
    return sp

def kpi_tile(slide, pos, number, label, *, accent=None):
    """Color card. accent=None -> neutral Mist tile; else tint tile with accent number."""
    left, top, width, height = (Inches(v) for v in pos)
    sp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    sp.adjustments[0] = 0.06
    _fill(sp, t.ramp(accent, "c100") if accent else t.MIST); _no_line(sp)
    tf = sp.text_frame; tf.word_wrap = True
    tf.margin_left = Inches(0.2); tf.margin_top = Inches(0.18)
    p = tf.paragraphs[0]
    r = p.add_run(); r.text = number
    r.font.name = "Helvetica Neue"; r.font.size = Pt(30); r.font.bold = True
    r.font.color.rgb = t.ramp(accent, "c800") if accent else t.INK
    p2 = tf.add_paragraph(); r2 = p2.add_run(); r2.text = label
    r2.font.name = "Helvetica Neue"; r2.font.size = Pt(12); r2.font.color.rgb = t.SLATE
    return sp
