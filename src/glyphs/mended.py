"""Redaction's own glyphs that have no outline on a grid, drawn: |.

Redaction 100 Bold has | in its cmap, as wide as Regular's, without an
outline: nothing shows, nor for ￨, made of it (fullwidth.py). There it is
Redaction 100 Regular's, a cell thick, as tall: Bold's ¦ is a cell thick
there too, as its l's stem is, and its | is a hairline, hardly heavier
than Regular's without a grid (56 units for 46), not a stem as those of I
and ! (two cells). Elsewhere it is left as it is.
"""

import pixel
from family import redaction

from .shapes import add, glyph, path, rect

SOURCES = {0x7C: "Regular"}  # code point: the style whose glyph it is, where it has none
CODEPOINTS = {0x7C: "bar"}
ALTERNATES = []
SAMPLES = ["a|b l|I|!", "|¦｜￨ [|] {|}", "x | y || z", "東|京"]


def add_glyphs(font, smooth, grid=None):
    if not grid:
        return
    cmap, glyf, hmtx = font.getBestCmap(), font["glyf"], font["hmtx"]
    for cp, style in SOURCES.items():
        name = cmap[cp]
        if glyf[name].numberOfContours:
            continue
        # a bar: its box, on the grid
        x0, y0, x1, y1 = (pixel.snap(v, grid) for v in path(redaction(grid, style), chr(cp)).bounds)
        add(font, {name: (glyph(rect(x0, y0, x1, y1)), hmtx[name][0])}, {})
