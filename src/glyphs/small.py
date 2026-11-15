"""Small form variants drawn from Redaction's own: ﹐ ﹒ ﹖ ﹙ ﹢ ﹫.

Taiwan's standard (CNS 11643) sets smaller punctuation and signs in a full
em. These are Redaction's, as Noto Serif JP's are: seven tenths as big,
around a point a quarter of the cap height up, centred in the em, their
as light as that makes them, which keeps their carving, pixelated on a
grid. A dot that covers less than half a cell there, and so none, is the
cell its middle is in: on 100, in Regular and Italic, ﹒, a cell on the
baseline where ﹐ is, and in Regular the lower dot of ﹕ and the dot of ﹗,
which read as · and a bar without them. Only the marks with a dot (DOTTED):
a bar put back so would be a cell under the other (﹦ on 70 and 100 stays a
bar, its two a row apart at most), a petal of ﹡ a blot. < and > are drawn
as signs.py
draws them. Redaction has no ideographic comma (﹑) nor tortoise shell
brackets (﹝﹞): those stay Noto Serif JP's.
"""

import pathops

import pixel

from . import signs
from .shapes import add, embolden, glyph, path, pixelate_glyphs, rect, shrunk, slope

SCALE = 0.7
# small form code point: the character it is the small form of
SOURCES = {
    0xFE50: ",",
    0xFE52: ".",
    0xFE54: ";",
    0xFE55: ":",
    0xFE56: "?",
    0xFE57: "!",
    0xFE58: "—",
    0xFE59: "(",
    0xFE5A: ")",
    0xFE5B: "{",
    0xFE5C: "}",
    0xFE5F: "#",
    0xFE60: "&",
    0xFE61: "*",
    0xFE62: "+",
    0xFE63: "-",
    0xFE64: "<",
    0xFE65: ">",
    0xFE66: "=",
    0xFE68: "\\",
    0xFE69: "$",
    0xFE6A: "%",
    0xFE6B: "@",
}
CODEPOINTS = {cp: f"uni{cp:04X}" for cp in SOURCES}
ALTERNATES = []
# Those with a dot, which is put back where pixelating leaves none of it
DOTTED = {CODEPOINTS[cp] for cp, char in SOURCES.items() if char in ".;:?!"}
SAMPLES = ["﹐﹒﹔﹕﹖﹗﹘", "﹙﹚﹛﹜﹟﹠﹡", "﹢﹣﹤﹥﹦﹨﹩﹪﹫", "，．？！ ﹐﹒﹖﹗ ,.?!"]


def _source(font, char):
    """`char` of `font` as a path; < and > as signs.py draws them."""
    if char not in "<>":
        return path(font, char)
    glyf, cmap = font["glyf"], font.getBestCmap()
    minus, plus = glyf[cmap[ord("−")]], glyf[cmap[ord("+")]]
    for g in (minus, plus):
        g.recalcBounds(glyf)
    angle = signs._angle(
        minus, plus, slope(font), 1 if char == "<" else -1, minus.yMax - minus.yMin
    )
    p = pathops.Path()
    angle.draw(pathops.PathPen(p), None)
    return p


def _pieces(gl):
    """The bounds of each piece of glyph `gl`: of its contours, but those
    inside another's bounds, counters."""
    boxes, start = [], 0
    for end in getattr(gl, "endPtsOfContours", []):
        xs, ys = zip(*gl.coordinates[start : end + 1])
        boxes.append((min(xs), min(ys), max(xs), max(ys)))
        start = end + 1
    return [
        b
        for b in boxes
        if not any(
            o != b and o[0] <= b[0] and o[1] <= b[1] and o[2] >= b[2] and o[3] >= b[3]
            for o in boxes
        )
    ]


def add_glyphs(font, smooth, grid=None):
    g = grid or 1
    em = pixel.snap_advance(1000, g)
    # As they are, shrunk: lighter than full size ones, as Noto Serif JP's
    # are, and with their carving, which emboldening would fill
    source, bold = shrunk(smooth, SCALE, SCALE)
    around = smooth["OS/2"].sCapHeight / 4
    glyphs = {}
    for cp, char in SOURCES.items():
        p = embolden(_source(source, char), bold)
        x0, _, x1, _ = p.bounds
        p = p.transform(SCALE, 0, 0, SCALE, em / 2 - SCALE * (x0 + x1) / 2, around * (1 - SCALE))
        glyphs[CODEPOINTS[cp]] = glyph(p)
    if grid:
        pieces = {n: _pieces(gl) for n, gl in glyphs.items()}
        glyphs = pixelate_glyphs(glyphs, grid)
        for name, gl in glyphs.items():
            if name not in DOTTED:
                continue
            ink = _pieces(gl)
            p = pathops.Path()
            gl.draw(pathops.PathPen(p), None)
            for x0, y0, x1, y1 in pieces[name]:
                # the cells it reaches, all air: smaller than half a cell
                a, b = x0 // grid * grid, y0 // grid * grid
                c, d = -(-x1 // grid) * grid, -(-y1 // grid) * grid
                if not any(i < c and k > a and j < d and m > b for i, j, k, m in ink):
                    x, y = (x0 + x1) / 2 // grid * grid, (y0 + y1) / 2 // grid * grid
                    p = pathops.op(p, rect(x, y, x + grid, y + grid), pathops.PathOp.UNION)
                    glyphs[name] = glyph(p)
    add(font, {name: (gl, em) for name, gl in glyphs.items()}, CODEPOINTS)
