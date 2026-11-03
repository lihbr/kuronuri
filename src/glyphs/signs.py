"""Math signs drawn from Redaction's own, which lacks them.

< and > span the plus, with the axis of the minus and the slant of the
plus. Their strokes are as thick as the minus before pixelation, or a cell:
Redaction 35's minus is two cells thick, which makes diagonal strokes heavy.
± is the plus over the minus and ÷ the minus between two periods, made of
Redaction's glyphs (components), as far apart as the plus is tall (or a
stroke apart, if further), so in the numbered variants they keep MCKL's
pixels. ‰ is the percent sign (a component) and its bottom ring again, as
far right of it as half the ring is thick, about as close as the ring is to
the slash: on a grid, the pixels of the percent sign where its smooth ring
is, MCKL's own, a cell apart at least.
"""

import math

import pixel

from .shapes import (
    add,
    composite,
    embolden,
    glyph,
    path,
    pixelate_glyphs,
    rect,
    slope,
    union,
    union_paths,
)

CODEPOINTS = {
    0x3C: "less",
    0x3E: "greater",
    0xB1: "plusminus",
    0xF7: "divide",
    0x2030: "perthousand",
}
ALTERNATES = []
RING = "perthousand.ring"  # the ring ‰ adds to the percent sign
APART = 0.5  # of the thickness of that ring, between it and the ring of the percent sign
SAMPLES = ["a<b>c 1<2", "+−±÷×=<>", "±1 ÷2 x±y", "H<H>H", "東京<大阪", "50% 5‰ %‰"]


def _angle(minus, plus, slant, sign, t):
    """< (sign 1) or > (sign -1): two strokes `t` thick, seen vertically,
    from a tip on the axis of the minus to the corners of the plus."""
    axis = (minus.yMax + minus.yMin) / 2
    half = (plus.yMax - plus.yMin - t) / 2  # rise of a stroke's centre line
    x0, x1 = (minus.xMin, minus.xMax) if sign > 0 else (minus.xMax, minus.xMin)

    def shear(x, y):
        return x + y * slant, y + axis

    arms = [
        [(x0, -t / 2), (x1, d * half - t / 2), (x1, d * half + t / 2), (x0, t / 2)] for d in (1, -1)
    ]
    return glyph(union([shear(*pt) for pt in arm] for arm in arms))


def add_glyphs(font, smooth, grid=None):
    glyf, hmtx, cmap = font["glyf"], font["hmtx"], font.getBestCmap()
    names = {c: cmap[ord(c)] for c in "+−."}
    plus, minus, period = (glyf[names[c]] for c in "+−.")
    for g in (plus, minus, period):
        g.recalcBounds(glyf)
    slant = slope(smooth)
    t = minus.yMax - minus.yMin
    axis = (minus.yMax + minus.yMin) / 2

    thin = smooth["glyf"][smooth.getBestCmap()[ord("−")]]
    thin.recalcBounds(smooth["glyf"])
    stroke = max(thin.yMax - thin.yMin, grid or 0)
    angles = {
        CODEPOINTS[0x3C]: _angle(minus, plus, slant, 1, stroke),
        CODEPOINTS[0x3E]: _angle(minus, plus, slant, -1, stroke),
    }
    if grid:
        angles = pixelate_glyphs(angles, grid)

    # ±: the plus, then a gap and the minus as thick as its stroke, centred
    # on the axis together.
    lift = t  # half the gap and the minus, below the plus
    drop = (plus.yMax - plus.yMin + t) / 2  # half the plus and the gap
    # ÷: periods at the top and bottom of the plus, at least a stroke away
    # from the minus, centred over it along the slant.
    centre = (minus.xMin + minus.xMax) / 2, axis
    dot = (period.xMin + period.xMax) / 2, (period.yMin + period.yMax) / 2

    def over_minus(dy):
        return centre[0] - dot[0] + (dot[1] + dy - axis) * slant

    composites = {
        CODEPOINTS[0xB1]: [
            (names["+"], lift * slant, lift),
            (names["−"], -drop * slant, -drop),
        ],
        CODEPOINTS[0xF7]: [
            (names["−"], 0, 0),
            *[
                (names["."], over_minus(dy), dy)
                for dy in (
                    max(plus.yMax - period.yMax, minus.yMax + t - period.yMin),
                    min(plus.yMin - period.yMin, minus.yMin - t - period.yMax),
                )
            ],
        ],
    }

    adv = hmtx[names["+"]][0]
    glyphs = {name: (g, adv) for name, g in angles.items()}
    glyphs |= {name: (composite(font, parts, grid), adv) for name, parts in composites.items()}
    add(font, glyphs, CODEPOINTS)

    # ‰: the bottom ring of the smooth percent sign, the lower of its two
    # contours with a hole, and the hole
    contours = list(path(smooth, "%").contours)

    def inside(c, outer):
        x0, y0, x1, y1 = outer.bounds
        return c is not outer and x0 <= c.bounds[0] and c.bounds[2] <= x1 and y0 <= c.bounds[1]

    rings = [c for c in contours if any(inside(d, c) for d in contours)]
    outer = min(rings, key=lambda c: c.bounds[1] + c.bounds[3])
    x0, y0, x1, y1 = outer.bounds
    ring = [outer, *(c for c in contours if inside(c, outer))]
    thick = x1 - max(c.bounds[2] for c in ring if c is not outer)
    shift = pixel.snap(x1 - x0 + thick * APART, grid or 1)
    p = union([])
    for c in ring:
        p.addPath(c)
    if grid:
        # Its own pixels: the cells of the pixel percent sign nearer the smooth
        # ring than its slash (grown a step at a time until one of them takes
        # them in). MCKL's ring, which at 70 and 100 is not what the smooth
        # ring would pixelate into
        slash = union([])
        for c in contours:
            if c is not outer and not inside(c, outer) and c not in rings:
                slash.addPath(c)
        steps = [grid * k / 4 for k in range(9)]
        grown = [(embolden(p, a), embolden(slash, a)) for a in steps]

        def ring_s(x, y):
            for near_ring, near_slash in grown:
                if near_ring.contains((x, y)) or near_slash.contains((x, y)):
                    return near_ring.contains((x, y))
            return False

        percent = path(font, "%")
        cells = [
            rect(x, y, x + grid, y + grid)
            for x in range(
                math.floor(x0 / grid) * grid - grid, math.ceil(x1 / grid) * grid + grid, grid
            )
            for y in range(
                math.floor(y0 / grid) * grid - grid, math.ceil(y1 / grid) * grid + grid, grid
            )
            if percent.contains((x + grid / 2, y + grid / 2)) and ring_s(x + grid / 2, y + grid / 2)
        ]
        p = union_paths(cells)
        shift = max(shift, round(p.bounds[2] - p.bounds[0]) + grid)
    ring_glyph = glyph(p.transform(1, 0, 0, 1, shift, 0))
    percent = cmap[ord("%")]
    add(font, {RING: (ring_glyph, 0)}, {})
    per_mille = composite(font, [(percent, 0, 0), (RING, 0, 0)], grid)
    add(font, {CODEPOINTS[0x2030]: (per_mille, hmtx[percent][0] + shift)}, CODEPOINTS)
