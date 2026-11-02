"""Arrows with the owner's head on Redaction's minus, and the features for
them.

The owner drew the head of → (a solid barbed dart), saved as drawn in
Regular's drawn UFO (shapes.drawn: arrowright, y flipped, scaled by 1.424,
rounded), on the axis of Redaction's minus. Shafts are its minus, as thick
all along, on its axis, into the head's back. Every arrow is made of them:
- → is the head on a shaft; ← ↑ ↓ ↖ ↗ ↘ ↙ are it turned and mirrored.
- ↔ ↕ have the head at both ends.
- Double arrows (⇒) have two shafts, as far apart as the bars of its
  equals sign, into the head, scaled to span them.
- Block arrows (⇦ ⇧ ⇨ ⇩) are ⇒ closed, its tail a bar as thick as the
  minus; ⬅ ⬆ ⬇ ⮕ its outline, filled.
- Pairs (⇄ ⇅ ↹ ↸, harpoons ⇌ with half the head) have heads PAIR as big, as
  big as two fit in the em; curved arrows (⤴, the shaft along a curve) and
  halfwidth arrows (￫) smaller ones.
- The alt arrows (`ss01`) are all of them again with smaller heads (SIZES).
Bold has its own minus, its head heavier by Redaction's Bold n's stem over
Regular's (the dart's arms), tips and barbs as pointed. Italic is Regular
slanted as Redaction's plus.

On a grid, strokes are as many cells either side of their axis, heads at
least 3 cells long, their barbs on the edge of a cell and blunt enough to
keep their reach (blunter where pixels come apart); every direction is its
arrow's pixels mirrored or turned (← is →), italic's are upright ones
slanted by rows of cells, bridged where that pulls them apart, and
pinholes and notches pixelating leaves are filled (_pixels).

`calt` turns -> <- <-> -^ ^- => <=> =^ into arrows, but leaves the ^-^ ^=^
=^.^= emoticons alone. `ss01` swaps in the alt arrows.
"""

import functools
import math

import numpy as np
import pathops
from fontTools.otlLib import builder as otl
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib.tables import otTables as ot

import layout
import pixel
from family import redaction

