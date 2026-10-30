"""Maths symbols drawn to match Redaction's own + − = × < >, which are all
it has: line work, in the square of its plus, on the axis of its minus,
with the slant of the plus.

Bars are as thick as the minus (across) and the stem of the plus (up),
other strokes as the strokes of < >: the minus of the style without a grid,
or a cell. Relations stack the < of signs.py, the bars of the equals sign
and a tilde drawn with those strokes, Redaction's being heavier than its
other signs (≤ ≦ ≲ ≃ ≅ ≈), and are crossed by a slash (≠ ≮ ∉).
Sets and logic (∩ ⊂ ∈ ∧ ⊥ ∠) are drawn with the same strokes, round where
they turn, and the dots (∴) are Redaction's period, ⋯ its ellipsis. ∀ ∃ ∆ ∇ stand on the
baseline, as tall as capitals. On a grid, they are pixelated.
"""

import math

import pathops

import pixel

from .shapes import (
    KAPPA,
    _hull,
    add,
    circle,
    embolden,
    glyph,
    path,
    pixelate_glyphs,
    rect,
    runs,
    slope,
    union,
    union_paths,
)

SIDE = 35  # side bearing, as on Redaction's math signs
SLASH = 0.467  # run over rise of Redaction's slash, which crosses (≠)
TILDE = 0.3  # height of a tilde's wave, over the distance between the bars of =
DOTS_APART = 1.6  # least distance between the centres of dots, over their size
RELATIONS = [0x2260, 0x2261, 0x2262, 0x2264, 0x2265, 0x2266, 0x2267, 0x226A, 0x226B]
RELATIONS += [0x226E, 0x226F, 0x2272, 0x2273, 0x2276, 0x2277, 0x22DA, 0x22DB]
TILDES = [0x2243, 0x2245, 0x2248, 0x223D, 0x224C]
SETS = [0x2208, 0x2209, 0x220A, 0x220B, 0x2229, 0x222A, 0x2282, 0x2283, 0x2284, 0x2285]
SETS += [0x2286, 0x2287, 0x228A, 0x228B, 0x2227, 0x2228]
LINES = [0x2213, 0x2215, 0x2223, 0x2225, 0x2226, 0x22A5, 0x221F, 0x2220, 0x22BF, 0x221A]
LINES += [0x221E, 0x221D, 0x2205, 0x29FA, 0x29FB]
CIRCLED = [0x2295, 0x2296, 0x2297, 0x2298, 0x2299, 0x29BF, 0x22A0]
DOTS = [0x2234, 0x2235, 0x2236, 0x2237, 0x22EF]
CAPITALS = [0x2200, 0x2203, 0x2206, 0x2207]
CODEPOINTS = {
    cp: f"uni{cp:04X}" for cp in [*RELATIONS, *TILDES, *SETS, *LINES, *CIRCLED, *DOTS, *CAPITALS]
}
ALTERNATES = []
SAMPLES = [
    "a≤b≥c a≠b≡c a≈b≃c≅d",
    "≤≥≦≧≪≫≠≡≢≮≯≲≳≶≷⋚⋛",
    "≃≅≈∽≌ ∓±+−=×<>",
    "∈∉∊∋∩∪⊂⊃⊄⊅⊆⊇⊊⊋∧∨",
    "∣∥∦∕⊥∟∠⊿√∞∝∅⧺⧻",
    "⊕⊖⊗⊘⊙⦿⊠ ∴∵∶∷⋯",
    "∀x∃y ∆x∇f ∅",
    "x∈A∪B ∀ε∃δ p∧q⊢r",
]


