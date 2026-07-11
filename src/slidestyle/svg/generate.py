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


# --- publication-grade swim-lane architecture (Route B, layout-rich) ---

import math

_LINE = "#B4B7BD"   # refined connector gray

def _rrect(x, y, w, h, r, fill, stroke=None, sw=1.5):
    st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}"{st} fill="{fill}"/>'

def _txt(x, y, text, *, size, color, weight=400, anchor="middle", track=0):
    ls = f' letter-spacing="{track}"' if track else ""
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" dominant-baseline="central" '
            f'font-family=\'{s.FONT}\' font-size="{size}" font-weight="{weight}" '
            f'fill="{color}"{ls}>{escape(text)}</text>')

def _node(x, y, w, h, label, *, kind, accent):
    r = s.RAMPS[accent]
    if kind == "warm":
        fill, stroke, tc = r["c100"], r["c600"], r["c800"]
    else:  # plain
        fill, stroke, tc = s.WHITE, s.HAIRLINE, s.GRAPHITE
    return (_rrect(x, y, w, h, 12, fill, stroke, 1.5)
            + _txt(x + w/2, y + h/2, label, size=15, color=tc, weight=600))

def _cylinder(cx, top, w, h, label):
    x = cx - w/2; ry = 9
    body = (f'<path d="M{x},{top+ry} a{w/2},{ry} 0 0 1 {w},0 v{h-2*ry} '
            f'a{w/2},{ry} 0 0 1 -{w},0 Z" fill="{s.MIST}" stroke="{s.HAIRLINE}" stroke-width="1.5"/>')
    lid = (f'<ellipse cx="{cx}" cy="{top+ry}" rx="{w/2}" ry="{ry}" '
           f'fill="{s.WHITE}" stroke="{s.HAIRLINE}" stroke-width="1.5"/>')
    t1 = _txt(cx, top + h/2 - 7, "Data", size=12, color=s.GRAPHITE, weight=600)
    t2 = _txt(cx, top + h/2 + 9, "Warehouse", size=12, color=s.GRAPHITE, weight=600)
    return body + lid + t1 + t2

def _diamond(cx, cy, half, label, accent):
    r = s.RAMPS[accent]
    pts = f"{cx},{cy-half} {cx+half},{cy} {cx},{cy+half} {cx-half},{cy}"
    return (f'<polygon points="{pts}" fill="{s.WHITE}" stroke="{r["c600"]}" stroke-width="1.5"/>'
            + _txt(cx, cy-6, "Perf", size=11, color=r["c800"], weight=600)
            + _txt(cx, cy+8, "drop?", size=11, color=r["c800"], weight=600))

def _document(x, y, w, h, label, accent):
    r = s.RAMPS[accent]
    wave = h*0.16
    d = (f'M{x},{y} h{w} v{h-wave} q{-w/4},{wave*1.4} {-w/2},0 t{-w/2},0 Z')
    return (f'<path d="{d}" fill="{r["c100"]}" stroke="{r["c600"]}" stroke-width="1.5" '
            f'stroke-linejoin="round"/>'
            + _txt(x + w/2, y + h/2 - 7, "Trained", size=12, color=r["c800"], weight=600)
            + _txt(x + w/2, y + h/2 + 9, "model", size=12, color=r["c800"], weight=600))

def _poly(pts, r=9, arrow=True):
    """Orthogonal connector through pts with rounded corners; optional end arrow."""
    d = f'M {pts[0][0]} {pts[0][1]} '
    for i in range(1, len(pts)-1):
        (x0, y0), (x1, y1), (x2, y2) = pts[i-1], pts[i], pts[i+1]
        def u(ax, ay, bx, by):
            dx, dy = bx-ax, by-ay
            L = math.hypot(dx, dy) or 1
            return dx/L, dy/L
        ux, uy = u(x0, y0, x1, y1); vx, vy = u(x1, y1, x2, y2)
        d += (f'L {x1-ux*r:.1f} {y1-uy*r:.1f} Q {x1} {y1} {x1+vx*r:.1f} {y1+vy*r:.1f} ')
    d += f'L {pts[-1][0]} {pts[-1][1]}'
    mk = ' marker-end="url(#chev)"' if arrow else ""
    return f'<path d="{d}" fill="none" stroke="{_LINE}" stroke-width="1.5"{mk}/>'

def _chip(cx, cy, text, color=None):
    color = color or s.SLATE
    w = len(text) * 6.4 + 12
    return (_rrect(cx - w/2, cy - 9, w, 18, 4, s.WHITE)
            + _txt(cx, cy, text, size=10.5, color=color, weight=600, track=0.6))

