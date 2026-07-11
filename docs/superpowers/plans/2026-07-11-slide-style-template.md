# Slide Style Template — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a reusable, editable PowerPoint style template (`dist/slide-style.pptx`) + usage guide (`dist/style-guide.md`) encoding one Apple-Keynote-minimal look: neutral hierarchy + three accent ramps, Helvetica Neue, 12 layout archetypes, and a hybrid architecture-diagram subsystem.

**Architecture:** A small Python package (`src/slidestyle/`) builds the deck deterministically. `tokens.py` is the single source of truth for colors/type. `theme.py` injects a real OOXML theme (so PowerPoint's color picker + "recolor by theme" reflect our palette). Each archetype is drawn as a real, editable example slide via python-pptx (rather than a master layout — python-pptx can't author master layouts cleanly). Architecture diagrams: native shapes by default (Route A), optional SVG-generation+embed for complex ones (Route B).

**Tech Stack:** Python 3.11+, `uv`, `python-pptx`, `lxml`; `cairosvg` for the optional SVG route.

**Verification note (project profile = personal):** Tests are light and structural — each task ends by rebuilding and running `verify.py` assertions (theme hexes, slide count, sample shapes). No heavy TDD ceremony. Visual spot-checks via LibreOffice where noted.

**Confirmed technical facts (probed 2026-07-11):**
- Theme part is a generic `Part`: read `theme_part.blob`, mutate with lxml, write back via `theme_part._blob = etree.tostring(...)`. Persists through `prs.save()`.
- `dk1`/`lt1` use `<a:sysClr>` — replace the child with `<a:srgbClr val=...>`. `dk2`/`lt2`/`accent1..6` already use `<a:srgbClr>` — just set `val`.
- Get theme part: `prs.slide_masters[0].part.part_related_by(RELATIONSHIP_TYPE.THEME)`.

---

## File Structure

```
slides/
  pyproject.toml                 # uv project + deps
  src/slidestyle/
    __init__.py
    tokens.py                    # colors, type scale, geometry — single source of truth
    theme.py                     # inject clrScheme + fontScheme + 16:9
    text.py                      # styled textbox helpers (kicker/title/body/caption)
    shapes.py                    # shape kit: box/focus/arrow/group-label/legend/kpi/band
    layouts.py                   # the 12 archetype builders
    build.py                     # assemble dist/slide-style.pptx
    guide.py                     # emit dist/style-guide.md
    svg/                         # Route B (optional phase)
      __init__.py
      style.py                   # our-palette SVG tokens
      generate.py                # diagram-type SVG generators (flow, layered)
      embed.py                   # insert SVG (png fallback + svgBlip) into a slide
  verify.py                      # structural checks used by verify steps
  dist/                          # OUTPUT: slide-style.pptx, style-guide.md (+ svg samples)
```