class _Pen:
    """Strokes in the square of the plus, centred on its centre and the axis
    of the minus: x right, y up, slanted when drawn."""

    def __init__(self, font, smooth, grid):
        cmap = font.getBestCmap()
        plus = path(font, "+")
        minus = font["glyf"][cmap[0x2212]]
        minus.recalcBounds(font["glyf"])
        self.font, self.grid, self.slant = font, grid, slope(smooth)
        self.axis = (minus.yMin + minus.yMax) / 2
        self.th = minus.yMax - minus.yMin  # across
        x0, y0, x1, y1 = plus.bounds
        stem = runs(plus, y=y1 - self.th / 2)
        self.tv = stem[0][1] - stem[0][0]  # up, along the slant
        self.cx = (x0 + x1) / 2 + (self.axis - (y0 + y1) / 2) * self.slant
        self.w, self.h = (x1 - x0) / 2, (y1 - y0) / 2
        thin = path(smooth, "−").bounds
        self.t = max(thin[3] - thin[1], grid or 0)  # other strokes
        equals = path(font, "=")
        bars = runs(equals, x=(equals.bounds[0] + equals.bounds[2]) / 2)
        self.eq = (bars[-1][0] + bars[-1][1] - bars[0][0] - bars[0][1]) / 2  # between bars
        self.gap = bars[-1][0] - bars[0][1]  # inside the equals sign
        self.cap = smooth["OS/2"].sCapHeight - self.axis

    def hbar(self, x0, x1, y):
        return rect(x0, y - self.th / 2, x1, y + self.th / 2)

    def vbar(self, x, y0, y1):
        return rect(x - self.tv / 2, y0, x + self.tv / 2, y1)

    def chevron(self, sign, y0, y1, x0=None, x1=None):
        """< (sign 1) or > (-1) between y0 and y1, as signs.py draws it: its
        strokes as thick across as those of < as wide as the plus, however
        steep (≪)."""
        x0 = -self.w if x0 is None else x0
        x1 = self.w if x1 is None else x1
        if sign < 0:
            x0, x1 = -x1, -x0
        tip, ends = (x0, x1) if sign > 0 else (x1, x0)
        # Thick up as the stroke of < across, over the cosine of its slope
        across = self.t / math.hypot(1, (2 * self.h - self.t) / 2 / (2 * self.w))
        t = across * math.hypot(1, (y1 - y0 - self.t) / 2 / abs(x1 - x0))
        yc, rise = (y0 + y1) / 2, (y1 - y0 - t) / 2
        return union(
            [
                (tip, yc - t / 2),
                (ends, yc + d * rise - t / 2),
                (ends, yc + d * rise + t / 2),
                (tip, yc + t / 2),
            ]
            for d in (1, -1)
        )

    def slash(self, rise, run=SLASH, y=0):
        """A stroke from bottom left to top right, `rise` above and below `y`,
        cut level."""
        half = self.t * math.hypot(1, run) / 2
        x = rise * run
        return union(
            [
                [
                    (-x - half, y - rise),
                    (-x + half, y - rise),
                    (x + half, y + rise),
                    (x - half, y + rise),
                ]
            ]
        )

    def line(self, points, closed=False, join=pathops.LineJoin.MITER_JOIN):
        """A stroke along `points`."""
        p = pathops.Path()
        p.moveTo(*points[0])
        for pt in points[1:]:
            p.lineTo(*pt)
        if closed:
            p.close()
        return self.stroke(p, join)

    def stroke(self, p, join=pathops.LineJoin.ROUND_JOIN):
        p = pathops.Path(p)
        p.stroke(self.t, pathops.LineCap.BUTT_CAP, join, 4)
        p.convertConicsToQuads()
        return union_paths([p])

    def ring(self, r):
        """A circle stroke, its outside `r` from the centre."""
        return pathops.op(circle(0, 0, r), circle(0, 0, r - self.t), pathops.PathOp.DIFFERENCE)

    def cup(self, w, y0, y1, down=True):
        """∪ (or ∩, not `down`) `w` wide either side, from y0 to y1."""
        r = w - self.t / 2
        k = r * KAPPA
        top, turn = (y1, y0 + self.t / 2 + r) if down else (y0, y1 - self.t / 2 - r)
        s = -1 if down else 1
        p = pathops.Path()
        p.moveTo(-r, top)
        p.lineTo(-r, turn)
        p.cubicTo(-r, turn + s * k, -k, turn + s * r, 0, turn + s * r)
        p.cubicTo(k, turn + s * r, r, turn + s * k, r, turn)
        p.lineTo(r, top)
        return self.stroke(p)

    def subset(self, y0, y1, x0=None, x1=None, sign=1):
        """⊂ (sign 1, open to the right) or ⊃ (-1), from y0 to y1."""
        x0 = -self.w if x0 is None else x0
        x1 = self.w if x1 is None else x1
        r = (y1 - y0 - self.t) / 2
        k, yc = r * KAPPA, (y0 + y1) / 2
        turn = x0 + self.t / 2 + r
        p = pathops.Path()
        p.moveTo(x1, yc + r)
        p.lineTo(turn, yc + r)
        p.cubicTo(turn - k, yc + r, turn - r, yc + k, turn - r, yc)
        p.cubicTo(turn - r, yc - k, turn - k, yc - r, turn, yc - r)
        p.lineTo(x1, yc - r)
        p = self.stroke(p)
        return p if sign > 0 else p.transform(-1, 0, 0, 1, x0 + x1, 0)

    def glyph_of(self, char, dx, dy, mirror=False):
        """Redaction's `char` in the square, its box centred on (dx, dy),
        mirrored or not: on the grid once slanted."""
        p = path(self.font, char).transform(
            1, 0, -self.slant, 1, -self.cx + self.axis * self.slant, -self.axis
        )
        x0, y0, x1, y1 = p.bounds
        if mirror:
            p = p.transform(-1, 0, 0, 1, x0 + x1, 0)
        oy = pixel.snap(dy - (y0 + y1) / 2, self.grid or 1)
        ox = pixel.snap(dx - (x0 + x1) / 2 + oy * self.slant, self.grid or 1) - oy * self.slant
        return p.transform(1, 0, 0, 1, ox, oy)

    def tilde(self, y, mirror=False, w=None):
        """A wave, one sine across the square on `y`, as high as TILDE of the
        distance between the bars of the equals sign (mirrored: ∽)."""
        w = self.w if w is None else w
        amp = self.eq * TILDE
        points = [(-w + 2 * w * i / 48, y + amp * math.sin(math.pi * i / 24)) for i in range(49)]
        if mirror:
            points = [(-x, y) for x, y in points]
        return self.line(points, join=pathops.LineJoin.ROUND_JOIN)

    def drawn(self, parts):
        """`parts`, in the square, slanted, in place on the axis."""
        p = union_paths(parts)
        return p.transform(1, 0, self.slant, 1, self.cx, self.axis)


