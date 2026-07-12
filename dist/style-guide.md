# Slide Style Guide

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
- Multiple environments / a lifecycle with a shared store, feedback loops & a decision
  → **Route A, Pattern D** (swim-lane): rotated lane labels, a divider, a shared cylinder
  straddling it, a titled container per lane, a horizontal flow with a feedback arc,
  specialized shapes (cylinder/document/diamond), and labeled cross-lane connectors.
  Warm accent for one lane, cool/neutral for the other. **Layout is the message — align
  boxes on a grid, keep one focus per lane, let it breathe.** Two forms:
  `arch_swimlane` (native shapes — editable in PowerPoint) and `arch_swimlane_svg`
  (publication-grade SVG in the same palette, embedded as a crisp image — regenerate
  to edit; needs the `[svg]` extra). Use SVG for the hero/handout, native for quick edits.
- Many nodes, specialized type (sequence / ER / state / UML), or "publication-grade"
  → **Route B**: generate SVG in this palette (see `src/slidestyle/svg/`) and embed.

### How to prompt generation
Give Claude: the content (title, bullets, concept) + the target accent + which
layout(s). Claude fills the matching builder in `slidestyle.layouts` (Route A) or
`slidestyle.svg` (Route B), then you polish the `.pptx` by hand.
