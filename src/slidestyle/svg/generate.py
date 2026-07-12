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


# --- Claude-Official-inspired palette (warm, layered, with depth) ---
_BG   = "#F8F6F3"
_STRK = "#4A4A4A"
_TX   = "#1A1A1A"
_TX2  = "#6A6A6A"
_LN   = "#5A5A5A"
_TINT = {"blue": "#A8C5E6", "green": "#9DD4C7", "beige": "#F4E4C1", "gray": "#E8E6E3"}

def _cnode(x, y, w, h, cat, name, tint):
    fill = _TINT[tint]
    parts = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{fill}" '
             f'stroke="{_STRK}" stroke-width="2.5" filter="url(#sh)"/>']
    parts.append(_txt(x+w/2, y+24, cat.upper(), size=11, color=_TX2, weight=700, track=1.2))
    parts.append(_txt(x+w/2, y+50, name, size=16, color=_TX, weight=600))
    return "".join(parts)

def _cband(x, y, w, h, tint_hex):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="{tint_hex}" '
            f'stroke="#D8D3CA" stroke-width="1.5" stroke-dasharray="7 5"/>')

def _ccyl(cx, top, w, h, cat, name):
    x = cx - w/2; ry = 10
    body = (f'<path d="M{x},{top+ry} a{w/2},{ry} 0 0 1 {w},0 v{h-2*ry} '
            f'a{w/2},{ry} 0 0 1 -{w},0 Z" fill="{_TINT["gray"]}" stroke="{_STRK}" '
            f'stroke-width="2.5" filter="url(#sh)"/>')
    lid = (f'<ellipse cx="{cx}" cy="{top+ry}" rx="{w/2}" ry="{ry}" fill="#F1EFEC" '
           f'stroke="{_STRK}" stroke-width="2.5"/>')
    return (body + lid
            + _txt(cx, top+h/2-4, cat.upper(), size=10, color=_TX2, weight=700, track=1.0)
            + _txt(cx, top+h/2+13, name, size=11, color=_TX, weight=600))

def _cdoc(x, y, w, h, cat, name):
    wave = h*0.16
    d = f'M{x},{y} h{w} v{h-wave} q{-w/4},{wave*1.4} {-w/2},0 t{-w/2},0 Z'
    return (f'<path d="{d}" fill="{_TINT["beige"]}" stroke="{_STRK}" stroke-width="2.5" '
            f'stroke-linejoin="round" filter="url(#sh)"/>'
            + _txt(x+w/2, y+22, cat.upper(), size=10, color=_TX2, weight=700, track=1.0)
            + _txt(x+w/2, y+44, name, size=14, color=_TX, weight=600))

def _cdia(cx, cy, half, name):
    pts = f"{cx},{cy-half} {cx+half},{cy} {cx},{cy+half} {cx-half},{cy}"
    return (f'<polygon points="{pts}" fill="{_TINT["blue"]}" stroke="{_STRK}" '
            f'stroke-width="2.5" filter="url(#sh)"/>'
            + _txt(cx, cy-6, "DECISION", size=9, color=_TX2, weight=700, track=1.0)
            + _txt(cx, cy+11, name, size=13, color=_TX, weight=600))

def _cflow(pts, *, dash=None, r=10, arrow=True):
    d = f'M {pts[0][0]} {pts[0][1]} '
    for i in range(1, len(pts)-1):
        (x0, y0), (x1, y1), (x2, y2) = pts[i-1], pts[i], pts[i+1]
        def u(ax, ay, bx, by):
            dx, dy = bx-ax, by-ay
            L = math.hypot(dx, dy) or 1
            return dx/L, dy/L
        ux, uy = u(x0, y0, x1, y1); vx, vy = u(x1, y1, x2, y2)
        d += f'L {x1-ux*r:.1f} {y1-uy*r:.1f} Q {x1} {y1} {x1+vx*r:.1f} {y1+vy*r:.1f} '
    d += f'L {pts[-1][0]} {pts[-1][1]}'
    da = f' stroke-dasharray="{dash}"' if dash else ""
    mk = ' marker-end="url(#car)"' if arrow else ""
    return f'<path d="{d}" fill="none" stroke="{_LN}" stroke-width="2"{da}{mk}/>'

def _clabel(cx, cy, text):
    w = len(text) * 6.6 + 12
    return (_rrect(cx-w/2, cy-10, w, 20, 4, _BG)
            + _txt(cx, cy, text, size=12, color=_LN, weight=500))