def _relations(pen):
    w, h, th, eq, gap = pen.w, pen.h, pen.th, pen.eq, pen.gap
    bars = (-eq / 2, eq / 2)
    three = (-eq, 0, eq)
    glyphs = {
        0x2260: [*(pen.hbar(-w, w, y) for y in bars), pen.slash(h)],
        0x2261: [pen.hbar(-w, w, y) for y in three],
        0x2262: [*(pen.hbar(-w, w, y) for y in three), pen.slash(h + th)],
        0x226E: [pen.chevron(1, -h, h), pen.slash(h)],
        0x226F: [pen.chevron(-1, -h, h), pen.slash(h)],
    }
    # Over a bar, or two: a < as high as the plus, the bar under it
    low = -h - eq / 2
    for cp, sign in ((0x2264, 1), (0x2265, -1)):
        glyphs[cp] = [pen.chevron(sign, low + th + gap, h + eq / 2), pen.hbar(-w, w, low + th / 2)]
    low = -h - eq
    for cp, sign in ((0x2266, 1), (0x2267, -1)):
        top = h + eq / 2
        glyphs[cp] = [
            pen.chevron(sign, low + eq + th + gap, top),
            *(pen.hbar(-w, w, low + th / 2 + d) for d in (0, eq)),
        ]
    # Two <, each shorter, the second where the first ends
    step = w * 0.75
    for cp, sign in ((0x226A, 1), (0x226B, -1)):
        glyphs[cp] = [
            pen.chevron(sign, -h, h, -w, w - step),
            pen.chevron(sign, -h, h, -w + step, w),
        ]
    # Over the tilde
    for cp, sign in ((0x2272, 1), (0x2273, -1)):
        tall = 2 * eq * TILDE + pen.t
        bottom = -h - eq / 2
        tilde = pen.tilde(bottom + tall / 2)
        glyphs[cp] = [pen.chevron(sign, bottom + tall + gap, h + eq / 2), tilde]
    # < over >, and < over = over >
    for cp, sign in ((0x2276, 1), (0x2277, -1)):
        top, low = h + eq / 2, -h - eq / 2
        mid = gap / 2
        glyphs[cp] = [pen.chevron(sign, mid, top), pen.chevron(-sign, low, -mid)]
    for cp, sign in ((0x22DA, 1), (0x22DB, -1)):
        top, low = h + eq, -h - eq
        inner = eq / 2 + th / 2 + gap
        glyphs[cp] = [
            pen.chevron(sign, inner, top),
            *(pen.hbar(-w, w, y) for y in bars),
            pen.chevron(-sign, low, -inner),
        ]
    return glyphs


