"""Arrows drawn to match Redaction, which has none, and the features for them.

The arrows have open, right-angled heads, the stroke and axis of Redaction's
minus, and the slant of its plus. Double arrows (⇒) have two such strokes,
as far apart as the bars of its equals sign. `calt` turns -> <- <-> -^ ^- => <=> =^ into arrows, but
leaves the ^-^ ^=^ =^.^= emoticons alone. `ss01` swaps in alt arrows, with
smaller heads.
"""

import math

import pathops
from fontTools.otlLib import builder as otl
from fontTools.ttLib.tables import otTables as ot

import layout
import pixel

from .shapes import add, glyph, path, pixelate_glyphs, runs, slope, union, union_paths

SIDE = 35  # side bearing, as on Redaction's math signs
# glyph name suffix: (length from tail to tip, side of the arrowhead)
SHAPES = {
    "": (630, 420),  # twice the minus axis: upright arrows stand on the baseline
    ".ss01": (600, 180),
}
SS01_NAME = "Alt arrows"
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
DOUBLE = {
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
ARROWS = SINGLE | DOUBLE
# Arrows made of arrows (⇄), harpoons (⇌), block arrows (⇨ ⮕), curved
# arrows (⤴) and halfwidth arrows (￫), with smaller heads: in pairs, they
# stand in the em
COMPOUND = [0x21B8, 0x21B9, 0x21C4, 0x21C5, 0x21C6, 0x21CB, 0x21CC, 0x21F5]
BLOCK = {0x21E6: (180, False), 0x21E7: (90, False), 0x21E8: (0, False), 0x21E9: (-90, False)}
BLOCK |= {0x2B05: (180, True), 0x2B06: (90, True), 0x2B07: (-90, True), 0x2B95: (0, True)}
CURVED = {0x2934: 1, 0x2935: -1}  # rightwards, then up or down
HALFWIDTH = {0xFFE9: 180, 0xFFEA: 90, 0xFFEB: 0, 0xFFEC: -90}
SMALL = 300  # side of the heads of compound arrows
CODEPOINTS = {cp: name for cp, (name, _, _) in ARROWS.items()} | {
    cp: f"uni{cp:04X}" for cp in [*COMPOUND, *BLOCK, *CURVED, *HALFWIDTH]
}
ALTERNATES = [name + ".ss01" for name in CODEPOINTS.values()]
SAMPLES = [
    "H←↑→↓↔↕↖↗↘↙H",
    "H⇐⇑⇒⇓⇔⇕⇖⇗⇘⇙H",
    "a → b ⇒ c ↔ d ⇔ e",
    "東京→大阪⇒京都",
    "−+→ =⇒",
    "⇄⇆⇅⇵ ↹↸ ⇋⇌ ⤴⤵",
    "⇦⇧⇨⇩ ⬅⬆⬇⮕ ￩￪￫￬",
]


def _arrow(t, length, side, double, grid=None, gap=0):
    """An arrow pointing right, centred on the origin: polygons for its shaft
    and one or two mitred heads of stroke `t` and side `side`, and the joint
    where the strokes of the head meet. With a `gap`, the shaft is two
    strokes, `gap` above and below the axis, that run into the heads."""
    d, s = side / math.sqrt(2), t / math.sqrt(2)
    # Double headed arrows are a head longer, so their shaft shows as much.
    tip = (length + d * double) / 2
    if grid:  # whole cells between the joints of double heads
        tip = s + round((tip - s) * 2 / grid) * grid / 2

    def head(sign):
        x = sign * tip
        return [
            (x, 0),
            (x - sign * d, d),
            (x - sign * (d + s), d - s),
            (x - sign * 2 * s, 0),
            (x - sign * (d + s), s - d),
            (x - sign * d, -d),
        ]

    tail = -tip + t if double else -tip
    if gap:  # into the middle of the strokes of the heads
        end = tip - s - gap
        tail = -end if double else -tip
        pieces = [
            [(tail, y - t / 2), (end, y - t / 2), (end, y + t / 2), (tail, y + t / 2)]
            for y in (gap, -gap)
        ]
    else:
        pieces = [[(tail, -t / 2), (tip - t, -t / 2), (tip - t, t / 2), (tail, t / 2)]]
    pieces.append(head(1))
    if double:
        pieces.append(head(-1))
    return pieces, (tip - s, 0)


def add_glyphs(font, smooth, grid=None):
    """Add the arrows, in both shapes, to `font`: a Redaction style, or one of
    Redaction 10 to 100 on `grid`. They take the stroke and axis of its minus,
    and the slant of the plus of `smooth`, the same style without a grid.

    On a grid, arrows are pixelated, with heads at least 2.8 cells long. The
    joint of every head falls on the same spot of a cell, so all arrows
    pixelate alike: where a 45° stroke falls on the grid decides whether it
    becomes a staircase or a chain of pixels touching at the corners.

    Double arrows take the axis and span of the equals sign instead: on a
    grid, it is not always centred on the axis of the minus (Redaction 50).
    Their strokes are as thick as the minus, as those of single arrows (the
    bars of the equals sign are not always: Redaction 35, 20 Bold), and
    their joints fall where the strokes land on the grid."""
    minus = font["glyf"][font.getBestCmap()[0x2212]]
    t = minus.yMax - minus.yMin
    single = (t, (minus.yMax + minus.yMin) / 2, 0)  # stroke, axis, gap
    equals = path(font, "=")
    bars = runs(equals, x=(equals.bounds[0] + equals.bounds[2]) / 2)
    lo, hi = bars[0][0], bars[-1][1]
    double = (t, (lo + hi) / 2, (hi - lo - t) / 2)
    slant = slope(smooth)

    glyphs = {}
    for suffix, (length, side) in SHAPES.items():
        for cp, (name, angle, both) in ARROWS.items():
            cos, sin = math.cos(math.radians(angle)), math.sin(math.radians(angle))
            t, axis, gap = double if cp in DOUBLE else single
            diagonal = angle % 90 != 0
            if grid and gap and diagonal:
                # Both strokes a whole number of cells apart along the grid,
                # so they pixelate alike, as the joints do, with a cell of
                # white between them.
                least = math.ceil((t * math.sqrt(2) + grid) / 2 / grid)
                gap = max(least, round(gap * math.sqrt(2) / grid)) * grid / math.sqrt(2)

            def turn(x, y, cos=cos, sin=sin, axis=axis):  # to the angle, slanted, on the axis
                return x * cos - y * sin + (x * sin + y * cos) * slant, x * sin + y * cos + axis

            # Heads reach a stroke past the strokes of double arrows.
            head = max(side, 2.8 * (grid or 0), (gap + 1.5 * t) * math.sqrt(2) * bool(gap))
            pieces, joint = _arrow(t, length, head, both, grid, gap)
            outline = union([turn(*pt) for pt in piece] for piece in pieces)
            if grid:
                # A cell centre for odd strokes, else a corner; for double
                # arrows, wherever puts the edges of their strokes on the grid.
                phase = (t / 2 if diagonal else gap + t / 2) % grid
                x, y = turn(*joint)
                dx, dy = (pixel.snap(v - phase, grid) + phase - v for v in (x, y))
                outline = outline.transform(1, 0, 0, 1, dx, dy)
            glyphs[name + suffix] = glyph(outline)

    side = SIDE
    if grid:
        glyphs = pixelate_glyphs(glyphs, grid)
        side = max(grid, pixel.snap(SIDE, grid))

    glyphs |= _compound(single[0], single[1], slant, grid)
    placed = {}
    for name, g in glyphs.items():
        x0, _, x1, _ = g.coordinates.calcIntBounds()
        g.coordinates.translate((side - x0, 0))
        placed[name] = (g, x1 - x0 + 2 * side)
    # Halfwidth arrows: in half an em
    half = pixel.snap_advance(500, grid or 1)
    for cp in HALFWIDTH:
        g = placed[CODEPOINTS[cp]][0]
        x0, _, x1, _ = g.coordinates.calcIntBounds()
        g.coordinates.translate((pixel.snap((half - x1 - x0) / 2, grid or 1), 0))
        placed[CODEPOINTS[cp]] = (g, half)
    add(font, placed, CODEPOINTS)


def _polygon(points):
    return union([points])


def _compound(t, axis, slant, grid):
    """{name: glyph} of the compound, block, curved and halfwidth arrows, of
    stroke `t`, on `axis`, slanted by `slant`, pixelated on `grid`."""
    d, s = SMALL / math.sqrt(2), t / math.sqrt(2)
    length = SHAPES[""][0]

    def place(p, angle=0, dx=0, dy=0):
        """`p`, pointing right, turned to `angle`, moved, slanted, on the axis."""
        cos, sin = math.cos(math.radians(angle)), math.sin(math.radians(angle))
        p = p.transform(cos, sin, -sin, cos, dx, dy)
        return p.transform(1, 0, slant, 1, -axis * slant, axis)

    def arrow(length=length, side=SMALL, barb=0):
        """An arrow pointing right, centred; `barb` 1 or -1, a harpoon with
        its barb up or down."""
        pieces, _ = _arrow(t, length, side, False)
        if not barb:
            return union(pieces)
        # A harpoon: the outer edge of its barb runs on to the far side of the
        # shaft, where it comes to a point, as the heads of arrows do
        tip = pieces[-1][0][0]
        tail = pieces[0][0][0]
        arm = [
            (tip + t / 2, -t / 2),
            (tip - d, d),
            (tip - d - s, d - s),
            (tip - 2 * s - t / 2, t / 2),
            (tip - 2 * s - t / 2, -t / 2),
        ]
        shaft = [(tail, -t / 2), (tip + t / 2, -t / 2), (tip + t / 2, t / 2), (tail, t / 2)]
        big = 10 * length
        inside = [(-big, -big), (tip + big, -big), (tip - big, big), (-big, big)]  # x + y <= tip
        p = pathops.op(union([shaft, arm]), _polygon(inside), pathops.PathOp.INTERSECTION)
        return p.transform(1, 0, 0, barb, 0, 0)

    def bar(x, half):  # a vertical stroke at `x`, `half` up and down
        return _polygon([(x - t, -half), (x, -half), (x, half), (x - t, half)])

    apart = (d + t) / 2 + t  # half the distance between the arrows of a pair
    shapes = {
        0x21C4: [place(arrow(), 0, 0, apart), place(arrow(), 180, 0, -apart)],
        0x21C6: [place(arrow(), 180, 0, apart), place(arrow(), 0, 0, -apart)],
        0x21C5: [place(arrow(), 90, -apart, 0), place(arrow(), -90, apart, 0)],
        0x21F5: [place(arrow(), -90, -apart, 0), place(arrow(), 90, apart, 0)],
        0x21CC: [place(arrow(barb=1), 0, 0, apart / 2), place(arrow(barb=1), 180, 0, -apart / 2)],
        # turned, a harpoon's barb turns over: barbs up on top, down below
        0x21CB: [place(arrow(barb=-1), 180, 0, apart / 2), place(arrow(barb=-1), 0, 0, -apart / 2)],
        # ↹: a bar at the tip of each arrow, leftwards over rightwards
        0x21B9: [
            place(union_paths([arrow(), bar(length / 2 + t, d)]), 180, 0, apart),
            place(union_paths([arrow(), bar(length / 2 + t, d)]), 0, 0, -apart),
        ],
    }
    # ↸: ↖ under a bar as wide as it
    nw = place(arrow(length * 0.85), 135)
    x0, _, x1, y1 = nw.bounds
    shapes[0x21B8] = [
        nw,
        _polygon([(x0, y1 + t), (x1, y1 + t), (x1, y1 + 2 * t), (x0, y1 + 2 * t)]),
    ]
    # Block arrows: a shaft and a head, filled, or a stroke inside their outline
    head, shaft = length * 0.42, length * 0.15
    block = [
        (-length / 2, -shaft),
        (length / 2 - head, -shaft),
        (length / 2 - head, -length * 0.32),
        (length / 2, 0),
        (length / 2 - head, length * 0.32),
        (length / 2 - head, shaft),
        (-length / 2, shaft),
    ]
    for cp, (angle, filled) in BLOCK.items():
        p = _polygon(block)
        if not filled:
            edge = pathops.Path()
            p.draw(pathops.PathPen(edge))
            edge.stroke(2 * t, pathops.LineCap.BUTT_CAP, pathops.LineJoin.MITER_JOIN, 10)
            p = pathops.op(p, edge, pathops.PathOp.INTERSECTION)
        shapes[cp] = [place(p, angle)]
    # Curved: rightwards along the bottom, then a quarter turn up (or down)
    for cp, way in CURVED.items():
        r, w = length * 0.35, length * 0.8
        line = pathops.Path()
        line.moveTo(-w / 2, -way * r)
        line.lineTo(w / 2 - r, -way * r)
        k = r * 0.5523
        line.cubicTo(w / 2 - r + k, -way * r, w / 2, -way * k, w / 2, 0)
        # Into the head, as far as the shafts of arrows go
        line.lineTo(w / 2, way * (r - t))
        line.stroke(t, pathops.LineCap.BUTT_CAP, pathops.LineJoin.MITER_JOIN, 4)
        head = _arrow(t, length, SMALL, False)[0][-1]
        head = _polygon([(x - head[0][0], y) for x, y in head])  # its tip at the origin
        shapes[cp] = [place(line), place(head, way * 90, w / 2, way * r)]
    for cp, angle in HALFWIDTH.items():
        shapes[cp] = [place(arrow(440, SHAPES[".ss01"][1]), angle)]
    glyphs = {CODEPOINTS[cp]: glyph(union_paths(parts)) for cp, parts in shapes.items()}
    return pixelate_glyphs(glyphs, grid) if grid else glyphs


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
    alt = {glyph[cp]: name + ".ss01" for cp, (name, _, _) in ARROWS.items()}
    layout.add_feature(table, "ss01", otl.buildLookup([otl.buildSingleSubstSubtable(alt)]), params)
