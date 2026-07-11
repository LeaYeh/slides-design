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
