"""Currency and letterlike symbols drawn from Redaction's own: ₩ ₫ ℃ ℉ Å ℡ ℻.

₩ is its W crossed by the bars of its equals sign, and ₫ its đ over a rule
as thick as its minus, a stroke under the baseline: Redaction's own pieces,
so in the numbered variants they keep MCKL's pixels. ℃ and ℉ are its ° and
letter as typed, and Å (the angstrom sign) its Å (components). ℡ and ℻
are its capitals as small caps: shrunk to the x-height, made heavier first
as its Bold is of its Regular (shapes.blend) so their stems match those of
n, hairlines and carving as MCKL's own, as tall as its z, and on a grid
on its rows, where in a cell they fall best (shapes.phased).
"""

import pathops

import pixel

from .shapes import (
    add,
    blend_text,
    composite,
    glyph,
    masters,
    path,
    phased,
    rect,
    runs,
    shaper,
    stem,
    typed,
)

SMALL_CAPS = {0x2121: "TEL", 0x213B: "FAX"}
CODEPOINTS = {cp: f"uni{cp:04X}" for cp in [0x20A9, 0x20AB, 0x2103, 0x2109, 0x212B, *SMALL_CAPS]}
ALTERNATES = []
SAMPLES = ["₩1,000 ₫50,000", "21℃ 70℉", "1 Å = 0.1 nm", "W₩W đ₫d", "℡ 03-1234-5678 ℻"]


def add_glyphs(font, smooth, grid=None):
    g = grid or 1
    hmtx, cmap = font["hmtx"], font.getBestCmap()
    minus = path(font, "−")
    t = minus.bounds[3] - minus.bounds[1]
    equals = path(font, "=")
    bars = runs(equals, x=(equals.bounds[0] + equals.bounds[2]) / 2)

    def crossed(char, rules):
        p = path(font, char)
        for rule in rules:
            p = pathops.op(p, rule, pathops.PathOp.UNION)
        return glyph(p)

    w = path(font, "W")
    won = crossed("W", [rect(w.bounds[0], a, w.bounds[2], b) for a, b in bars])
    d = path(font, "đ")
    dong = crossed("đ", [rect(d.bounds[0], -pixel.snap(2 * t, g), d.bounds[2], -pixel.snap(t, g))])
    s = shaper(font)
    glyphs = {
        "uni20A9": (won, hmtx[cmap[ord("W")]][0]),
        "uni20AB": (dong, hmtx[cmap[ord("đ")]][0]),
        "uni2103": typed(font, s, "°C", grid),
        "uni2109": typed(font, s, "°F", grid),
        "uni212B": (composite(font, [(cmap[ord("Å")], 0, 0)], grid), hmtx[cmap[ord("Å")]][0]),
    }
    add(font, glyphs, CODEPOINTS)

    # Small caps: as tall as z, flat on its rows on a grid, as wide as their
    # ink, between the side bearings of n
    glyf = font["glyf"]
    z, n = glyf[cmap[ord("z")]], glyf[cmap[ord("n")]]
    z.recalcBounds(glyf)
    scale = z.yMax / smooth["OS/2"].sCapHeight
    target = stem(path(smooth, "n"))
    side = smooth["hmtx"][smooth.getBestCmap()[ord("n")]][1]
    small = {
        CODEPOINTS[cp]: glyph(small_caps(smooth, text, scale, target, side))
        for cp, text in SMALL_CAPS.items()
    }
    if grid:
        small = phased(small, grid, (z.yMin, z.yMax), [n])
    add(font, {n: (gl, pixel.snap(gl.xMax + side, g)) for n, gl in small.items()}, CODEPOINTS)


def small_caps(smooth, text, scale, target, x=0):
    """`text` in the capitals of `smooth` shrunk by `scale`, made heavier
    first as Redaction's Bold is of its Regular (shapes.blend_text: past
    Bold for Bold) till the stems of I match `target`: on the baseline,
    its ink from `x`. score.py draws the T and M of ™ with it."""
    regular, bold = masters()
    grow = stem(path(bold, "I")) - stem(path(regular, "I"))
    p = blend_text(smooth, text, (target / scale - stem(path(smooth, "I"))) / grow)
    return p.transform(scale, 0, 0, scale, x - p.bounds[0] * scale, 0)
