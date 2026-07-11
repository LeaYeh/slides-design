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
    try:
        svg_part, svg_rId = slide.part.get_or_add_image_part(io.BytesIO(svg_bytes))
        blip = pic._element.blipFill.find(qn("a:blip"))
        ext_lst = blip.makeelement(qn("a:extLst"), {})
        ext = blip.makeelement(qn("a:ext"), {"uri": "{96DAC541-7B7A-43D3-8B79-37D633B846F1}"})
        svg_blip = ext.makeelement(f"{{{SVG_NS}}}svgBlip",
                                   {f"{{{nsmap['r']}}}embed": svg_rId})
        ext.append(svg_blip); ext_lst.append(ext); blip.append(ext_lst)
    except Exception:
        pass  # PNG-only fallback; diagram still renders
    return pic
