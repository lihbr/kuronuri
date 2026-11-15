"""The en and em spaces, U+2002 and U+2003: empty, half an em and an em
wide.

Redaction's are copies of its en and em dashes: in Italic, but on 100, they
still have the dash's outline, so "A B" (an en space) set as "A–B"; in
every style and grid they have the dash's advance, 518 and 668 units smooth,
a grid's dash's in Italic, and the smooth 518 and 668, off the grid, in
Regular's and Bold's pixel fonts. They are drawn anew, empty, as wide as
spaces are by name: an en, half the em, and the em, on the grid
(pixel.snap_advance: the em space as wide as full-width forms, 980 on 35
and 70). The dashes are their own glyphs, and stay as drawn.

Redaction's other spaces (space, no-break, thin, hair, zero width) are
empty and stay as they are.
"""

from fontTools.pens.ttGlyphPen import TTGlyphPen

import pixel

from .shapes import add

# code point: (Redaction's glyph name, its advance, over the em)
SPACES = {0x2002: ("enspace", 1 / 2), 0x2003: ("emspace", 1)}
CODEPOINTS = {cp: name for cp, (name, _) in SPACES.items()}
ALTERNATES = []
SAMPLES = [
    "A B A B A B A–B A—B",
    "1999 2026 Paris Tokyo",
    "x = y  (1)",
    "東京 大阪　名古屋",
]


def add_glyphs(font, smooth, grid=None):
    cmap, em = font.getBestCmap(), font["head"].unitsPerEm
    glyphs = {}
    for cp, (name, width) in SPACES.items():
        if cmap.get(cp) != name:  # drawn in place, so review shows the change
            raise ValueError(f"U+{cp:04X} is {cmap.get(cp)}, not {name}")
        glyphs[name] = TTGlyphPen(None).glyph(), pixel.snap_advance(em * width, grid or 1)
    add(font, glyphs, CODEPOINTS)
