"""Structural checks for the built deck."""
import sys
from pptx import Presentation
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from lxml import etree
from slidestyle.theme import NS

def main(path="dist/slide-style.pptx"):
    prs = Presentation(path)
    n = len(list(prs.slides))
    assert n == 15, f"expected 15 gallery slides, got {n}"
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