def swimlane_svg():
    """MLOps-lifecycle swim-lane in a warm, layered, Claude-official-inspired style
    (1280x760): soft semantic node tints, dark strokes + depth, category labels,
    semantic solid/dashed connectors, and a legend."""
    W, H = 1280, 760
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family=\'{s.FONT}\'>',
         '<defs>'
         '<marker id="car" viewBox="0 0 8 8" refX="6.5" refY="4" markerWidth="7" '
         f'markerHeight="7" orient="auto"><polygon points="0 0, 8 4, 0 8" fill="{_LN}"/></marker>'
         '<filter id="sh" x="-20%" y="-20%" width="140%" height="150%">'
         '<feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#000000" flood-opacity="0.14"/>'
         '</filter></defs>',
         f'<rect width="{W}" height="{H}" fill="{_BG}"/>']

    # title + subtitle (centered, warm)
    p.append(_txt(W/2, 56, "ML lifecycle across environments", size=30, color=_TX, weight=700))
    p.append(_txt(W/2, 88, "From dev experimentation to production retraining",
                  size=15, color=_TX2, weight=400))

    # lane bands + left labels
    p.append(_cband(120, 150, 1040, 215, "#FBF7F0"))   # Dev — warm
    p.append(_cband(120, 445, 1040, 215, "#F2F2F0"))   # Prod — cool
    p.append(_txt(70, 257, "Dev", size=15, color=_TX2, weight=700, anchor="middle"))
    p.append(_txt(64, 545, "Staging", size=15, color=_TX2, weight=700, anchor="middle"))
    p.append(_txt(64, 566, "/ Prod", size=15, color=_TX2, weight=700, anchor="middle"))

    # shared data store straddling the gap
    p.append(_ccyl(182, 335, 132, 150, "Store", "Data Warehouse"))

    nodes_x = [285, 520, 755]
    nw, nh = 185, 84
    # --- Dev lane ---
    dev_y, dcy = 220, 262
    devs = [("Ingest", "Data Prep", "green"), ("Train", "Model Training", "green"),
            ("Evaluate", "Model Validation", "green")]
    for x, (cat, nm, tint) in zip(nodes_x, devs):
        p.append(_cnode(x, dev_y, nw, nh, cat, nm, tint))
    p.append(_cflow([(nodes_x[0]+nw, dcy), (nodes_x[1], dcy)]))
    p.append(_cflow([(nodes_x[1]+nw, dcy), (nodes_x[2], dcy)]))
    # feedback (dashed control)
    fx1, fx2 = nodes_x[2]+nw/2, nodes_x[1]+nw/2
    p.append(_cflow([(fx1, dev_y), (fx1, dev_y-30), (fx2, dev_y-30), (fx2, dev_y)], dash="4 3"))
    p.append(_txt((fx1+fx2)/2, dev_y-38, "hyperparameter tuning", size=12, color=_LN))
    # artifact
    p.append(_cdoc(970, dev_y, 150, nh, "Artifact", "Trained model"))
    p.append(_cflow([(nodes_x[2]+nw, dcy), (970, dcy)]))

    # --- Prod lane ---
    prod_y, pcy = 515, 557
    prods = [("Ingest", "Data Prep", "gray"), ("Train", "Retrain", "blue"),
             ("Evaluate", "Validate", "gray")]
    for x, (cat, nm, tint) in zip(nodes_x, prods):
        p.append(_cnode(x, prod_y, nw, nh, cat, nm, tint))
    p.append(_cflow([(nodes_x[0]+nw, pcy), (nodes_x[1], pcy)]))
    p.append(_cflow([(nodes_x[1]+nw, pcy), (nodes_x[2], pcy)]))
    dcx = 1010
    p.append(_cdia(dcx, pcy, 62, "Perf drop?"))
    p.append(_cflow([(nodes_x[2]+nw, pcy), (dcx-62, pcy)]))
    # retrain loop (dashed write)
    p.append(_cflow([(dcx, pcy+62), (dcx, 632), (nodes_x[0]+nw/2, 632),
                     (nodes_x[0]+nw/2, prod_y+nh)], dash="6 4"))
    p.append(_txt(dcx-16, pcy+50, "yes", size=12, color=_LN, weight=600, anchor="end"))

    # --- cross-lane connectors (dashed control) with chips ---
    p.append(_cflow([(226, 372), (256, 372), (256, dcy), (nodes_x[0], dcy)], dash="4 3"))
    p.append(_clabel(256, 340, "POC data"))
    p.append(_cflow([(226, 448), (256, 448), (256, pcy), (nodes_x[0], pcy)], dash="4 3"))
    p.append(_clabel(256, 480, "batch fetch"))
    p.append(_cflow([(1045, dev_y+nh), (1045, 445)], dash="6 4"))
    p.append(_clabel(1045, 405, "deploy"))

    # --- legend (bottom-right, stacked) ---
    lx, ly, lw, lh = 1024, 626, 232, 118
    p.append(_rrect(lx, ly, lw, lh, 10, "#FFFFFF", _STRK, 1.5))
    p.append(_txt(lx+18, ly+24, "Legend", size=13, color=_TX, weight=700, anchor="start"))
    rows = [("", "primary flow"), ("4 3", "control · trigger"), ("6 4", "write · retrain")]
    for i, (dash, lab) in enumerate(rows):
        y = ly+50+i*24
        da = f' stroke-dasharray="{dash}"' if dash else ""
        p.append(f'<line x1="{lx+18}" y1="{y}" x2="{lx+48}" y2="{y}" stroke="{_LN}" '
                 f'stroke-width="2"{da} marker-end="url(#car)"/>')
        p.append(_txt(lx+58, y, lab, size=12, color=_TX2, anchor="start"))
    p.append("</svg>")
    return "".join(p)