def _tildes(pen):
    w, th, gap = pen.w, pen.th, pen.gap
    tall = 2 * pen.eq * TILDE + pen.t

    def stacked(items):
        """Bars (None) and tildes (False, or True mirrored), the gap of the
        equals sign between them, centred on the axis."""
        heights = [th if item is None else tall for item in items]
        total = sum(heights) + gap * (len(items) - 1)
        y, parts = total / 2, []
        for item, height in zip(items, heights):
            mid = y - height / 2
            parts.append(pen.hbar(-w, w, mid) if item is None else pen.tilde(mid, item))
            y -= height + gap
        return parts

    return {
        0x2243: stacked([False, None]),
        0x2245: stacked([False, None, None]),
        0x2248: [pen.tilde(d * (tall + gap) / 2) for d in (1, -1)],
        0x223D: [pen.tilde(0, True)],
        0x224C: stacked([True, None, None]),
    }


def _sets(pen):
    w, h, th, t, eq, gap = pen.w, pen.h, pen.th, pen.t, pen.eq, pen.gap
    glyphs = {
        0x2229: [pen.cup(w, -h, h, down=False)],
        0x222A: [pen.cup(w, -h, h)],
        0x2282: [pen.subset(-h, h)],
        0x2283: [pen.subset(-h, h, sign=-1)],
        0x2284: [pen.subset(-h, h), pen.slash(h + eq / 2)],
        0x2285: [pen.subset(-h, h, sign=-1), pen.slash(h + eq / 2)],
        0x2227: [_turned(pen.chevron(1, -w, w, -h, h), 1)],
        0x2228: [_turned(pen.chevron(1, -w, w, -h, h), -1)],
    }
    low = -h - eq / 2
    for cp, sign in ((0x2286, 1), (0x2287, -1)):
        glyphs[cp] = [
            pen.subset(low + th + gap, h + eq / 2, sign=sign),
            pen.hbar(-w, w, low + th / 2),
        ]
    for cp in (0x228A, 0x228B):  # crossed
        glyphs[cp] = [*glyphs[cp - 4], pen.slash(th / 2 + gap * 0.6, y=low + th / 2)]
    # Elements: a subset with its middle bar, and the small one
    for cp, sign, scale in ((0x2208, 1, 1), (0x220B, -1, 1), (0x220A, 1, 0.72)):
        sw, sh = w * scale, h * scale
        x0 = -sw + t / 2 if sign > 0 else -sw
        x1 = sw if sign > 0 else sw - t / 2
        glyphs[cp] = [pen.subset(-sh, sh, -sw, sw, sign), pen.hbar(x0, x1, 0)]
    glyphs[0x2209] = [*glyphs[0x2208], pen.slash(h + eq / 2)]
    return glyphs


def _outline(pen, points):
    """The polygon of `points` drawn with the strokes, inside it."""
    p = union([points])
    return pathops.op(p, embolden(p, -pen.t), pathops.PathOp.DIFFERENCE)


def _crossed(pen, rise):
    """× of slashes at 45°, `rise` above and below the axis."""
    return [pen.slash(rise, 1), pen.slash(rise, 1).transform(-1, 0, 0, 1, 0, 0)]


def _turned(p, sign):
    """`p` turned a quarter: up (∧, sign 1) or down (∨, -1)."""
    return p.transform(0, -sign, sign, 0, 0, 0)


