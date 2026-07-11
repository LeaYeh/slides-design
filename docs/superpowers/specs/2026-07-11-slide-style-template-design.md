# Slide Style Template — Design Spec

**Date:** 2026-07-11
**Status:** Approved (brainstorming)

## Goal

A reusable **PowerPoint style template** that encodes one consistent, professional
presentation look. It is the durable style artifact. Later, the workflow is:

> `slide-style.pptx` template + user-provided content + visual direction
> → Claude generates a `.pptx` deck → user manually polishes the result.

This spec covers **building the template + its usage guide only**. It does NOT build an
automatic deck generator — generation happens later, in a separate session, with the
template handed to Claude as one input.

## Aesthetic

Apple-Keynote minimalism. Professionalism comes from **typography, text hierarchy,
color cards, highlights, and architecture diagrams** — never from decoration.

- English content only (any source Chinese is translated to English).
- 16:9 widescreen.
- Generous whitespace; one idea per slide; a single accent per slide by default.

## Color System

Two tracks: a neutral hierarchy (does the structural work) + three interchangeable
"science-tech" accent ramps.

### Neutral scale (hierarchy)

| Token | Hex | Use |
|---|---|---|
| Ink | `#1D1D1F` | Titles, primary text (softer than pure black) |
| Graphite | `#424245` | Strong body text |
| Slate | `#6E6E73` | Secondary text, captions |
| Silver | `#AEAEB2` | Muted / disabled |
| Hairline | `#D2D2D7` | Dividers, box borders |
| Mist | `#F5F5F7` | Light surface / neutral card |
| White | `#FFFFFF` | Canvas |

### Accent ramps (900 / 800 / 600 / 400 / 300 / 100)

**Default accent1 = Tech Blue.** All three are tuned to similar lightness/energy so
they read as one family.

| Step | 🔵 Tech Blue | 🟢 42-Vienna Teal | 🟠 Tech Orange |
|---|---|---|---|
| 900 (deep bg) | `#16337A` | `#0B5F60` | `#7C2D12` |
| 800 (accent **text**) | `#1D4ED8` | `#0A6E6F` | `#C2410C` |
| 600 (primary **fill** ★) | `#2563EB` | `#22B5B7` | `#F97316` |
| 400 (mid) | `#60A5FA` | `#6FD6D8` | `#FDA55A` |
| 300 (highlight) | `#93C5FD` | `#A2E8E9` | `#FDBA8C` |
| 100 (tint surface) | `#EAF2FE` | `#E8FBFC` | `#FFF3EA` |

### Usage rules

- **Accent text** on white → step **800** (600 fails contrast on white for text).
- **Fills / bars / shapes / icons** → step **600**.
- **Highlight background** behind a key term → step **300** (or **100** for subtle).
- **Deep section / cover background** → step **900**, white text on top.
- **Two usage modes, both supported:**
  1. *Single-accent deck* — pick one ramp; whole deck uses it.
  2. *Categorical* — blue/teal/orange together for diagram stages, KPI categories,
     chart series.

## Typography

- **Font stack:** `Helvetica Neue` → `Arial` fallback (zero-install, Apple feel,
  portable across PowerPoint / Keynote / Google Slides). No font embedding needed.
- **Scale** (weight = 600 semibold for display/headings, 400 regular for body):

| Role | Size / Weight | Color | Notes |
|---|---|---|---|
| Cover title | 52–60 / 600 | Ink | Tight tracking (-0.02em) |
| Heading | 34 / 600 | Ink | Slide titles |
| Statement | 40 / 600 | Ink | Big single-sentence slides |
| Kicker (overline) | 12 / 600 | Accent 800 | Uppercase, letter-spaced 0.14em |
| Body | 18 / 400 | Graphite | Generous line-height |
| Caption / footnote | 13 / 400 | Slate | — |

## Layout Masters — 12 archetypes

Each is a slide layout in the template's master.

1. **Cover / Title** — accent bar, kicker, large title, subtitle. Lots of whitespace.
2. **Section divider** — full-bleed accent-900 background, section number + title, white text.
3. **Big statement** — one bold centered sentence; a key phrase may be accent-800.
4. **Heading + hierarchical body** — title top-left, structured body (heading/body/sub).
5. **Minimal bullet list** — clean list, generous spacing, small accent-600 square marker.
6. **Two-column** — text|text or text|visual split.
7. **Color cards / KPI tiles** — row of 2–4 tiles on tint surfaces; big number (accent-800) + label.
8. **Highlight / callout** — key term/number highlighted with accent-300 background + supporting text.
9. **Architecture diagram** — a *family*, not one slide. See "Architecture Diagram Subsystem" below.
10. **Image + caption** — full or half image with caption in Slate.
11. **Quote** — large quotation with attribution.
12. **Closing** — minimal end slide (accent bar, "Thank you", contact).

