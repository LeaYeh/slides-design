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