def _lines(pen):
    w, h, th, tv, t, eq = pen.w, pen.h, pen.th, pen.tv, pen.t, pen.eq
    tall = h + eq / 2
    plus = pen.glyph_of("+", 0, 0)
    ph = plus.bounds[3] - plus.bounds[1]
    glyphs = {
        # ∓: ± turned over, the minus over the plus
        0x2213: [pen.glyph_of("−", 0, (ph + th) / 2), pen.glyph_of("+", 0, -th)],
        0x2215: [pen.slash(tall)],
        0x2223: [pen.vbar(0, -tall, tall)],
        0x2225: [pen.vbar(x, -tall, tall) for x in (-eq / 2, eq / 2)],
        0x2226: [*(pen.vbar(x, -tall, tall) for x in (-eq / 2, eq / 2)), pen.slash(h * 0.75, 1.2)],
        0x22A5: [pen.hbar(-w, w, -h + th / 2), pen.vbar(0, -h, h)],
        0x221F: [pen.hbar(-w, w, -h + th / 2), pen.vbar(-w + tv / 2, -h, h)],
        0x29FA: [
            pen.hbar(-w * 1.25, w * 1.25, 0),
            *(pen.vbar(x, -h, h) for x in (-eq / 2, eq / 2)),
        ],
        0x29FB: [pen.hbar(-w * 1.5, w * 1.5, 0), *(pen.vbar(x, -h, h) for x in (-eq, 0, eq))],
    }
    # ∠ rises from the left end of the bar, ⊿ is a triangle on it
    run = (2 * w - t) / (2 * h)
    # its bar cut along the outer edge of the stroke rising from it
    rise = pen.slash(h, run)
    edge = [pt for pt in _hull(list(rise.points)) if pt[0] < 0]
    (bx, by), (tx, ty) = min(edge, key=lambda pt: pt[1]), max(edge, key=lambda pt: pt[1])
    far = 4 * w
    right = union(
        [[(bx, by - far * (ty - by)), (tx, ty + far * (ty - by)), (far, ty + far), (far, by - far)]]
    )
    bar = pathops.op(pen.hbar(-w * 2, w, -h + th / 2), right, pathops.PathOp.INTERSECTION)
    glyphs[0x2220] = [bar, rise]
    glyphs[0x22BF] = [_outline(pen, [(-w, -h), (w, -h), (w, h)])]
    # √: a tick down to the foot, the long stroke up, and a bar to the right
    top, foot = pen.cap, -tall
    root = pen.line([(-w, 0), (-w * 0.55, foot + t * 0.6), (w * 0.15, top - th / 2)])
    glyphs[0x221A] = [root, pen.hbar(w * 0.15 - t / 2, w * 1.05, top - th / 2)]
    # ∞ and ∝: lemniscates, stretched up
    a, stretch = w * 1.2, 1.45

    def lemniscate(t0, t1, n=96):
        points = []
        for i in range(n + 1):
            u = t0 + (t1 - t0) * i / n
            d = 1 + math.sin(u) ** 2
            points.append((a * math.cos(u) / d, stretch * a * math.sin(u) * math.cos(u) / d))
        return points

    glyphs[0x221E] = [
        pen.line(lemniscate(0, 2 * math.pi)[:-1], closed=True, join=pathops.LineJoin.ROUND_JOIN)
    ]
    arm = 0.27 * math.pi
    loop = lemniscate(arm, 2 * math.pi - arm)
    shift = (max(x for x, _ in loop) + min(x for x, _ in loop)) / 2
    glyphs[0x221D] = [pen.line([(x - shift, y) for x, y in loop], join=pathops.LineJoin.ROUND_JOIN)]
    # ∅: a ring, crossed beyond it
    glyphs[0x2205] = [pen.ring(h + eq / 4), pen.slash(h + eq / 2, 0.75)]
    return glyphs