def _kicker(x, y, text, accent):
    return _txt(x, y, text.upper(), size=12, color=s.RAMPS[accent]["c800"],
                weight=700, anchor="start", track=1.6)

def _lane_label(cx, cy, text):
    return (f'<g transform="rotate(-90 {cx} {cy})">'
            + _txt(cx, cy, text.upper(), size=12, color=s.SLATE, weight=700, track=1.6)
            + '</g>')

def swimlane_svg():
    """A refined MLOps-lifecycle swim-lane diagram (1280x720)."""
    W, H = 1280, 720
    DEV, PROD = "orange", "blue"
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family=\'{s.FONT}\'>',
         '<defs>'
         '<marker id="chev" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6.5" '
         'markerHeight="6.5" orient="auto-start-reverse">'
         f'<path d="M1,1 L8,5 L1,9" fill="none" stroke="{_LINE}" stroke-width="1.6" '
         'stroke-linecap="round" stroke-linejoin="round"/></marker></defs>',
         f'<rect width="{W}" height="{H}" fill="{s.WHITE}"/>']

    # heading
    p.append(_kicker(56, 52, "Architecture", "blue"))
    p.append(_txt(56, 92, "ML lifecycle across environments", size=30, color=s.INK,
                  weight=600, anchor="start", track=-0.4))

    div = 425
    p.append(f'<line x1="40" y1="{div}" x2="{W-40}" y2="{div}" stroke="{s.HAIRLINE}" stroke-width="1"/>')

    # containers
    p.append(_rrect(200, 160, 905, 235, 14, s.MIST, s.HAIRLINE, 1.25))
    p.append(_kicker(222, 188, "ML Training Pipeline", DEV))
    p.append(_rrect(200, 455, 905, 235, 14, s.MIST, s.HAIRLINE, 1.25))
    p.append(_kicker(222, 483, "Staging / Prod Pipeline", PROD))

    # lane labels + shared store
    p.append(_lane_label(28, 277, "Dev"))
    p.append(_lane_label(28, 572, "Staging / Prod"))
    p.append(_cylinder(117, 355, 96, 140, "Data Warehouse"))

    # dev lane
    bw, bh = 180, 72
    dev_y, dcy = 235, 271
    dxs = [245, 495, 745]
    labels = ["Data Prep", "Model Training", "Model Validation"]
    for x, lb in zip(dxs, labels):
        p.append(_node(x, dev_y, bw, bh, lb, kind="warm", accent=DEV))
    p.append(_poly([(dxs[0]+bw, dcy), (dxs[1], dcy)]))
    p.append(_poly([(dxs[1]+bw, dcy), (dxs[2], dcy)]))
    # feedback arc
    ax1, ax2, ytop = dxs[2]+bw/2, dxs[1]+bw/2, dev_y
    p.append(_poly([(ax1, ytop), (ax1, ytop-38), (ax2, ytop-38), (ax2, ytop)], r=10))
    p.append(_txt((ax1+ax2)/2, ytop-46, "Hyperparameter tuning", size=11, color=s.SLATE, weight=600))
    # artifact
    p.append(_document(955, dev_y, 120, bh, "Trained model", DEV))
    p.append(_poly([(dxs[2]+bw, dcy), (955, dcy)]))

    # prod lane
    prod_y, pcy = 530, 566
    for x, lb in zip(dxs, ["Data Prep", "Retrain", "Validate"]):
        p.append(_node(x, prod_y, bw, bh, lb, kind="plain", accent=PROD))
    p.append(_poly([(dxs[0]+bw, pcy), (dxs[1], pcy)]))
    p.append(_poly([(dxs[1]+bw, pcy), (dxs[2], pcy)]))
    dcx = 1000
    p.append(_diamond(dcx, pcy, 60, "Perf drop?", PROD))
    p.append(_poly([(dxs[2]+bw, pcy), (dcx-60, pcy)]))
    # retrain loop
    p.append(_poly([(dcx, pcy+60), (dcx, 662), (dxs[0]+bw/2, 662), (dxs[0]+bw/2, prod_y+bh)], r=10))
    p.append(_txt(dcx+26, pcy+72, "YES", size=10.5, color=s.RAMPS[PROD]["c800"], weight=700))

    # cross-lane connectors (orthogonal) with chips
    p.append(_poly([(165, 388), (205, 388), (205, dcy), (dxs[0], dcy)], r=8))
    p.append(_chip(205, 340, "POC data"))
    p.append(_poly([(165, 462), (205, 462), (205, pcy), (dxs[0], pcy)], r=8))
    p.append(_chip(205, 508, "Batch fetch"))
    p.append(_poly([(1015, dev_y+bh), (1015, 455)], r=6))
    p.append(_chip(1015, 425, "Deploy"))

    p.append("</svg>")
    return "".join(p)
