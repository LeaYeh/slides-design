"""Structural checks for the built deck. Grows as tasks land."""
import sys
from pptx import Presentation

def main(path="dist/slide-style.pptx"):
    prs = Presentation(path)
    print(f"opened {path}: {len(prs.slides.__iter__.__self__._sldIdLst)} slide ids")
    print(f"slide size EMU: {prs.slide_width} x {prs.slide_height}")

if __name__ == "__main__":
    main(*sys.argv[1:])