from .shapes import (
    add,
    cells,
    drawn,
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
SS01_NAME = "Alt arrows"
LENGTH = 630  # from tail to tip: twice the minus axis, upright arrows stand on the baseline
HALF = 440  # length of halfwidth arrows
ALT = 0.55  # of the head, the alt heads (ss01)
PAIR = 0.75  # of the head, those of pairs (⇄ ⇅ ↹ ↸ ⇌), as big as two fit in the em
CURL = 0.75  # of the head, that of curved arrows
# of the head, by kind, of the arrows and of the alt arrows
SIZES = {
    "": dict(main=1, pair=PAIR, curl=CURL, half=ALT),
    ".ss01": dict(main=ALT, pair=ALT, curl=ALT, half=0.4),
}
# On a grid: barbs lose at most this much of how far out they are at their
# needle point (half a cell along it), and are made BLUNT degrees blunter at
# a time where an arrow's pixels come apart where its drawing does not
REACH = 0.25
BLUNT = 5
# code point: (glyph name, direction in degrees, double headed)
SINGLE = {
    0x2190: ("arrowleft", 180, False),
    0x2191: ("arrowup", 90, False),
    0x2192: ("arrowright", 0, False),
    0x2193: ("arrowdown", -90, False),
    0x2194: ("arrowboth", 0, True),
    0x2195: ("arrowupdn", 90, True),
    0x2196: ("arrowupleft", 135, False),
    0x2197: ("arrowupright", 45, False),
    0x2198: ("arrowdownright", -45, False),
    0x2199: ("arrowdownleft", -135, False),
}
DOUBLES = {
    0x21D0: ("arrowdblleft", 180, False),
    0x21D1: ("arrowdblup", 90, False),
    0x21D2: ("arrowdblright", 0, False),
    0x21D3: ("arrowdbldown", -90, False),
    0x21D4: ("arrowdblboth", 0, True),
    0x21D5: ("arrowdblupdn", 90, True),
    0x21D6: ("arrowdblupleft", 135, False),
    0x21D7: ("arrowdblupright", 45, False),
    0x21D8: ("arrowdbldownright", -45, False),
    0x21D9: ("arrowdbldownleft", -135, False),
}
ARROWS = SINGLE | DOUBLES
# Arrows made of arrows (⇄), harpoons (⇌), block arrows (⇨ ⮕), curved
# arrows (⤴) and halfwidth arrows (￫): in pairs, they stand in the em.
# Block arrows by their direction, and whether filled
COMPOUND = [0x21B8, 0x21B9, 0x21C4, 0x21C5, 0x21C6, 0x21CB, 0x21CC, 0x21F5]
BLOCK = {0x21E6: (180, False), 0x21E7: (90, False), 0x21E8: (0, False), 0x21E9: (-90, False)}
BLOCK |= {0x2B05: (180, True), 0x2B06: (90, True), 0x2B07: (-90, True), 0x2B95: (0, True)}
CURVED = {0x2934: 1, 0x2935: -1}  # rightwards, then up or down
HALFWIDTH = {0xFFE9: 180, 0xFFEA: 90, 0xFFEB: 0, 0xFFEC: -90}
CODEPOINTS = {cp: name for cp, (name, _, _) in ARROWS.items()} | {
    cp: f"uni{cp:04X}" for cp in [*COMPOUND, *BLOCK, *CURVED, *HALFWIDTH]
}
ALTERNATES = [name + ".ss01" for name in CODEPOINTS.values()]
SOURCES = "→"  # the owner's head, in Regular's drawn UFO
SAMPLES = [
    "H←↑→↓↔↕↖↗↘↙H",
    "H⇐⇑⇒⇓⇔⇕⇖⇗⇘⇙H",
    "a → b ⇒ c ↔ d ⇔ e",
    "東京→大阪⇒京都",
    "−+→ =⇒",
    "⇄⇆⇅⇵ ↹↸ ⇋⇌ ⤴⤵",
    "⇦⇧⇨⇩ ⬅⬆⬇⮕ ￩￪￫￬",
]
# On a grid, arrows that are others turned or mirrored are their pixels so:
# {name: (name of the other, steps)}, a step "x" or "y" mirroring across
# that axis, or a quarter turn anticlockwise (90, -90, 180)
_TURNED = {
    prefix + way: (prefix + of, steps)
    for prefix in ("arrow", "arrowdbl")
    for way, of, steps in [
        ("left", "right", ["x"]),
        ("up", "right", [90]),
        ("down", "right", [-90]),
        ("updn", "both", [90]),
        ("upleft", "upright", ["x"]),
        ("downright", "upright", ["y"]),
        ("downleft", "upright", [180]),
    ]
} | {
    "uni21C6": ("uni21C4", ["x"]),  # ⇆ ⇄
    "uni21C5": ("uni21C4", [90]),  # ⇅
    "uni21F5": ("uni21C4", ["x", 90]),  # ⇵
    "uni21CB": ("uni21CC", ["x"]),  # ⇋ ⇌
    "uni21E6": ("uni21E8", ["x"]),  # ⇦ ⇨
    "uni21E7": ("uni21E8", [90]),  # ⇧
    "uni21E9": ("uni21E8", [-90]),  # ⇩
    "uni2B05": ("uni2B95", ["x"]),  # ⬅ ⮕
    "uni2B06": ("uni2B95", [90]),  # ⬆
    "uni2B07": ("uni2B95", [-90]),  # ⬇
    "uni2935": ("uni2934", ["y"]),  # ⤵ ⤴
    "uniFFE9": ("uniFFEB", ["x"]),  # ￩ ￫
    "uniFFEA": ("uniFFEB", [90]),
    "uniFFEC": ("uniFFEB", [-90]),
}
TURNED = {n + s: (of + s, steps) for n, (of, steps) in _TURNED.items() for s in SIZES}
# On a grid, arrows drawn as many cells either side of their axis, which
# pixelating does not always keep (pixel.py puts thin strokes back one side)
SYMMETRIC = {"arrowright", "arrowboth", "arrowdblright", "arrowdblboth", "uniFFEB"}
SYMMETRIC |= {"uni21E8", "uni2B95"}
# Arrows on the axis of the equals sign: double and block arrows
EQUALS = {n for n, _, _ in DOUBLES.values()} | {f"uni{cp:04X}" for cp in BLOCK}
HOLLOW = {f"uni{cp:04X}" for cp, (_, filled) in BLOCK.items() if not filled}
# Pairs standing side by side (⇅ ⇵): slanted by rows of cells, they come
# together, so Italic's are drawn a cell further apart, not turned from ⇄
STANDING = {n + s for n in ("uni21C5", "uni21F5") for s in SIZES}


def _points(p):
    """[[(x, y)]] of the contours of `p`, a path of lines."""
    return [[pts[0] for _, pts in c.segments if pts] for c in p.contours]


@functools.cache
def source():
    """The owner's head, from Regular's drawn UFO: →'s, its tip at the
    origin, on its axis, between its barbs."""
    ((right,),) = (_points(drawn("Regular")[c][0]) for c in SOURCES)
    tip = max(x for x, _ in right)
    axis = (right[0][1] + right[3][1]) / 2
    return [(x - tip, y - axis) for x, y in right]


class Pen:
    """Redaction's measures in a style: its minus (stroke and axis), the bars
    of its equals sign and its hairline (H's bar), from `font` (on its
    grid); Regular's hairline (`thin`), the slant of its plus, and `weight`,
    how much heavier its Bold is than its Regular (by their n's stems; 1 in
    other styles), from `smooth`."""

    def __init__(self, font, smooth, grid=None):
        cmap = font.getBestCmap()
        minus = font["glyf"][cmap[0x2212]]
        self.minus = minus.yMax - minus.yMin
        self.axis = (minus.yMax + minus.yMin) / 2
        h = path(font, "H")
        cap = font["OS/2"].sCapHeight
        bars = runs(h, x=(h.bounds[0] + h.bounds[2]) / 2)
        y0, y1 = min(bars, key=lambda r: abs(sum(r) / 2 - cap / 2))  # its bar, not its serifs
        self.hair = y1 - y0
        h = path(redaction(None, "Regular"), "H")
        bars = runs(h, x=(h.bounds[0] + h.bounds[2]) / 2)
        y0, y1 = min(bars, key=lambda r: abs(sum(r) / 2 - cap / 2))
        self.thin = y1 - y0  # Regular's hairline smooth, as on no grid, in every style
        equals = path(font, "=")
        bars = runs(equals, x=(equals.bounds[0] + equals.bounds[2]) / 2)
        self.equals = (bars[0][0], bars[-1][1])
        self.slant = slope(smooth)
        self.weight = 1
        if smooth["name"].getDebugName(2) == "Bold":
            (a, b), *_ = runs(path(smooth, "n"), y=200)
            (c, d), *_ = runs(path(redaction(None, "Regular"), "n"), y=200)
            self.weight = (b - a) / (d - c)
        self.grid = grid


class Head:
    """A head pointing right, its tip at x = 0, on its axis: its points."""

    def __init__(self, points):
        self.points = points
        self.length = -min(x for x, _ in points)
        self.half = max(y for _, y in points)

    def path(self, x=0):
        return union([[(px + x, py) for px, py in self.points]])

    @property
    def notch(self):
        """How far behind the tip its back meets the axis."""
        return -min(x for x, y in self.points if abs(y) < 0.05 * self.half)

    def inside(self, y):
        """Where along x a stroke at height `y` may end inside the head: half
        way between its back and its front, the tip at 0."""
        r = runs(self.path(), y=y)
        return (r[0][0] + r[0][1]) / 2 if r else 0


def _shaft(x0, x1, tail, neck, hold, both=False, y=0):
    """A stroke along the axis from `x0` to `x1`, as the owner's: `tail`
    thick for `hold`, then tapering to `neck`; with `both`, `tail` thick in
    the middle, tapering to `neck` at both ends, so it shows between heads."""
    if both:
        pts = [(x0, neck), ((x0 + x1) / 2, tail), (x1, neck)]
    else:
        pts = [(x0, tail), (x0 + hold, tail), (x1, neck)]
    return union([[(x, y + w / 2) for x, w in pts] + [(x, y - w / 2) for x, w in pts[::-1]]])


class Arrows:
    """The drawing of a style, from `pen` and the owner's heads (source): its
    shafts, the minus's stroke all along, and heads, on the pen's grid,
    upright there (slanted after, see _slanted)."""

    def __init__(self, pen):
        self.pen, self.grid = pen, pen.grid
        self.slant = 0 if self.grid else pen.slant
        self.blunt = 0  # radians added to the barbs' angle, on a grid
        self.length, self.hold = LENGTH, 0
        self.tail = self.neck = pen.minus

    def phase(self, axis):
        """Where in a cell `axis` falls: 0 on its edge, 0.5 in its middle."""
        return (axis / self.grid) % 1 if self.grid else 0

    def cells(self, w, odd=None):
        """A stroke `w` thick on the grid: whole cells, at least one, an odd
        number for one centred in a cell, even on an edge (`odd`), so its
        pixels are as many on either side."""
        if not self.grid:
            return w
        k = w / self.grid
        if odd is None:
            return max(1, round(k)) * self.grid
        k = max(1 if odd else 2, 2 * math.floor((k - odd) / 2 + 0.5) + odd)
        return k * self.grid

    def head(self, scale=1, half=0, phase=0, diagonal=False, fit=False):
        """The owner's head, `scale` as big, or as it takes to be `half` out;
        in Bold its notch further back as it is heavier, so its arms are.
        On a grid, a dart as long: whole cells long, at least 3, its barbs on
        the edge of a cell from an axis at `phase`, at least 2 out (to `fit`
        two in the em, only as far out as drawn, at least 1), no wider
        than drawn (a quarter of a cell's leeway), as sharp as drawn but
        blunt enough to keep their reach (REACH); `diagonal`, those cells
        are a cell's diagonal (its half), as 45° heads cross them."""
        points = source()
        scale = max(scale, half / Head(points).half)
        weight = self.pen.weight
        # the tip's and the notch's points are those on the axis
        points = [(x * scale * (weight if abs(y) < 5 else 1), y * scale) for x, y in points]
        if not self.grid:
            return Head(points)
        h = Head(points)
        notch = -min(x for x, y in points if abs(y) < 5 * scale)
        length, half = h.length, h.half
        alpha = math.atan2(half, length)
        beta = math.atan2(half, length - notch) - alpha
        g = self.grid
        if diagonal:
            g, phase = g / math.sqrt(2), 0
        wide = half / length
        length = max(3, round(length / g)) * g
        half = math.floor((half if fit else max(half, length * wide)) / g + 0.25 - phase)
        half = (max(1 if fit else 2, half) + phase) * g
        g = self.grid
        beta = max(beta, math.asin(min(1, g / 2 / (REACH * half)))) + self.blunt
        alpha = math.atan2(half, length)
        notch = max(0, length - half / math.tan(min(alpha + beta, math.radians(89))))
        return Head([(0, 0), (-length, half), (-notch, 0), (-length, -half)])

    def tip(self, length, head, both=False):
        """Where the tip of an arrow `length` long, centred, falls: double
        headed ones are 0.6 of a head longer, so their shaft shows as much."""
        tip = (length + head.length * 0.6 * both) / 2
        return round(tip / self.grid) * self.grid if self.grid else tip

    def arrow(self, length, head, both=False, gap=0, tail=None, neck=None):
        """An arrow pointing right, centred on the origin; with `gap`, two
        strokes `gap` above and below the axis."""
        tail, neck = tail or self.tail, neck or self.neck
        tip = self.tip(length, head, both)
        pieces = [head.path(tip)]
        if both:
            pieces.append(head.path(tip).transform(-1, 0, 0, 1, 0, 0))
        for y in (gap, -gap) if gap else (0,):
            end = tip + head.inside(y + math.copysign(neck / 2, y) if y else neck / 2)
            if gap:  # its inner edge too, nearer the notch, its outer within the front
                (back, _), *_ = runs(head.path(), y=abs(y) - neck / 2) or [(end - tip, 0)]
                (_, front), *_ = runs(head.path(), y=abs(y) + neck / 2) or [(0, end - tip)]
                end = min(max(end, tip + back + 1), tip + front - 1)
            start = -end if both else -tip
            pieces.append(_shaft(start, end, tail, neck, self.hold, both, y))
        return union_paths(pieces)

    def place(self, p, angle, axis, tip, turn=0):
        """`p`, pointing right, centred on its axis, turned to `angle`,
        slanted, its axis on `axis`. On a grid, moved on along the way its
        `tip` (before turning, pointing `turn` more) points, to the edge of
        a cell, and across to where the axis of horizontal arrows falls in a
        cell, so they all pixelate alike."""
        cos, sin = math.cos(math.radians(angle)), math.sin(math.radians(angle))
        p = p.transform(cos, sin, -sin, cos, 0, 0)
        p = p.transform(1, 0, self.slant, 1, -axis * self.slant, axis)
        g = self.grid
        if not g:
            return p
        x, y = tip
        x, y = x * cos - y * sin, x * sin + y * cos + axis
        ph = self.phase(self.pen.axis) * g
        if (angle + turn) % 180 == 0:
            dx, dy = pixel.snap(x, g) - x, 0
        elif (angle + turn) % 180 == 90:
            dx, dy = pixel.snap(x - ph, g) + ph - x, pixel.snap(y, g) - y
        else:
            dx, dy = pixel.snap(x, g) - x, pixel.snap(y, g) - y
        return p.transform(1, 0, 0, 1, dx, dy)


def add_glyphs(font, smooth, grid=None):
    """Add the arrows, in both shapes, to `font`: a Redaction style, or one of
    Redaction 10 to 100 on `grid`, drawn from the owner's (source) with the
    measures of both (Pen)."""
    a = Arrows(Pen(font, smooth, grid))
    paths = _paths(a)
    if grid:
        glyphs = _pixels(a, paths)
        side = max(grid, pixel.snap(SIDE, grid))
    else:
        glyphs, side = {name: glyph(p) for name, p in paths.items()}, SIDE
    placed = {}
    for name, g in glyphs.items():
        x0, _, x1, _ = g.coordinates.calcIntBounds()
        g.coordinates.translate((side - x0, 0))
        placed[name] = (g, x1 - x0 + 2 * side)
    # Halfwidth arrows: in half an em
    half = pixel.snap_advance(500, grid or 1)
    for name in (CODEPOINTS[cp] + suffix for cp in HALFWIDTH for suffix in SIZES):
        g = placed[name][0]
        x0, _, x1, _ = g.coordinates.calcIntBounds()
        g.coordinates.translate((pixel.snap((half - x1 - x0) / 2, grid or 1), 0))
        placed[name] = (g, half)
    add(font, placed, CODEPOINTS)


def _doubles(a):
    """The axis, the strokes (tail and neck) and how far each is off the
    axis, of double arrows: the owner's shaft twice, on the axis and span of
    the equals sign (not always centred on the minus's, Redaction 50), at
    least a hairline and a half of white between them (or a cell). On a
    grid, the strokes as many cells on either side of their middle, their
    edges on those of cells."""
    pen, g = a.pen, a.grid
    lo, hi = pen.equals
    axis = (lo + hi) / 2
    tail, neck = a.tail, a.neck
    if g:  # tail and neck both odd or even cells, whichever comes nearer
        tail, neck = min(
            ((a.cells(tail, odd), a.cells(neck, odd)) for odd in (True, False)),
            key=lambda w: abs(w[0] - tail) + abs(w[1] - neck),
        )
    white = max(1.5 * pen.hair, g or 0)
    if g:
        white = max(g, math.floor(1.5 * pen.hair / g) * g)
    gap = max((hi - lo - pen.minus) / 2, (tail + white) / 2)
    if g:  # on half cells, the edges of the strokes on those of cells
        gap = math.ceil(gap * 2 / g) * g / 2
        while (axis + gap - tail / 2) % g:
            gap += g / 2
    return axis, tail, neck, gap


def _paths(a):
    """{name: path} of every arrow of the drawing `a`, and of its alt arrows
    (ss01, smaller heads), placed."""
    pen, g = a.pen, a.grid or 0
    axis2, tail2, neck2, gap = _doubles(a)

    def double(scale, both=False, diagonal=False):
        """A double arrow, pointing right, centred; its head; its strokes'
        thickness and how far each is off the axis."""
        apart, tail, neck = gap, tail2, neck2
        if g and diagonal:
            # 45°, strokes become chains of cells: at least 3 cells apart
            # along the grid (more as thick), so no corners touch; strokes
            # of a cell, a chain each (a cell's diagonal thick), 4 apart,
            # both through cells' middles
            along = round(tail2 * math.sqrt(2) / g) + 2
            along = max(along, round(2 * gap * math.sqrt(2) / g))
            if tail2 == g:
                tail = neck = g / math.sqrt(2)
                along = max(4, along + along % 2)
            apart = along * g / 2 / math.sqrt(2)
        # the barbs as far past the strokes as they are out (on a grid, a
        # hairline or a cell past their tails, a cell and a half for heads
        # smaller than drawn, so they show)
        past = apart + neck / 2
        past = apart + tail / 2 + max(pen.hair, g * (1.5 if scale < 1 else 1)) if g else 2 * past
        head = a.head(scale, past, a.phase(axis2), diagonal)
        return a.arrow(a.length, head, both, apart, tail, neck), head, tail, apart

    paths = {}
    for suffix, sizes in SIZES.items():
        scale = sizes["main"]
        for cp, (name, angle, both) in ARROWS.items():
            diagonal = bool(angle % 90)
            if cp in DOUBLES:
                axis = axis2
                p, head, _, _ = double(scale, both, diagonal)
            else:
                axis = pen.axis
                head = a.head(scale, 0, a.phase(axis), diagonal)
                # 45° on a grid, a shaft of a cell a chain of cells (a cell's diagonal thick)
                chain = g / math.sqrt(2) if g and diagonal and a.tail == g else None
                p = a.arrow(a.length, head, both, tail=chain, neck=chain)
            paths[name + suffix] = a.place(p, angle, axis, (a.tip(a.length, head, both), 0))
        # Block arrows: ⇒ closed, its tail a bar as thick as the minus;
        # filled, its outline
        p, head, tail, apart = double(scale)
        tip = a.tip(a.length, head)
        hollow = union_paths([p, rect(-tip, -apart - tail / 2, -tip + tail, apart + tail / 2)])
        for cp, (angle, filled) in BLOCK.items():
            q = _filled_in(hollow) if filled else hollow
            paths[CODEPOINTS[cp] + suffix] = a.place(q, angle, axis2, (tip, 0))
        paths |= _compound(a, suffix, sizes)
    return paths


def _filled_in(p):
    """`p` without its counters: its outer contours, filled."""
    p = pathops.op(p, pathops.Path(), pathops.PathOp.UNION, clockwise=True)
    out = pathops.Path()
    for c in p.contours:
        if c.clockwise:
            out = pathops.op(out, c, pathops.PathOp.UNION, clockwise=True)
    return out


def _polygon(points):
    return union([points])


def _along(points, widths):
    """A stroke along the polyline `points`, `widths` thick at each."""
    left, right = [], []
    for i, (x, y) in enumerate(points):
        a, b = points[max(0, i - 1)], points[min(len(points) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        k = math.hypot(dx, dy)
        nx, ny = -dy / k, dx / k
        w = widths[i] / 2
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    return _polygon(left + right[::-1])


def _compound(a, suffix, sizes):
    """{name: path} of the compound, curved and halfwidth arrows of the
    drawing `a`, their heads `sizes` (SIZES) as big, named with `suffix`,
    placed."""
    pen, g = a.pen, a.grid or 0
    t, neck, axis = a.tail, a.neck, pen.axis
    ph = a.phase(axis)
    small = a.head(sizes["pair"], 0, ph)
    if small.length >= a.tip(a.length, small):  # heads meet: smaller, two in the em
        small = a.head(sizes["pair"], 0, ph, fit=True)
    length = a.length

    def cells(v, phase=0, up=False):  # `v` on the grid, at `phase` in a cell
        if not g:
            return v
        return ((math.ceil if up else round)(v / g - phase) + phase) * g

    def arrow(length=length, head=small, barb=False):
        """An arrow pointing right, centred; with `barb`, a harpoon, its barb
        up: half its head (on a grid, 3 cells out at least, so it shows), its
        tip on the shaft's lower edge, the shaft into its notch."""
        if not barb:
            return a.arrow(length, head)
        head = a.head(sizes["pair"], 3 * g, ph) if g else head
        tip = a.tip(length, head)
        half = pathops.op(
            head.path(tip), rect(-length, 0, length, length), pathops.PathOp.INTERSECTION
        )
        shaft = _shaft(-tip, tip - head.notch, t, neck, a.hold)
        return union_paths([shaft, half.transform(1, 0, 0, 1, 0, -neck / 2)])

    def place(p, angle=0, *, tip, turn=0, axis=axis):
        return a.place(p, angle, axis, tip, turn)

    end = a.tip(length, small)
    # each off the axis: two hairlines (smooth, as on no grid) between them,
    # between their heads too where they come over each other (on a grid)
    apart = (small.half + t / 2 + pen.thin * 2) / 2
    if small.length >= a.tip(length, small):
        apart = max(apart, small.half + pen.thin)
    apart = cells(apart, up=True)
    above = apart

    def pair(above):
        return union_paths(
            [arrow().transform(1, 0, 0, 1, 0, above), arrow().transform(-1, 0, 0, 1, 0, -apart)]
        )

    # ⇄, turned a quarter ⇅ (up on the left), mirrored ⇆ ⇵; slanted by rows
    # of cells, upright ones a cell further apart (STANDING)
    across, standing = pair(apart), pair(apart + (g if pen.slant else 0))
    mirror = (-1, 0, 0, 1, 0, 0)
    shapes = {
        0x21C4: place(across, tip=(end, apart)),
        0x21C5: place(standing, 90, tip=(end, apart)),
        0x21C6: place(across.transform(*mirror), tip=(-end, apart)),
        0x21F5: place(standing.transform(*mirror), 90, tip=(-end, apart)),
    }
    # ⇌: rightwards, barb up, over leftwards, barb down; ⇋ mirrored
    hp = cells((t + pen.thin * 2) / 2, up=True)
    harpoons = union_paths(
        [
            arrow(barb=True).transform(1, 0, 0, 1, 0, hp),
            arrow(barb=True).transform(-1, 0, 0, -1, 0, -hp),
        ]
    )
    shapes[0x21CC] = place(harpoons, tip=(end, hp))
    shapes[0x21CB] = place(harpoons.transform(-1, 0, 0, 1, 0, 0), tip=(-end, hp))
    # ↹: a bar at the tip of each arrow, into it, leftwards over rightwards
    into = 0 if g else t / 4
    stop = union_paths([arrow(), rect(end - into, -small.half, end - into + t, small.half)])
    stops = union_paths(
        [stop.transform(-1, 0, 0, 1, 0, above), stop.transform(1, 0, 0, 1, 0, -apart)]
    )
    shapes[0x21B9] = place(stops, tip=(end, -apart))
    # ↸: ↖ under a bar as wide as it, as heavy as ↹'s
    corner = a.head(sizes["pair"], 0, ph, diagonal=True)
    nw = arrow(length * 0.85, corner).transform(
        -(0.5**0.5), 0.5**0.5, -(0.5**0.5), -(0.5**0.5), 0, 0
    )
    x0, _, x1, y1 = nw.bounds
    y = y1 + cells(pen.hair, up=True)
    tip = a.tip(length * 0.85, corner)
    shapes[0x21B8] = place(
        union_paths([nw, rect(x0, y, x1, y + t)]), tip=(-tip * 0.5**0.5, tip * 0.5**0.5), turn=135
    )
    # Curved: rightwards along the bottom, then a quarter turn up (or down),
    # tapering from the turn as the owner's shaft does, into its head (CURL)
    curl = a.head(sizes["curl"], 0, ph)
    for cp, way in CURVED.items():
        r, w = cells(length * 0.35), cells(length * 0.8)
        tip = cells(r + curl.length * 0.3, ph)  # its tip on a cell's edge, its tail in place
        pts = [(-w / 2, -r), (w / 2 - r, -r)]
        pts += [
            (w / 2 - r + r * math.cos(th), r * math.sin(th))
            for th in (math.radians(-90 + 90 * i / 16) for i in range(1, 17))
        ]
        pts.append((w / 2, tip + curl.inside(neck / 2)))
        dist = [0]
        for p0, p1 in zip(pts, pts[1:]):
            dist.append(dist[-1] + math.dist(p0, p1))
        hold = dist[1]
        widths = [t if s <= hold else t + (neck - t) * (s - hold) / (dist[-1] - hold) for s in dist]
        line = _along(pts, widths).transform(1, 0, 0, way, 0, 0)
        head = curl.path(0).transform(0, way, -way, 0, w / 2, way * tip)
        shapes[cp] = place(union_paths([line, head]), tip=(w / 2, way * tip), turn=90)
    alt = a.head(sizes["half"], 0, ph)
    for cp, angle in HALFWIDTH.items():
        shapes[cp] = place(arrow(HALF, alt), angle, tip=(a.tip(HALF, alt), 0))
    return {CODEPOINTS[cp] + suffix: p for cp, p in shapes.items()}


def _pieces(p):
    """How many pieces `p` is in: its outer contours."""
    p = pathops.op(p, pathops.Path(), pathops.PathOp.UNION, clockwise=True)
    return sum(c.clockwise for c in p.contours)


def _pixels(a, paths):
    """{name: glyph} of `paths` pixelated on the grid of `a`, upright.

    Arrows that are others turned or mirrored (TURNED) are their pixels so,
    for every direction to pixelate alike, where their drawing falls. One
    whose pixels come apart where its drawing does not (a needle barb, a
    pixel alone) is drawn again with blunter barbs, BLUNT degrees at a time,
    until they hold together. Pinholes and notches are filled (_filled),
    then Italic's slanted (_slanted)."""
    g = a.grid
    turned = {n: t for n, t in TURNED.items() if not (a.pen.slant and n in STANDING)}
    own = {n: p for n, p in paths.items() if n not in turned}
    glyphs = pixelate_glyphs({n: glyph(p) for n, p in own.items()}, g)
    pieces = {n: _pieces(p) for n, p in own.items()}
    for step in range(1, 1 + round(45 / BLUNT)):
        apart = [n for n, gl in glyphs.items() if cells(gl, g)[2][0] > pieces[n]]
        if not apart:
            break
        a.blunt = math.radians(step * BLUNT)
        again = _paths(a)
        glyphs |= pixelate_glyphs({n: glyph(again[n]) for n in apart}, g)
    a.blunt = 0
    lo, hi = a.pen.equals

    def axis(name):  # of its strokes, in cells
        return ((lo + hi) / 2 if name.split(".")[0] in EQUALS else a.pen.axis) / g

    ink = {}  # name: {(x, y) of its cells}
    for name, gl in glyphs.items():
        on, (x0, top), _ = cells(gl, g)
        drawing = pathops.op(paths[name], pathops.Path(), pathops.PathOp.UNION)

        def near(x, y, p=drawing):  # whether its drawing covers a quarter of a cell
            cell = rect(x * g, y * g, (x + 1) * g, (y + 1) * g)
            return abs(pathops.op(p, cell, pathops.PathOp.INTERSECTION).area) >= g * g / 4

        ink[name] = _filled(_ink(on, x0, top), near)
        if name.split(".")[0] in SYMMETRIC:  # as many cells either side of its axis
            ink[name] |= {(x, round(2 * axis(name)) - 1 - y) for x, y in ink[name]}
    for name, (of, steps) in turned.items():
        on, _, _ = _grid(ink[of])
        on = _turned(on, steps)
        x0, y0, x1, y1 = paths[name].bounds  # where its drawing falls
        left = round((x0 + x1) / 2 / g - on.shape[1] / 2)
        ink[name] = _ink(on, left, round((y0 + y1) / 2 / g + len(on) / 2))
    out = {}
    for name, cells_ in ink.items():
        slant, p = a.pen.slant, paths[name]
        if slant:
            p = p.transform(1, 0, slant, 1, -axis(name) * g * slant, 0)
        p = pathops.op(p, pathops.Path(), pathops.PathOp.UNION, clockwise=True)

        def covers(x, y, p=p):  # whether the drawing covers a cell's middle
            return p.contains(((x + 0.5) * g, (y + 0.5) * g))

        if slant:  # bridged where drawn, else anywhere no gap closes
            pieces = _count(cells_)
            for test in (covers, lambda x, y: True):
                moved = _slanted(cells_, slant, axis(name), test)
                if _count(moved) <= pieces:
                    break
            # white slanting encloses: pinholes, but between double strokes
            # and inside block arrows only where they had ink
            hollow = name.split(".")[0] in EQUALS - {f"uni{cp:04X}" for cp in BLOCK} | HOLLOW
            cells_ = _sealed(_kept(moved, pieces), cells_ if hollow else None, slant, axis(name))
        out[name] = _traced(*_grid(cells_), g)
    return out


def _ink(on, x0, top):
    """{(x, y)} of cells `on` (rows down), its left at grid x `x0`, top at y
    `top`: each cell by its bottom left corner, in cells."""
    return {(x0 + j, top - i - 1) for i, j in zip(*np.nonzero(on))}


def _grid(ink):
    """Cells (rows down) of `ink`, the grid x of its left, y of its top."""
    x0, y0 = min(x for x, _ in ink), min(y for _, y in ink)
    x1, y1 = max(x for x, _ in ink), max(y for _, y in ink)
    on = np.zeros((y1 - y0 + 1, x1 - x0 + 1), bool)
    for x, y in ink:
        on[y1 - y, x - x0] = True
    return on, x0, y1 + 1


def _filled(ink, near=None):
    """`ink` filled where pixelating left a pinhole (a cell of white
    enclosed, which no arrow is drawn with), and with `near`, a notch (a
    cell its drawing touches, `near`, with ink on three sides and outside
    on the fourth)."""
    on, x0, top = _grid(ink)
    white = ~np.pad(on, 1)
    seen = np.zeros(white.shape, bool)
    ink = set(ink)
    edges = ((0, 1), (1, 0), (0, -1), (-1, 0))
    for start in zip(*np.nonzero(white)):
        if seen[start]:
            continue
        seen[start], todo, region = True, [start], []
        while todo:
            i, j = todo.pop()
            region.append((i, j))
            for di, dj in edges:
                n = i + di, j + dj
                if 0 <= n[0] < white.shape[0] and 0 <= n[1] < white.shape[1]:
                    if white[n] and not seen[n]:
                        seen[n] = True
                        todo.append(n)
        cells_ = {(x0 + j - 1, top - i) for i, j in region}
        if (0, 0) in region:
            outside = cells_
        elif len(region) == 1:
            ink |= cells_
    for x, y in [(x, y) for x, y in _around(ink) if near and near(x, y)]:
        sides = [(x + dx, y + dy) for dx, dy in edges]
        if sum(c in ink for c in sides) == 3 and any(c in outside for c in sides):
            ink.add((x, y))
    return ink


def _sealed(ink, upright, slant, axis):
    """Slanted cells `ink` with the pinholes slanting opened filled: a cell of
    white enclosed (where `upright`, as it was before, had ink, if given)."""
    on, x0, top = _grid(ink)
    white = ~np.pad(on, 1)
    out = set(ink)
    for i, j in zip(*np.nonzero(white[1:-1, 1:-1])):
        i, j = i + 1, j + 1
        x, y = x0 + j - 1, top - i
        if all(not white[i + di, j + dj] for di, dj in ((0, 1), (1, 0), (0, -1), (-1, 0))):
            if upright is None or (x - round((y + 0.5 - axis) * slant), y) in upright:
                out.add((x, y))
    return out


def _count(ink):
    """How many pieces cells `ink` are in, touching at corners too."""
    left, pieces = set(ink), 0
    while left:
        pieces += 1
        todo = [left.pop()]
        while todo:
            x, y = todo.pop()
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if (x + dx, y + dy) in left:
                        left.remove((x + dx, y + dy))
                        todo.append((x + dx, y + dy))
    return pieces


def _kept(ink, pieces):
    """`ink` but its smallest pieces of a cell or two, past `pieces`: a barb's
    tip slanting pulled off."""
    left, found = set(ink), []
    while left:
        todo, piece = [left.pop()], set()
        while todo:
            x, y = todo.pop()
            piece.add((x, y))
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if (x + dx, y + dy) in left:
                        left.remove((x + dx, y + dy))
                        todo.append((x + dx, y + dy))
        found.append(piece)
    found.sort(key=len)
    while len(found) > pieces and len(found[0]) <= 2:
        found.pop(0)
    return set().union(*found)


def _around(ink):
    """The white cells next to `ink`."""
    edges = ((0, 1), (1, 0), (0, -1), (-1, 0))
    return {(x + dx, y + dy) for x, y in ink for dx, dy in edges} - ink


def _turned(on, steps):
    """Cells `on` mirrored ("x", "y") or turned (quarter turns, anticlockwise)."""
    for step in steps:
        if step == "x":
            on = on[:, ::-1]
        elif step == "y":
            on = on[::-1]
        else:
            on = np.rot90(on, step // 90)
    return on


def _slanted(ink, slant, axis, covers):
    """Cells `ink` slanted about `axis` (in cells): each row moved over by
    whole cells, as far as its middle slants. Where that pulls two cells
    that touched apart, one reaches over to touch again: the lower, or the
    upper, where the slanted drawing covers it (`covers`, of a cell), where
    it does not close a gap."""
    shift = {y: round((y + 0.5 - axis) * slant) for _, y in ink}
    out = {(x + shift[y], y) for x, y in ink}
    for x, y in ink:
        for dx in (-1, 0, 1):
            if (x + dx, y - 1) in ink:
                up, down = x + shift[y], x + dx + shift[y - 1]
                if abs(up - down) > 1:
                    way = 1 if up > down else -1
                    for cx, cy in ((down + way, y - 1), (up - way, y)):
                        # not where it would close a gap a cell wide
                        gap = {(cx - 1, cy), (cx + 1, cy)} <= out or {
                            (cx, cy - 1),
                            (cx, cy + 1),
                        } <= out
                        if covers(cx, cy) and not gap:
                            out.add((cx, cy))
                            break
    return out


def _traced(on, x0, top, g):
    """A glyph of cells `on`, its left at grid x `x0`, its top at y `top`."""
    pen = TTGlyphPen(None)
    for contour in pixel._trace(on):
        pen.moveTo(((x0 + contour[0][0]) * g, (top + contour[0][1]) * g))
        for x, y in contour[1:]:
            pen.lineTo(((x0 + x) * g, (top + y) * g))
        pen.closePath()
    return pen.glyph()


def add_features(font):
    """Add `calt` and `ss01`, for every script and language system, to the
    merged font."""
    glyph = font.getBestCmap()
    hyphen, less, greater, caret, equal, period, underscore = (glyph[ord(c)] for c in "-<>^=._")
    table = font["GSUB"].table
    ligatures = otl.LigatureSubstBuilder(font, None)
    ligatures.ligatures = {
        (less, hyphen, greater): glyph[0x2194],
        (hyphen, greater): glyph[0x2192],
        (less, hyphen): glyph[0x2190],
        (hyphen, caret): glyph[0x2191],
        (caret, hyphen): glyph[0x2193],
        (less, equal, greater): glyph[0x21D4],
        (equal, greater): glyph[0x21D2],
        (equal, caret): glyph[0x21D1],
    }
    table.LookupList.Lookup.append(ligatures.build())
    ligatures.lookup_index = len(table.LookupList.Lookup) - 1
    # The first rule that matches applies: emoticons first, to keep them as
    # typed (^-^, ^=^, =^.^=, =^_^=), and longer sequences before the ones
    # they start with.
    calt = otl.ChainContextSubstBuilder(font, None)
    for before, sequence, after in [
        ([], [caret, hyphen], [{caret}]),
        ([{caret}], [equal, caret], []),
        ([], [equal, caret], [{period, underscore}]),
    ]:
        calt.rules.append(
            otl.ChainContextualRule(before, [{g} for g in sequence], after, [None, None])
        )
    for sequence in ligatures.ligatures:
        lookups = [[ligatures]] + [None] * (len(sequence) - 1)
        calt.rules.append(otl.ChainContextualRule([], [{g} for g in sequence], [], lookups))
    layout.add_feature(table, "calt", calt.build())

    # After calt in the lookup list, so it also swaps the arrows calt makes.
    params = ot.FeatureParamsStylisticSet()
    params.Version = 0
    params.UINameID = font["name"].addName(SS01_NAME, platforms=((3, 1, 0x409),))
    alt = {glyph[cp]: name + ".ss01" for cp, name in CODEPOINTS.items()}
    layout.add_feature(table, "ss01", otl.buildLookup([otl.buildSingleSubstSubtable(alt)]), params)