def _circled(pen):
    h, th, tv, t, eq = pen.h, pen.th, pen.tv, pen.t, pen.eq
    r = h + eq / 4
    inner = circle(0, 0, r - t / 2)

    def inside(*parts):
        return pathops.op(union_paths(parts), inner, pathops.PathOp.INTERSECTION)

    cross = _crossed(pen, r)
    period = path(pen.font, ".")
    dot = (period.bounds[2] - period.bounds[0]) / 2
    square = rect(-h, -h, h, h)
    frame = pathops.op(square, rect(-h + tv, -h + th, h - tv, h - th), pathops.PathOp.DIFFERENCE)
    return {
        0x2295: [pen.ring(r), inside(pen.hbar(-r, r, 0), pen.vbar(0, -r, r))],
        0x2296: [pen.ring(r), inside(pen.hbar(-r, r, 0))],
        0x2297: [pen.ring(r), inside(*cross)],
        0x2298: [pen.ring(r), inside(cross[0])],
        0x2299: [pen.ring(r), circle(0, 0, dot)],
        0x29BF: [pen.ring(r), circle(0, 0, r * 0.5)],
        0x22A0: [
            frame,
            pathops.op(union_paths(_crossed(pen, h)), square, pathops.PathOp.INTERSECTION),
        ],
    }


def _dots(pen):
    h = pen.h
    period = path(pen.font, ".")
    size = period.bounds[3] - period.bounds[1]
    up = h - size / 2  # at the top and bottom of the plus, as in ÷
    side = max(up * 0.6, size * DOTS_APART / 2)

    def dots(*places):
        return [pen.glyph_of(".", x, y) for x, y in places]

    return {
        0x2234: dots((-side, -up), (side, -up), (0, up)),
        0x2235: dots((-side, up), (side, up), (0, -up)),
        0x2236: dots((0, up), (0, -up)),
        0x2237: dots((-side, up), (side, up), (-side, -up), (side, -up)),
        0x22EF: [pen.glyph_of("…", 0, 0)],  # Redaction's ellipsis, on the axis
    }


def _capitals(pen):
    """∀ ∃ ∆ ∇, from the baseline to the height of capitals."""
    th, tv = pen.th, pen.tv
    low, top = -pen.axis, pen.cap
    half = (top - low) / 2
    w = half * 0.78
    mid = (top + low) / 2
    # ∀: a V, its bar at two thirds
    v = _turned(pen.chevron(1, -w, w, -half, half), -1).transform(1, 0, 0, 1, 0, mid)
    y = low + (top - low) * 0.62
    # its bar ends along the outer edges of the V
    outer = union([_hull(list(v.points))])
    forall = [v, pathops.op(pen.hbar(-w, w, y), outer, pathops.PathOp.INTERSECTION)]
    # ∃: an E turned, its middle bar shorter
    e = w * 0.8
    exists = [
        pen.hbar(-e, e, top - th / 2),
        pen.hbar(-e * 0.6, e, mid),
        pen.hbar(-e, e, low + th / 2),
        pen.vbar(e - tv / 2, low, top),
    ]
    return {
        0x2200: forall,
        0x2203: exists,
        0x2206: [_outline(pen, [(-w, low), (w, low), (0, top)])],
        0x2207: [_outline(pen, [(-w, top), (w, top), (0, low)])],
    }


def add_glyphs(font, smooth, grid=None):
    """Add the maths symbols to `font`: a Redaction style, or one of
    Redaction 10 to 100 on `grid`, its own plus, minus, equals sign, tilde
    and period, with the strokes and slant of `smooth`, the same style
    without a grid."""
    pen = _Pen(font, smooth, grid)
    shapes = {}
    for group in (_relations, _tildes, _sets, _lines, _circled, _dots, _capitals):
        shapes |= group(pen)
    # As wide as the plus, or as their ink upright and the side bearings of
    # the plus: slanted, they lean out of it, as the plus does
    advance = font["hmtx"][font.getBestCmap()[ord("+")]][0]
    side = max(grid, pixel.snap(SIDE, grid)) if grid else SIDE
    glyphs, widths = {}, {}
    for cp, parts in shapes.items():
        x0, _, x1, _ = union_paths(parts).bounds
        width = max(advance, pixel.snap(x1 - x0 + 2 * side, grid or 1))
        shift = pixel.snap((width - advance) / 2, grid or 1)
        glyphs[CODEPOINTS[cp]] = glyph(pen.drawn(parts).transform(1, 0, 0, 1, shift, 0))
        widths[CODEPOINTS[cp]] = width
    if grid:
        glyphs = pixelate_glyphs(glyphs, grid)
    add(font, {name: (g, widths[name]) for name, g in glyphs.items()}, CODEPOINTS)
