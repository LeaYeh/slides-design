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