Deliverables land in `dist/`. `.gitignore` keeps `.venv/` out; `dist/` IS committed (it's the product).

---

## Phase 0 — Scaffold & tooling

### Task 1: Project scaffold

**Files:**
- Create: `pyproject.toml`, `src/slidestyle/__init__.py`, `verify.py`
- Modify: `.gitignore`

- [ ] **Step 1: Write `pyproject.toml`**

```toml
[project]
name = "slidestyle"
version = "0.1.0"
description = "Apple-minimal PowerPoint style template generator"
requires-python = ">=3.11"
dependencies = ["python-pptx>=0.6.23", "lxml>=5.0"]

[project.optional-dependencies]
svg = ["cairosvg>=2.7"]

[tool.uv]
package = true

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

- [ ] **Step 2: Create the package marker**

`src/slidestyle/__init__.py`:
```python
"""Apple-minimal PowerPoint style template generator."""
__all__ = []
```

- [ ] **Step 3: Add `.venv` and caches to `.gitignore`**

Append to `.gitignore`:
```
.venv/
__pycache__/
*.pyc
```

- [ ] **Step 4: Create the env and install**

Run:
```bash
uv venv && uv pip install -e .
```
Expected: installs python-pptx + lxml, no errors.

- [ ] **Step 5: Write a minimal `verify.py` placeholder**

```python
"""Structural checks for the built deck. Grows as tasks land."""
import sys
from pptx import Presentation

def main(path="dist/slide-style.pptx"):
    prs = Presentation(path)
    print(f"opened {path}: {len(prs.slides.__iter__.__self__._sldIdLst)} slide ids")
    print(f"slide size EMU: {prs.slide_width} x {prs.slide_height}")

if __name__ == "__main__":
    main(*sys.argv[1:])
```

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml src/slidestyle/__init__.py verify.py .gitignore
git commit -m "chore: scaffold slidestyle package"
```

---

## Phase 1 — Tokens & theme

### Task 2: Tokens (single source of truth)

**Files:**
- Create: `src/slidestyle/tokens.py`

- [ ] **Step 1: Write `tokens.py`**

```python
"""Design tokens — the single source of truth for colors, type, geometry."""
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

def rgb(h: str) -> RGBColor:
    return RGBColor.from_string(h)

# --- neutral scale ---
INK      = rgb("1D1D1F")
GRAPHITE = rgb("424245")
SLATE    = rgb("6E6E73")
SILVER   = rgb("AEAEB2")
HAIRLINE = rgb("D2D2D7")
MIST     = rgb("F5F5F7")
WHITE    = rgb("FFFFFF")

# --- accent ramps: 900/800/600/400/300/100 (hex strings) ---
RAMPS = {
    "blue":   {"c900":"16337A","c800":"1D4ED8","c600":"2563EB","c400":"60A5FA","c300":"93C5FD","c100":"EAF2FE"},
    "teal":   {"c900":"0B5F60","c800":"0A6E6F","c600":"22B5B7","c400":"6FD6D8","c300":"A2E8E9","c100":"E8FBFC"},
    "orange": {"c900":"7C2D12","c800":"C2410C","c600":"F97316","c400":"FDA55A","c300":"FDBA8C","c100":"FFF3EA"},
}
DEFAULT_ACCENT = "blue"

def ramp(name: str, step: str) -> RGBColor:
    """ramp('blue','c600') -> RGBColor."""
    return rgb(RAMPS[name][step])

# --- type scale: name -> (size_pt, bold) ; color chosen at call site ---
TYPE = {
    "cover":     (54, True),
    "heading":   (34, True),
    "statement": (40, True),
    "kicker":    (12, True),   # uppercase + tracking, accent-800 color
    "body":      (18, False),
    "caption":   (13, False),
}
KICKER_TRACK_PT = 1.7  # ~0.14em at 12pt

# --- 16:9 canvas ---
SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)
MARGIN  = Inches(0.9)

ALIGN_LEFT = PP_ALIGN.LEFT
ALIGN_CENTER = PP_ALIGN.CENTER
```

- [ ] **Step 2: Verify import**

Run:
```bash
uv run python -c "from slidestyle import tokens as t; print(t.INK, t.ramp('blue','c600'), t.TYPE['cover'])"
```
Expected: `1D1D1F 2563EB (54, True)`

- [ ] **Step 3: Commit**

```bash
git add src/slidestyle/tokens.py
git commit -m "feat: design tokens"
```

### Task 3: Theme injection

**Files:**
- Create: `src/slidestyle/theme.py`

- [ ] **Step 1: Write `theme.py`**

```python
"""Inject a real OOXML theme: our color scheme + Helvetica Neue + 16:9."""
from lxml import etree
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from . import tokens as t

A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
FONT = "Helvetica Neue"

def _set_srgb(clr_scheme, name: str, hex6: str):
    node = clr_scheme.find(f"a:{name}", NS)
    for c in list(node):
        node.remove(c)
    s = etree.SubElement(node, A + "srgbClr")
    s.set("val", hex6)

def apply_theme(prs, primary: str = t.DEFAULT_ACCENT):
    # 16:9 canvas
    prs.slide_width = t.SLIDE_W
    prs.slide_height = t.SLIDE_H

    # accent order: primary first, then the other two 600s, then three 800s
    order = [primary] + [n for n in ("blue", "teal", "orange") if n != primary]
    accents = {
        "accent1": t.RAMPS[order[0]]["c600"],
        "accent2": t.RAMPS[order[1]]["c600"],
        "accent3": t.RAMPS[order[2]]["c600"],
        "accent4": t.RAMPS["blue"]["c800"],
        "accent5": t.RAMPS["teal"]["c800"],
        "accent6": t.RAMPS["orange"]["c800"],
    }
    neutrals = {"dk1": "1D1D1F", "lt1": "FFFFFF", "dk2": "424245", "lt2": "F5F5F7"}

    theme_part = prs.slide_masters[0].part.part_related_by(RT.THEME)
    root = etree.fromstring(theme_part.blob)
    clr = root.find(".//a:clrScheme", NS)
    for name, hex6 in {**neutrals, **accents}.items():
        _set_srgb(clr, name, hex6)
    # hyperlink colors -> primary
    _set_srgb(clr, "hlink", t.RAMPS[primary]["c600"])
    _set_srgb(clr, "folHlink", t.RAMPS[primary]["c800"])
    # fonts
    for tag in ("majorFont", "minorFont"):
        latin = root.find(f".//a:fontScheme/a:{tag}/a:latin", NS)
        latin.set("typeface", FONT)
    theme_part._blob = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
```

- [ ] **Step 2: Verify theme round-trips through save**

Run:
```bash
uv run python -c "
from pptx import Presentation
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from lxml import etree
from slidestyle.theme import apply_theme, NS
prs = Presentation(); apply_theme(prs); prs.save('/tmp/t.pptx')
p = Presentation('/tmp/t.pptx')
tp = p.slide_masters[0].part.part_related_by(RT.THEME)
r = etree.fromstring(tp.blob)
print('accent1', r.find('.//a:clrScheme/a:accent1/a:srgbClr', NS).get('val'))
print('dk1', r.find('.//a:clrScheme/a:dk1/a:srgbClr', NS).get('val'))
print('font', r.find('.//a:fontScheme/a:majorFont/a:latin', NS).get('typeface'))
print('16:9', p.slide_width, p.slide_height)
"
```
Expected: `accent1 2563EB` / `dk1 1D1D1F` / `font Helvetica Neue` / `16:9 12192000 6858000`

- [ ] **Step 3: Commit**

```bash
git add src/slidestyle/theme.py
git commit -m "feat: inject OOXML theme (palette + Helvetica Neue + 16:9)"
```

---

## Phase 2 — Styling primitives

### Task 4: Text helpers

**Files:**
- Create: `src/slidestyle/text.py`

- [ ] **Step 1: Write `text.py`**

```python
"""Styled text helpers built on the token type scale."""
from pptx.util import Inches, Pt
from pptx.oxml.ns import qn
from . import tokens as t

def _set_tracking(run, pts: float):
    run.font._rPr.set("spc", str(int(pts * 100)))  # spc is 1/100 pt

def textbox(slide, box, text, *, size, bold=False, color=t.INK,
            align=t.ALIGN_LEFT, upper=False, tracking=0.0, line=1.12):
    """box = (left,top,width,height) in inches. Returns the shape."""
    left, top, width, height = (Inches(v) for v in box)
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    if line:
        p.line_spacing = line
    run = p.add_run()
    run.text = text.upper() if upper else text
    f = run.font
    f.name = t.FONT if False else "Helvetica Neue"
    f.size = Pt(size)
    f.bold = bold
    f.color.rgb = color
    if tracking:
        _set_tracking(run, tracking)
    return tb

def kicker(slide, left, top, text, accent):
    """Uppercase overline in accent-800, letter-spaced."""
    return textbox(slide, (left, top, 6.0, 0.4), text,
                   size=t.TYPE["kicker"][0], bold=True,
                   color=t.ramp(accent, "c800"), upper=True,
                   tracking=t.KICKER_TRACK_PT)

def title(slide, left, top, width, text, kind="heading", color=t.INK):
    size, bold = t.TYPE[kind]
    return textbox(slide, (left, top, width, 1.6), text, size=size, bold=bold,
                   color=color, tracking=-0.4)  # slight tight tracking

def body(slide, left, top, width, text, color=t.GRAPHITE):
    return textbox(slide, (left, top, width, 3.5), text,
                   size=t.TYPE["body"][0], color=color, line=1.3)

def caption(slide, left, top, width, text):
    return textbox(slide, (left, top, width, 0.4), text,
                   size=t.TYPE["caption"][0], color=t.SLATE)
```
Note: `t.FONT` is imported from theme conceptually; keep the literal "Helvetica Neue" here to avoid a circular import.

- [ ] **Step 2: Verify a textbox gets the right font/size/color**

Run:
```bash
uv run python -c "
from pptx import Presentation
from slidestyle.theme import apply_theme
from slidestyle import text, tokens as t
prs=Presentation(); apply_theme(prs)
s=prs.slides.add_slide(prs.slide_layouts[6])
tb=text.title(s,0.9,0.9,10,'Designing with clarity','cover')
r=tb.text_frame.paragraphs[0].runs[0]
print(r.font.name, r.font.size.pt, r.font.bold, str(r.font.color.rgb))
"
```
Expected: `Helvetica Neue 54.0 True 1D1D1F`

- [ ] **Step 3: Commit**

```bash
git add src/slidestyle/text.py
git commit -m "feat: styled text helpers"
```

### Task 5: Shape kit

**Files:**
- Create: `src/slidestyle/shapes.py`

- [ ] **Step 1: Write `shapes.py`**

```python
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
```

- [ ] **Step 2: Verify shapes render with correct fills**

Run:
```bash
uv run python -c "
from pptx import Presentation
from slidestyle.theme import apply_theme
from slidestyle import shapes
prs=Presentation(); apply_theme(prs)
s=prs.slides.add_slide(prs.slide_layouts[6])
b=shapes.box(s,(1,1,2,1),'Engine',kind='focus',accent='blue',sub='core')
print('fill', str(b.fill.fore_color.rgb), 'line', str(b.line.color.rgb))
shapes.arrow(s,3.2,1.5,4.2,1.5)
print('shapes on slide:', len(s.shapes))
"
```
Expected: `fill EAF2FE line 2563EB` / `shapes on slide: 2`

- [ ] **Step 3: Commit**

```bash
git add src/slidestyle/shapes.py
git commit -m "feat: shape kit (box/focus/arrow/band/kpi)"
```

---

## Phase 3 — The 12 archetypes

Each builder takes a blank slide and draws the archetype. All live in `layouts.py`.

### Task 6: Core text archetypes (cover, section, statement, heading+body)

**Files:**
- Create: `src/slidestyle/layouts.py`

- [ ] **Step 1: Write `layouts.py` with the first four builders**

```python
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
```

- [ ] **Step 2: Verify the four builders run**

Run:
```bash
uv run python -c "
from pptx import Presentation
from slidestyle.theme import apply_theme
from slidestyle import layouts
prs=Presentation(); apply_theme(prs)
for fn in (layouts.cover, layouts.section, layouts.statement, layouts.heading_body):
    fn(prs.slides.add_slide(prs.slide_layouts[6]))
prs.save('/tmp/core.pptx'); print('slides', len(prs.slides._sldIdLst))
"
```
Expected: `slides 4`

- [ ] **Step 3: Commit**

```bash
git add src/slidestyle/layouts.py
git commit -m "feat: cover/section/statement/heading-body archetypes"
```

### Task 7: List, two-column, color-cards, highlight

**Files:**
- Modify: `src/slidestyle/layouts.py`

- [ ] **Step 1: Append four builders to `layouts.py`**

```python
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
```

- [ ] **Step 2: Verify**

Run:
```bash
uv run python -c "
from pptx import Presentation
from slidestyle.theme import apply_theme
from slidestyle import layouts
prs=Presentation(); apply_theme(prs)
for fn in (layouts.bullet_list, layouts.two_column, layouts.color_cards, layouts.highlight):
    fn(prs.slides.add_slide(prs.slide_layouts[6]))
print('ok', len(prs.slides._sldIdLst))
"
```
Expected: `ok 4`

- [ ] **Step 3: Commit**

```bash
git add src/slidestyle/layouts.py
git commit -m "feat: list/two-column/color-cards/highlight archetypes"
```

### Task 8: Architecture family (Route A: shape kit + 3 patterns)

**Files:**
- Modify: `src/slidestyle/layouts.py`

- [ ] **Step 1: Append the architecture builders**

```python
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
```

- [ ] **Step 2: Verify (and eyeball the flow render)**

Run:
```bash
uv run python -c "
from pptx import Presentation
from slidestyle.theme import apply_theme
from slidestyle import layouts
prs=Presentation(); apply_theme(prs)
for fn in (layouts.arch_flow, layouts.arch_layered, layouts.arch_nested):
    fn(prs.slides.add_slide(prs.slide_layouts[6]))
prs.save('/tmp/arch.pptx'); print('ok')
"
```
Expected: `ok`. Optional visual check: `soffice --headless --convert-to pdf --outdir /tmp /tmp/arch.pptx` and open the PDF — arrows should sit between boxes, focus box tinted.

- [ ] **Step 3: Commit**

```bash
git add src/slidestyle/layouts.py
git commit -m "feat: architecture family (flow/layered/nested)"
```

### Task 9: Image+caption, quote, closing

**Files:**
- Modify: `src/slidestyle/layouts.py`

- [ ] **Step 1: Append the final three builders**

```python
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
```

- [ ] **Step 2: Verify all 12 builders exist**

Run:
```bash
uv run python -c "
from slidestyle import layouts
names=['cover','section','statement','heading_body','bullet_list','two_column',
 'color_cards','highlight','arch_flow','arch_layered','arch_nested',
 'image_caption','quote','closing']
missing=[n for n in names if not hasattr(layouts,n)]
print('missing:', missing)
"
```
Expected: `missing: []` (14 builders: 11 non-arch + 3 arch = the 12 archetypes, arch counted as one family of 3).

- [ ] **Step 3: Commit**

```bash
git add src/slidestyle/layouts.py
git commit -m "feat: image-caption/quote/closing archetypes"
```

---

## Phase 4 — Assemble & document

### Task 10: Build the deck

**Files:**
- Create: `src/slidestyle/build.py`
- Modify: `verify.py`

- [ ] **Step 1: Write `build.py`**

```python
"""Assemble dist/slide-style.pptx: one labeled example slide per archetype."""
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from . import tokens as t
from .theme import apply_theme
from . import layouts, text

# (builder, caption) in gallery order
GALLERY = [
    (layouts.cover, "1 · Cover / Title"),
    (layouts.section, "2 · Section divider"),
    (layouts.statement, "3 · Big statement"),
    (layouts.heading_body, "4 · Heading + body"),
    (layouts.bullet_list, "5 · Minimal list"),
    (layouts.two_column, "6 · Two column"),
    (layouts.color_cards, "7 · Color cards / KPI"),
    (layouts.highlight, "8 · Highlight / callout"),
    (layouts.arch_flow, "9a · Architecture — flow"),
    (layouts.arch_layered, "9b · Architecture — layered"),
    (layouts.arch_nested, "9c · Architecture — nested"),
    (layouts.image_caption, "10 · Image + caption"),
    (layouts.quote, "11 · Quote"),
    (layouts.closing, "12 · Closing"),
]

def build(path="dist/slide-style.pptx", primary=t.DEFAULT_ACCENT):
    prs = Presentation()
    apply_theme(prs, primary)
    for fn, cap in GALLERY:
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        fn(slide, accent=primary)
        # tiny archetype label bottom-left (not part of the design; a gallery marker)
        text.textbox(slide, (0.4, 7.05, 6, 0.35), cap, size=9, color=t.SILVER)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    prs.save(path)
    return path

if __name__ == "__main__":
    print("built", build())
```

- [ ] **Step 2: Replace `verify.py` with real assertions**

```python
"""Structural checks for the built deck."""
import sys
from pptx import Presentation
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from lxml import etree
from slidestyle.theme import NS

def main(path="dist/slide-style.pptx"):
    prs = Presentation(path)
    n = len(list(prs.slides))
    assert n == 14, f"expected 14 gallery slides, got {n}"
    assert prs.slide_width == 12192000 and prs.slide_height == 6858000, "not 16:9"
    tp = prs.slide_masters[0].part.part_related_by(RT.THEME)
    r = etree.fromstring(tp.blob)
    a1 = r.find(".//a:clrScheme/a:accent1/a:srgbClr", NS).get("val")
    font = r.find(".//a:fontScheme/a:majorFont/a:latin", NS).get("typeface")
    assert a1 == "2563EB", f"accent1 ={a1}"
    assert font == "Helvetica Neue", f"font ={font}"
    print(f"OK — {n} slides, 16:9, accent1={a1}, font={font}")

if __name__ == "__main__":
    main(*sys.argv[1:])
```

- [ ] **Step 3: Build and verify**

Run:
```bash
uv run python -m slidestyle.build && uv run python verify.py
```
Expected: `built dist/slide-style.pptx` then `OK — 14 slides, 16:9, accent1=2563EB, font=Helvetica Neue`

- [ ] **Step 4: Visual spot-check (if LibreOffice available)**

Run:
```bash
soffice --headless --convert-to pdf --outdir dist dist/slide-style.pptx 2>/dev/null && echo "open dist/slide-style.pdf"
```
Eyeball: hierarchy reads, accents correct, arrows between boxes, nothing overlapping.

- [ ] **Step 5: Commit**

```bash
git add src/slidestyle/build.py verify.py dist/slide-style.pptx
git commit -m "feat: assemble slide-style.pptx gallery"
```

### Task 11: Generate the style guide

**Files:**
- Create: `src/slidestyle/guide.py`

- [ ] **Step 1: Write `guide.py`** (emits `dist/style-guide.md` — tokens + per-layout usage + arch decision tree)

```python
"""Emit dist/style-guide.md — the usage guide handed to Claude at generation time."""
from pathlib import Path
from . import tokens as t

GUIDE = """# Slide Style Guide

Apple-Keynote minimalism · English · 16:9. Professionalism from typography,
hierarchy, color cards, highlights, and architecture diagrams — never decoration.

## Tokens

### Neutral scale
| Token | Hex | Use |
|---|---|---|
| Ink | #1D1D1F | titles / primary text |
| Graphite | #424245 | strong body |
| Slate | #6E6E73 | secondary / caption |
| Silver | #AEAEB2 | muted |
| Hairline | #D2D2D7 | dividers / borders |
| Mist | #F5F5F7 | surface |
| White | #FFFFFF | canvas |

### Accent ramps (900/800/600/400/300/100) — default accent1 = Blue
| Step | Blue | Teal | Orange |
|---|---|---|---|
| 900 | #16337A | #0B5F60 | #7C2D12 |
| 800 (text) | #1D4ED8 | #0A6E6F | #C2410C |
| 600 (fill) | #2563EB | #22B5B7 | #F97316 |
| 400 | #60A5FA | #6FD6D8 | #FDA55A |
| 300 (highlight) | #93C5FD | #A2E8E9 | #FDBA8C |
| 100 (tint) | #EAF2FE | #E8FBFC | #FFF3EA |

**Rules:** accent *text* → 800; fills/bars/shapes → 600; highlight bg → 300/100;
deep section bg → 900 (white text). One accent per deck, OR blue/teal/orange
together as categorical colors (diagram stages, KPI categories, chart series).

### Type (Helvetica Neue → Arial)
Cover 54/600 · Heading 34/600 · Statement 40/600 · Kicker 12/600 UPPERCASE
tracked · Body 18/400 Graphite · Caption 13/400 Slate.

## Layouts — when to use each
1. **Cover** — deck title; accent bar + kicker + big title.
2. **Section divider** — chapter breaks; accent-900 full bleed, white text.
3. **Big statement** — one bold sentence; the payoff slide.
4. **Heading + body** — standard content; title + hierarchical body.
5. **Minimal list** — 3–5 short points, accent square markers.
6. **Two-column** — compare / text|visual.
7. **Color cards / KPI** — 2–4 metric tiles; big number in accent-800.
8. **Highlight / callout** — one key term on accent-300 tint.
9. **Architecture** — see decision tree below.
10. **Image + caption** — visual right, body left, caption in Slate.
11. **Quote** — large centered quotation + attribution.
12. **Closing** — thank-you / contact.

## Architecture-diagram decision tree
- Simple flow / pipeline → **Route A, Pattern A** (horizontal flow, one focus node).
- System layers → **Route A, Pattern B** (stacked bands, 3 accents as categories).
- Grouping / boundaries → **Route A, Pattern C** (nested container).
- Many nodes, specialized type (sequence / ER / state / UML), or "publication-grade"
  → **Route B**: generate SVG in this palette (see `src/slidestyle/svg/`) and embed.

### How to prompt generation
Give Claude: the content (title, bullets, concept) + the target accent + which
layout(s). Claude fills the matching builder in `slidestyle.layouts` (Route A) or
`slidestyle.svg` (Route B), then you polish the `.pptx` by hand.
"""

def write(path="dist/style-guide.md"):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(GUIDE, encoding="utf-8")
    return path

if __name__ == "__main__":
    print("wrote", write())
```

- [ ] **Step 2: Generate and sanity-check**

Run:
```bash
uv run python -m slidestyle.guide && head -20 dist/style-guide.md
```
Expected: file written; header + tokens visible.

- [ ] **Step 3: Commit**

```bash
git add src/slidestyle/guide.py dist/style-guide.md
git commit -m "feat: style-guide.md generator"
```

---

## Phase 5 — Route B: SVG generation (OPTIONAL / bonus)

Only needed for complex, publication-grade diagrams. Ship the core (Phases 0–4)
first; this phase is independently valuable and can be deferred.

### Task 12: Our-palette SVG generators

**Files:**
- Create: `src/slidestyle/svg/__init__.py`, `src/slidestyle/svg/style.py`, `src/slidestyle/svg/generate.py`

- [ ] **Step 1: `svg/__init__.py`**
```python
__all__ = ["style", "generate"]
```

- [ ] **Step 2: `svg/style.py`** — palette as hex for SVG
```python
"""SVG palette tokens (hex) mirroring slidestyle.tokens."""
INK="#1D1D1F"; GRAPHITE="#424245"; SLATE="#6E6E73"; SILVER="#AEAEB2"
HAIRLINE="#D2D2D7"; MIST="#F5F5F7"; WHITE="#FFFFFF"
RAMPS={
 "blue":{"c900":"#16337A","c800":"#1D4ED8","c600":"#2563EB","c400":"#60A5FA","c300":"#93C5FD","c100":"#EAF2FE"},
 "teal":{"c900":"#0B5F60","c800":"#0A6E6F","c600":"#22B5B7","c400":"#6FD6D8","c300":"#A2E8E9","c100":"#E8FBFC"},
 "orange":{"c900":"#7C2D12","c800":"#C2410C","c600":"#F97316","c400":"#FDA55A","c300":"#FDBA8C","c100":"#FFF3EA"},
}
FONT='-apple-system,"Helvetica Neue",Arial,sans-serif'
```

- [ ] **Step 3: `svg/generate.py`** — a flow generator (viewBox 0 0 960 540) borrowing fireworks' architecture layout rules, our style
```python
"""Diagram-type SVG generators in the Apple-minimal palette.
Borrows fireworks-tech-graph's per-type layout rules; restyled to our tokens."""
from xml.sax.saxutils import escape
from . import style as s

def _box(x, y, w, h, label, sub=None, focus=False, accent="blue"):
    r = s.RAMPS[accent]
    fill = r["c100"] if focus else s.WHITE
    stroke = r["c600"] if focus else s.HAIRLINE
    tcol = r["c800"] if focus else s.GRAPHITE
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" '
           f'fill="{fill}" stroke="{stroke}" stroke-width="1.75"/>']
    out.append(f'<text x="{x+w/2}" y="{y+h/2}" text-anchor="middle" '
               f'dominant-baseline="middle" font-family=\'{s.FONT}\' font-size="17" '
               f'font-weight="600" fill="{tcol}">{escape(label)}</text>')
    if sub:
        out.append(f'<text x="{x+w/2}" y="{y+h/2+20}" text-anchor="middle" '
                   f'font-family=\'{s.FONT}\' font-size="12" fill="{s.SLATE}">{escape(sub)}</text>')
    return "".join(out)

def _arrow(x1, y, x2):
    return (f'<line x1="{x1}" y1="{y}" x2="{x2-8}" y2="{y}" stroke="{s.SILVER}" '
            f'stroke-width="1.75" marker-end="url(#ah)"/>')

def flow_svg(title, nodes, focus_index=None, accent="blue"):
    """nodes = [(label, sub), ...]. Returns an SVG string (960x540)."""
    W, H = 960, 540
    n = len(nodes)
    bw, bh, gap = 170, 90, 44
    total = n*bw + (n-1)*gap
    x0 = (W-total)/2; y = 250
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">',
             f'<defs><marker id="ah" markerWidth="10" markerHeight="10" refX="8" refY="3" '
             f'orient="auto"><path d="M0,0 L8,3 L0,6 Z" fill="{s.SILVER}"/></marker></defs>',
             f'<rect width="{W}" height="{H}" fill="{s.WHITE}"/>',
             f'<text x="60" y="90" font-family=\'{s.FONT}\' font-size="30" font-weight="600" '
             f'fill="{s.INK}">{escape(title)}</text>']
    x = x0
    for i, (label, sub) in enumerate(nodes):
        if i > 0:
            parts.append(_arrow(x-gap, y+bh/2, x))
        parts.append(_box(x, y, bw, bh, label, sub, focus=(i == focus_index), accent=accent))
        x += bw + gap
    parts.append("</svg>")
    return "".join(parts)
```

- [ ] **Step 4: Verify SVG is well-formed**
```bash
uv run python -c "
from xml.dom.minidom import parseString
from slidestyle.svg.generate import flow_svg
svg=flow_svg('How a deck is generated',
  [('Content','concept'),('Style template','theme'),('Claude','python-pptx'),('.pptx','editable')],
  focus_index=1)
parseString(svg); open('dist/sample-flow.svg','w').write(svg); print('valid svg', len(svg),'bytes')
"
```
Expected: `valid svg <N> bytes` (parses without error).

- [ ] **Step 5: Commit**
```bash
git add src/slidestyle/svg/ dist/sample-flow.svg
git commit -m "feat: our-palette SVG flow generator (Route B)"
```

### Task 13: Embed SVG into a slide (PNG fallback + true SVG)

**Files:**
- Create: `src/slidestyle/svg/embed.py`

- [ ] **Step 1: Write `embed.py`** — insert PNG (always renders) + attach the SVG blip for editability
```python
"""Embed an SVG into a pptx slide: PNG fallback (renders everywhere) plus an
svgBlip reference so PowerPoint 365/2016+ can 'Convert to Shape' for editing."""
import io
from pptx.util import Inches
from pptx.oxml.ns import qn, nsmap

SVG_NS = "http://schemas.microsoft.com/office/drawing/2016/SVG/main"

def embed_svg(slide, svg_bytes: bytes, left, top, width, height):
    import cairosvg  # requires the [svg] extra
    png = cairosvg.svg2png(bytestring=svg_bytes, output_width=1920)
    pic = slide.shapes.add_picture(io.BytesIO(png), Inches(left), Inches(top),
                                   Inches(width), Inches(height))
    # add the SVG as a related image part and reference it via svgBlip
    svg_part, svg_rId = slide.part.get_or_add_image_part(io.BytesIO(svg_bytes))  # see note
    blip = pic._element.blipFill.find(qn("a:blip"))
    ext_lst = blip.makeelement(qn("a:extLst"), {})
    ext = blip.makeelement(qn("a:ext"), {"uri": "{96DAC541-7B7A-43D3-8B79-37D633B846F1}"})
    svg_blip = ext.makeelement(f"{{{SVG_NS}}}svgBlip",
                               {f"{{{nsmap['r']}}}embed": svg_rId})
    ext.append(svg_blip); ext_lst.append(ext); blip.append(ext_lst)
    return pic
```
Note on `get_or_add_image_part`: python-pptx registers images by content type. SVG may need the content type registered — if `get_or_add_image_part` rejects SVG, fall back to `slide.part.package` image-part API or skip the svgBlip and ship PNG-only. **PNG-only is an acceptable degrade** (renders correctly; just not shape-editable). Keep the try/except:

```python
    try:
        svg_part, svg_rId = slide.part.get_or_add_image_part(io.BytesIO(svg_bytes))
        # ... svgBlip injection above ...
    except Exception:
        pass  # PNG-only fallback; diagram still renders
```

- [ ] **Step 2: Verify a diagram embeds and the deck still opens**
```bash
uv run pip install -e '.[svg]' 2>/dev/null; uv run python -c "
from pptx import Presentation
from slidestyle.theme import apply_theme
from slidestyle.svg.generate import flow_svg
from slidestyle.svg.embed import embed_svg
prs=Presentation(); apply_theme(prs)
s=prs.slides.add_slide(prs.slide_layouts[6])
svg=flow_svg('Pipeline',[('A',None),('B',None),('C',None)],focus_index=1).encode()
embed_svg(s,svg,0.9,2.5,11.5,3)
prs.save('/tmp/embed.pptx')
print('embedded; shapes', len(s.shapes))
Presentation('/tmp/embed.pptx'); print('reopens OK')
"
```
Expected: `embedded; shapes 1` then `reopens OK`. (If cairosvg unavailable, this task is skipped — core deck is unaffected.)

- [ ] **Step 3: Commit**
```bash
git add src/slidestyle/svg/embed.py
git commit -m "feat: embed SVG diagrams into pptx (png fallback + svgBlip)"
```

---

## Self-Review (completed by plan author)

**Spec coverage:**
- Palette (neutrals + 3 ramps, default blue) → Task 2 (tokens) + Task 3 (theme). ✅
- Helvetica Neue, 16:9 → Task 3. ✅
- Type scale → Task 2 + Task 4. ✅
- 12 archetypes → Tasks 6–9. ✅
- Architecture hybrid (Route A kit + 3 patterns; Route B SVG) → Task 5 (kit) + Task 8 (patterns) + Tasks 12–13 (SVG). ✅
- Deliverables `slide-style.pptx` + `style-guide.md` → Tasks 10–11. ✅
- Decision tree in guide → Task 11. ✅

**Placeholder scan:** No TBD/TODO; every code step is complete runnable code. The one honest degrade (svgBlip → PNG-only) is documented with fallback code, not a placeholder.

**Type consistency:** builder signature `fn(slide, accent="blue")` is uniform across all 14 builders and matches `build.py`'s call `fn(slide, accent=primary)`. `shapes.box(kind=...)`, `ramp(name, step)`, `textbox(box, ...)` signatures are used consistently everywhere.

**Known risk (flagged, not blocking):** `get_or_add_image_part` accepting SVG is version-dependent; Task 13 degrades to PNG-only cleanly. Route B is optional, so this never blocks the deliverable.
