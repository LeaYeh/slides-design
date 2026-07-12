# slidestyle

Apple-Keynote-minimal PowerPoint style template generator. A small brand system —
tokens, typography, layouts, and architecture-diagram builders — that produces
consistent `.pptx` decks and publication-grade SVG diagrams.

Professionalism comes from typography, hierarchy, color, and layout — never decoration.

## Install

```bash
uv sync                 # core
uv sync --extra svg     # + cairosvg, for SVG diagrams & rasterized icons
```

## Quick start

```bash
uv run python -m slidestyle.build      # -> dist/slide-style.pptx (gallery of every layout)
uv run python -m slidestyle.guide      # -> dist/style-guide.md   (the design guide)
uv run python -m slidestyle.assets     # -> assets/               (photo + tool-icon cache)
```

Open `dist/slide-style.pptx` to see one labeled example slide per archetype.

## What's inside

| Module | Purpose |
|---|---|
| `tokens` / `theme` | Neutral scale + blue/teal/orange accent ramps; injects a real OOXML theme (Helvetica Neue, 16:9) |
| `layouts` | 16 slide builders — cover, section, statement, KPI cards, highlight, quote, closing, and 5 architecture patterns |
| `svg/` | Route-B SVG generators (flow, swim-lane) in the same palette, embedded as crisp images |
| `assets` | Personal photo + official-color tool logos for diagrams (see below) |
| `guide` | Emits `dist/style-guide.md`, the usage guide handed to Claude at generation time |

### Layouts

`cover`, `section`, `statement`, `heading_body`, `bullet_list`, `two_column`,
`color_cards`, `highlight`, `arch_flow`, `arch_layered`, `arch_nested`,
`arch_swimlane`, `arch_swimlane_svg`, `image_caption`, `quote`, `closing` — each
takes `(slide, accent="blue")`.

```python
from pptx import Presentation
from slidestyle import layouts, tokens as t
from slidestyle.theme import apply_theme

prs = Presentation(); apply_theme(prs, primary="teal")
slide = prs.slides.add_slide(prs.slide_layouts[6])
layouts.cover(slide, accent="teal")
prs.save("out.pptx")
```

## Personal assets — photo & tool icons

`slidestyle.assets` caches a profile photo and **official-color brand logos** under
`assets/`, so architecture diagrams can label nodes with the real tech. Icons are
Devicon (true multi-color) where available, Simple Icons (official-color) otherwise.

Sources: the [jsonresume registry](https://registry.jsonresume.org/LeaYeh) (photo +
skills) plus an optional local doc (`SLIDESTYLE_JD_DOC`, gitignored — skipped when
absent). Any recognised tool that appears in a source gets a logo downloaded.

```bash
uv run python -m slidestyle.assets     # refresh the cache
```

```python
from slidestyle import assets

assets.icons().keys()                     # available logo names
assets.icon_image("Kubernetes", x, y, 52) # <image> (data URI) for an SVG diagram node
assets.add_photo(slide, 0.5, 0.5, 1.5)    # profile photo on a pptx slide (Inches)
assets.add_icon(slide, "PyTorch", 3, 0.5, 0.8)  # tool logo on a pptx slide (needs [svg])
```

Reads go through `assets/manifest.json`, so decks build offline. The cached
`resume.json` is gitignored; only generic logo names land in the manifest.

See `dist/icon-catalog.png` for the full logo set and `dist/sample-icons.png` for a
branded pipeline diagram using them.

## Architecture-diagram guidance

`dist/style-guide.md` documents a decision tree for picking a diagram pattern (flow /
layered / nested / swim-lane), the token system, and the icon convention. Regenerate
it with `python -m slidestyle.guide`.