## Architecture Diagram Subsystem

Architecture diagrams are a key focus. **Hybrid strategy** — routine diagrams use native
PowerPoint shapes (fully editable, no toolchain); complex/publication-grade diagrams are
generated as SVG in our palette and embedded.

### Route A — native pptx shapes (the default)

A **shape kit** of locked-style, real PowerPoint shapes (rounded rectangles + connectors)
Claude places and edits directly:

- `box` (plain node, white/Mist), `focus box` (accent-100 fill + accent-600 border +
  accent-800 text), `neutral box` (Mist), `arrow` (thin, Silver/Slate), `group label`
  (kicker-style small caps), `legend` (categorical dots).

Three ready patterns cover ~90% of needs:
- **Pattern A — horizontal flow**: left→right pipeline/stages, one focus node.
- **Pattern B — layered stack**: horizontal bands, three accents as categories.
- **Pattern C — nested container**: a boundary box holding sub-nodes (grouping).

Visual rules: hairline borders `#D2D2D7`, ~10px radius, generous padding, depth via
grouping not decoration; thin arrows; ≤5–7 nodes per slide.

### Route B — SVG generation, embedded (for complex/high-polish diagrams)

Prior art: [`yizhiyanhua-ai/fireworks-tech-graph`](https://github.com/yizhiyanhua-ai/fireworks-tech-graph)
(a skill that turns NL → SVG technical diagrams). We **borrow its structure, restyle to ours**:

- Its **diagram-type classification + per-type layout rules** (architecture, data-flow,
  flowchart, sequence, ER, state-machine, etc.) and its **validate → visual-review loop**.
- Rendered with **our tokens** (neutral scale + 3 accent ramps, Helvetica Neue) — not its
  8 styles. One new "style" = our Apple-minimal palette.
- Export SVG (via `cairosvg`), **insert into the pptx slide**; note in the guide that
  PowerPoint 365/2016+ can "Convert to Shape" for editing (fidelity caveat for Keynote /
  Google Slides).

### Decision tree (goes into `style-guide.md`)

- Simple flow / pipeline → Route A, Pattern A.
- System layers → Route A, Pattern B.
- Grouping / boundaries → Route A, Pattern C.
- Many nodes, specialized type (sequence/ER/state/UML), or "make it publication-grade"
  → Route B (SVG), pick the matching diagram-type rules, render in our palette, embed.

## Deliverables

- `slide-style.pptx` — the template: theme (neutrals + 3 accent ramps, default blue),
  Helvetica Neue font scheme, and the 12 slide layouts in the master.
- `style-guide.md` — tokens + per-layout guidance ("what it is, when to use, how to
  prompt Claude to fill it") to hand to Claude alongside content during generation.
- `style-guide.md` also carries the **architecture-diagram decision tree** + the SVG
  route's diagram-type rules (restyled to our palette) + per-pattern prompting guidance.
- `style-preview.html` / `style-preview-v2.html` / `style-preview-arch.html` — visual
  reference (already built).

**Not included (YAGNI):** automatic deck generator, `tokens.json`, CJK fonts, 4:3 variant.
The SVG route reuses fireworks-tech-graph's *approach*, not its code as a dependency.

## Build approach (for the plan)

python-pptx cannot cleanly author new slide *layouts* with placeholders from scratch,
so the template is authored by:
1. Defining the theme (`theme1.xml`: color scheme with the 3 accent ramps mapped to
   accent1–6 + neutrals, and the Helvetica Neue font scheme) — via OOXML.
2. Building the 12 layouts in the slide master (placeholder + styled sample shapes),
   editing OOXML / starting from a blank base `.pptx` where python-pptx falls short.
3. The architecture shape kit + 3 patterns are built as real shapes on example slides.
4. The SVG route (Route B) is a small generator + our-palette style reference + the
   borrowed diagram-type layout rules and validation loop; SVGs are embedded into slides.
5. Verifying: open the produced `.pptx`, confirm theme colors, fonts, and each layout
   render correctly and are editable; for Route B, run the validate → visual-review loop.

Details and task breakdown belong to the implementation plan.
