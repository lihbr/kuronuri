"""Building blocks for glyphs drawn from Redaction's own: its slant, its
glyphs as paths and components, text set as typed, emboldening, blending
towards its Bold, measuring strokes, unions of polygons, circles and
rectangles, pixelation of glyphs drawn outside a font, where in a cell they
fall best, and adding them to it."""

import copy
import functools
import io
import math

import numpy as np
import pathops
import uharfbuzz as hb
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.basePen import BasePen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.recordingPen import DecomposingRecordingPen, RecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib.tables._c_m_a_p import cmap_format_12

import pixel
from family import redaction

CUT = 14  # half the width of Redaction's carving (20 to 27 across), and some
SLIVER = 3  # half the width of the thinnest of it: thinner, it is a sliver along a concave edge
SIDE = 0.8  # of ink along a gap, for it to run along a stroke
BAND = 20  # width of a cut along a bowl, as Redaction's carving is across
SHORTER = 0.2  # of the length of a cut along a bowl, taken off for it to read as deep
DEEP = 60  # most length of it through the strokes as drawn: Bold's n d h (53 to 58)
STRAIGHT = 0.995  # of ink along it, for that stroke to be straight
# Least area and mean width, most width and length of its gaps: smaller, it
# is the curl of a terminal (r), which grows together
CARVING = (300, 4, 60, 180)
THIN = 10  # most that Bold is thinned, on each side, or its hairlines go
SLIP = 2  # longest line that is a slip of the pen, not drawn: only for a unit in Bold's 6 and 9
SMOOTH = 2  # most degrees an outline turns at a point for it to be smooth
MITER = 4  # farthest a tip grows past its corner (sideways), over how much: sharper, it is cut
TAPER = 2.5  # of its stem: how far from a tip a stroke tapers to it, grown (sideways)
CORNER = 20  # least degrees an outline turns at a point for it to be a corner, where a stroke ends
KAPPA = 0.5523  # control point distance of a cubic quarter circle, over its radius
SHIFTS = 8  # spots within a cell a glyph is tried at, across and up or down (phased)
NEARBY = 4  # points of the outline a gap of carving moves as, blended
ALONG = 8  # of them on each segment
SPECK = 20  # least area of a gap of carving, under which it is noise (score.SPECK)
STEP = 1 / 16  # of t, that a glyph that does not blend so far is blended by (enclosed)


def slope(smooth):
    """The slant of the plus of `smooth`, a Redaction style without a grid:
    run over rise, 0 when upright. The fonts do not set an italic angle."""
    plus = smooth["glyf"][smooth.getBestCmap()[ord("+")]]
    coords = list(plus.getCoordinates(smooth["glyf"])[0])
    top = [x for x, y in coords if y == plus.yMax]
    bottom = [x for x, y in coords if y == plus.yMin]
    return (sum(top) / len(top) - sum(bottom) / len(bottom)) / (plus.yMax - plus.yMin)


def path(font, char, transform=(1, 0, 0, 1, 0, 0)):
    """The outline of `char` in `font`, transformed, as a path."""
    p = pathops.Path()
    font.getGlyphSet()[font.getBestCmap()[ord(char)]].draw(
        TransformPen(pathops.PathPen(p), transform)
    )
    return p


def embolden(p, amount, round=False):
    """`p` with `amount` added to each side of its strokes, or taken off them
    when it is less than 0, with sharp corners (or `round`)."""
    if not amount:
        return p
    stroke = pathops.Path()
    p.draw(pathops.PathPen(stroke))
    join = pathops.LineJoin.ROUND_JOIN if round else pathops.LineJoin.MITER_JOIN
    stroke.stroke(2 * abs(amount), pathops.LineCap.BUTT_CAP, join, 4)
    stroke.convertConicsToQuads()
    op = pathops.PathOp.UNION if amount > 0 else pathops.PathOp.DIFFERENCE
    return pathops.op(p, stroke, op)


class _Sweep(BasePen):
    """The area each segment of an outline sweeps moved from `amount` left
    to right, unioned into `ops`, an OpBuilder."""

    def __init__(self, amount, ops):
        super().__init__(None)
        self.amount, self.ops = amount, ops

    def _moveTo(self, pt):
        self.start = pt

    def _sweep(self, pts):
        a, start = self.amount, self._getCurrentPoint()
        *offs, end = pts
        swept = pathops.Path()
        segment = {1: swept.lineTo, 2: swept.quadTo, 3: swept.cubicTo}[len(pts)]
        swept.moveTo(start[0] - a, start[1])
        segment(*(c for x, y in pts for c in (x - a, y)))  # along it, moved left
        swept.lineTo(end[0] + a, end[1])
        segment(*(c for x, y in [*offs[::-1], start] for c in (x + a, y)))  # back, moved right
        swept.close()
        self.ops.add(swept, pathops.PathOp.UNION)

    def _lineTo(self, pt):
        self._sweep([pt])

    def _qCurveToOne(self, a, b):
        self._sweep([a, b])

    def _curveToOne(self, a, b, c):
        self._sweep([a, b, c])

    def _closePath(self):
        if self._getCurrentPoint() != self.start:
            self._sweep([self.start])


def sideways(p, amount, carve=False, pointed=True, thick=None):
    """`p` with `amount` added to each side of its strokes across only: as
    wide as `p` moved from `amount` left to right sweeps. Stems grow, strokes
    across do not, an edge as much as it faces across. Tips pointing up or
    down stay pointed (_tips), where the sweep cuts them flat, unless not
    `pointed`: carving is cut as swept (_gaps), its tips added after. With `carve`,
    Redaction's carving, which growing fills, is kept (_gaps): its gaps are
    widened by `amount` first, for the strokes around them to grow back to
    their edges, then cut on through the new edges where they open. Grown
    so, it raises if its pieces or counters change, or its carving closes:
    fewer gaps of it than `p` has."""
    if carve:
        around, through = _gaps(p, amount)
        widened = pathops.op(p, around, pathops.PathOp.DIFFERENCE)
        out = sideways(widened, amount, pointed=False)
        out = pathops.op(out, through, pathops.PathOp.DIFFERENCE)
        if pointed:  # after: cut with them, its curves split where its tips are not
            carved = embolden(union_paths([around, through]), CUT)
            out = _pointed(*_tapered(out, widened, amount, thick, carved))
        if len(grooves(out)) < len(grooves(p)):
            raise ValueError(f"grown by {amount:.1f}: its carving closes")
        if _pieces(out) != _pieces(p):
            raise ValueError(f"grown by {amount:.1f}: its pieces or counters change")
        return out
    ops = pathops.OpBuilder()
    for d in (-amount, amount):
        ops.add(p.transform(1, 0, 0, 1, d, 0), pathops.PathOp.UNION)
    p.draw(_Sweep(amount, ops))
    grown = ops.resolve()
    return _pointed(*_tapered(grown, p, amount, thick)) if pointed else grown


class _Corners(BasePen):
    """The corners of an outline: (point, unit tangent in, unit tangent out),
    and whether its contours turn counterclockwise, as its largest does."""

    def __init__(self):
        super().__init__(None)
        self.contours, self.area = [], (0, 0)

    def _moveTo(self, pt):
        self.contours.append([])
        self.start = pt

    def _segment(self, pts):
        start = self._getCurrentPoint()
        if any(_unit(start, q) for q in pts):
            self.contours[-1].append([start, *pts])

    def _lineTo(self, pt):
        self._segment([pt])

    def _qCurveToOne(self, a, b):
        self._segment([a, b])

    def _curveToOne(self, a, b, c):
        self._segment([a, b, c])

    def _closePath(self):
        if self._getCurrentPoint() != self.start:
            self._segment([self.start])
        contour = self.contours[-1]
        area = sum(s[0][0] * s[-1][1] - s[-1][0] * s[0][1] for s in contour) / 2
        self.area = max(self.area, (abs(area), area))

    def corners(self):
        for contour in self.contours:
            for before, seg in zip(contour[-1:] + contour[:-1], contour):
                u = next(t for q in before[-2::-1] if (t := _unit(q, before[-1])))
                v = next(t for q in seg[1:] if (t := _unit(seg[0], q)))
                yield seg[0], u, v


def _tips(p, amount):
    """Where growing `p` across by `amount` (sideways) cuts a tip flat, twice
    `amount` wide: at a corner that turns out, sharper than smooth (SMOOTH),
    its edges facing opposite ways across, a tip pointing up or down. Each:
    the ends of that flat, and where its two edges grown meet (a miter), or,
    farther than MITER times `amount` from the corner, where they cross that
    distance."""
    pen = _Corners()
    p.draw(pen)
    side = 1 if pen.area[1] > 0 else -1  # outward: right of the way it turns
    out = []
    for (x, y), u, v in pen.corners():
        cross, dot = u[0] * v[1] - u[1] * v[0], u[0] * v[0] + u[1] * v[1]
        a, b = side * u[1], side * v[1]  # how much each edge faces across, outward
        if side * cross <= 0 or dot > math.cos(math.radians(SMOOTH)) or a * b >= 0:
            continue
        # Its edges grown: moved across, out, and where they meet
        (ax, ay), (bx, by) = (x + math.copysign(amount, a), y), (x + math.copysign(amount, b), y)
        t = ((bx - ax) * v[1] - (by - ay) * v[0]) / cross
        apex = ax + u[0] * t, ay + u[1] * t
        far = math.dist((x, y), apex)
        if far <= MITER * amount:
            out.append(((ax, ay), (bx, by), [apex]))
            continue
        # Cut across, MITER * amount from the corner: where each edge crosses it
        dx, dy = (apex[0] - x) / far, (apex[1] - y) / far
        cut = MITER * amount
        ends = []
        for (sx, sy), (tx, ty) in (((ax, ay), u), ((bx, by), v)):
            k = (cut - (sx - x) * dx - (sy - y) * dy) / (tx * dx + ty * dy)
            ends.append((sx + tx * k, sy + ty * k))
        out.append(((ax, ay), (bx, by), ends))
    return out


def _tapered(grown, p, amount, thick=None, carved=None):
    """`grown`, `p` swept across by `amount`, its strokes tapering to a tip
    (_tips) grown as much as they are thick: along the outline from the
    flat the sweep cuts a tip to, both ways, while the stroke widens away
    from it, thinner across than `thick` (the stem of `p`, by default),
    within TAPER of it of the tip, short of a corner of `p` (CORNER), and
    not on its carving (`carved`), edges
    are moved back across, for it to be as much wider as a stroke `thick`
    grows. The tip ends where it did in `p`. And the tips whose flat it did
    not find, to point otherwise (_pointed)."""
    tips = _tips(p, amount)
    thick = thick or stem(p)
    contours = _contours(grown)
    pen = _Corners()
    p.draw(pen)
    edges = [(pt, u, v) for pt, u, v in pen.corners()]
    sharp = [pt for pt, u, v in edges if u[0] * v[0] + u[1] * v[1] < math.cos(math.radians(CORNER))]
    left = []
    for a, b, between in tips:
        found = next(
            (
                (contour, i)
                for contour in contours
                for i, (s0, op, args) in enumerate(contour)
                if op == "lineTo"
                and {_near(s0, a), _near(args[0], b)} == {True}
                or op == "lineTo"
                and {_near(s0, b), _near(args[0], a)} == {True}
            ),
            None,
        )
        if found is None:
            left.append((a, b, between))
            continue
        contour, i = found
        tip = ((a[0] + b[0]) / 2, a[1])
        corners = [c for c in sharp if math.dist(c, tip) > 2 * amount]  # in `p`, but its end's
        n = len(contour)
        moves = {}  # segment: its points moved
        for step in (1, -1):  # after the flat, then before it
            k, widest, side = i + step, 0, 0
            for _ in range(n - 1):
                seg = contour[k % n]
                pts = [seg[0], *seg[2]]
                moved = [_back(grown, pt, amount, thick, tip) for pt in pts]
                width = _width(grown, pts[-1 if step == 1 else 0], amount)
                on_carving = carved is not None and any(carved.contains(q) for q in pts)
                corner = any(math.dist(q, c) < 1.5 * amount for q in pts for c in corners)
                if moved == pts or width < widest - 1 or on_carving or corner:  # another stroke
                    break
                moves[k % n], widest, side = moved, max(widest, width), side + 1
                k += step
            if not side:  # a corner of a stroke as thick, not a stroke tapering to it
                break
        else:
            for k, moved in moves.items():
                contour[k][0], contour[k][2] = moved[0], tuple(moved[1:])
            flat = contour[i]
            flat[0], flat[2] = tip, (tip,)
            prev, nxt = contour[i - 1], contour[(i + 1) % n]
            prev[2] = (*prev[2][:-1], tip)
            nxt[0] = tip
            continue
        left.append((a, b, between))
    out = _path(contours)
    return pathops.op(out, pathops.Path(), pathops.PathOp.UNION), left


def _width(grown, pt, amount):
    """How wide across the stroke of `grown` at `pt` was before growing by
    `amount`; 0 off it."""
    x, y = pt
    run = next(((a, b) for a, b in runs(grown, y=y) if a - 0.5 <= x <= b + 0.5), None)
    return max(run[1] - run[0] - 2 * amount, 0) if run else 0


def _back(grown, pt, amount, thick, tip):
    """`pt` of `grown` moved back across toward where it was before growing
    by `amount`, as much as its stroke there is thinner than `thick`, near
    `tip`, within TAPER stems."""
    x, y = pt
    if math.dist(pt, tip) >= TAPER * thick:
        return pt
    # Its stroke there: the run it is on, or, off the curve, the nearest
    spans = [(max(a - x, x - b, 0), (a, b)) for a, b in runs(grown, y=y)]
    off, run = min(spans, default=(math.inf, None))
    if off > 2 * amount:
        return pt
    width = max(run[1] - run[0] - 2 * amount, 0)  # in what was grown
    moved = amount * (1 - min(1, width / thick))
    return (x + moved, y) if x < (run[0] + run[1]) / 2 else (x - moved, y)


def _contours(p):
    """The contours of `p` as segments [start, op, args], closed by a line."""
    rec = RecordingPen()
    p.draw(rec)
    contours = []
    for op, args in rec.value:
        if op == "moveTo":
            contours.append([])
            start = current = args[0]
        elif op in ("lineTo", "qCurveTo", "curveTo"):
            contours[-1].append([current, op, args])
            current = args[-1]
        elif op == "closePath" and math.dist(current, start) > 1e-9:
            contours[-1].append([current, "lineTo", (start,)])
    return contours


def _path(contours):
    """A path of contours of segments [start, op, args]."""
    out = pathops.Path()
    pen = pathops.PathPen(out)
    for contour in contours:
        pen.moveTo(contour[0][0])
        for _, op, args in contour:
            getattr(pen, op)(*args)
        pen.closePath()
    return out


def _pointed(p, tips):
    """`p`, swept (sideways), its flats at `tips` (_tips) pointed again: each
    line from one end of a flat to the other, either way, goes through its
    points instead, the outline otherwise as it is. Where a side of a tip
    carries on a line, they are one. A flat not found, its tip is added."""
    rec = RecordingPen()
    p.draw(rec)
    contours = []  # each, its segments: [start, op, args]
    for op, args in rec.value:
        if op == "moveTo":
            contours.append([])
            start = current = args[0]
        elif op in ("lineTo", "qCurveTo", "curveTo"):
            contours[-1].append([current, op, args])
            current = args[-1]
        elif op == "closePath" and math.dist(current, start) > 1e-9:
            contours[-1].append([current, "lineTo", (start,)])
    missed = []
    for a, b, between in tips:
        for contour in contours:
            i = next(
                (
                    i
                    for i, (s0, op, args) in enumerate(contour)
                    if op == "lineTo"
                    and {_near(s0, a), _near(args[0], b)} == {True}
                    or op == "lineTo"
                    and {_near(s0, b), _near(args[0], a)} == {True}
                ),
                None,
            )
            if i is not None:
                s0, _, (s1,) = contour[i]
                chain = [s0, *(between if _near(s0, a) else between[::-1]), s1]
                contour[i : i + 1] = [[q, "lineTo", (r,)] for q, r in zip(chain, chain[1:])]
                for j in (i + len(chain) - 1, i):  # its ends, the later first
                    _join(contour, j % len(contour))
                break
        else:
            missed.append(union([[a, *between, b]]))
    out = pathops.Path()
    for contour in contours:
        out.moveTo(*contour[0][0])
        pen = pathops.PathPen(out)
        for _, op, args in contour:
            getattr(pen, op)(*args)
        out.close()
    for tip in missed:
        out = pathops.op(out, tip, pathops.PathOp.UNION)
    return out


def _near(a, b):
    return math.dist(a, b) < 1e-3  # pathops keeps floats


def _join(contour, j):
    """Segment `j` of `contour` ([start, op, args]) and the one before it
    made one, in place, where both are lines and one carries on the other."""
    (s0, op0, (e0, *_)), (s1, op1, (e1, *_)) = contour[j - 1], contour[j]
    u, v = _unit(s0, e0), _unit(s1, e1)
    if op0 == op1 == "lineTo" and u and v and abs(u[0] * v[1] - u[1] * v[0]) < 1e-4:
        if u[0] * v[0] + u[1] * v[1] > 0:
            contour[j - 1] = [s0, "lineTo", (e1,)]
            del contour[j]


def stem(p):
    """The mean width of the stems of `p`, at half its height."""
    spans = runs(p, y=(p.bounds[1] + p.bounds[3]) / 2)
    return sum(b - a for a, b in spans) / len(spans)


def grooves(p):
    """Redaction's carving in `p`: where a stroke stops short of another,
    thin gaps and wedges, which `p` emboldened by CUT and thinned back fills
    (carving). Not corners filled, which are wider or longer (CARVING), or
    slivers along concave edges (SLIVER). Each gap and its hull."""
    gaps, out = list(carving(p).contours), []
    for gap in gaps:
        points = _hull(list(gap.points))
        if any(_within(gap.bounds, other.bounds) for other in gaps if other is not gap):
            continue
        if abs(gap.area) < CARVING[0] or len(points) < 3:
            continue
        _, (u0, u1), (v0, v1) = _extent(points)
        if abs(gap.area) / (u1 - u0) < CARVING[1] or v1 - v0 > CARVING[2] or u1 - u0 > CARVING[3]:
            continue
        out.append((gap, points))
    return out


def _notches(p):
    """The gaps of the carving of `p` (carving), but specks (SPECK), as
    score.py counts them."""
    return [c for c in carving(p).contours if abs(c.area) >= SPECK]


def _gaps(p, amount):
    """Redaction's carving in `p` (grooves), to grow it by `amount` across
    only (sideways). Returns its gaps, where they go, widened by `amount`,
    and their cuts through the new edges.

    A gap keeps its size. Along a straight stroke (_side), as in Bold, it
    moves away from it as far as its edge moves, as much as it faces across,
    flush with it, the stroke stopping short of it that much shorter, and out
    to the new edge where it opens (_mouths), if only at one end: by `amount`
    at most. Along a bowl, it stays where it is, and is cut on through the
    new edges where it opens, along its length. Where it only touches the
    air at a point, a wedge meeting the outline, the strokes grow together."""
    grown = pathops.op(sideways(p, amount, pointed=False), p, pathops.PathOp.DIFFERENCE)
    around, through = [], []
    for gap, points in grooves(p):
        (ux, uy), _, _ = _extent(points)
        mouths, tips = _mouths(p, gap, points, amount)
        # Along its length where it opens at an end
        for i, (mx, my) in enumerate(mouths):
            along = mx * ux + my * uy
            if abs(along) > 0.7:
                mouths[i] = (ux, uy) if along > 0 else (-ux, -uy)
        side = _side(p, points)
        if side and not side[3]:
            through.append(_band(p, gap, points, side, amount))
            continue
        moves = []
        if side and side[3]:
            r = abs(side[0])
            moves = [(-side[0] * r, -side[1] * r)]
            if len(mouths) == 1 and mouths[0][0] * -side[0] + mouths[0][1] * -side[1] < 0.7:
                # Out to the new edge it opens through, nearer when it moved
                # along it slanted (t in Italic), no farther: across the mouth
                # of a wedge, from a stroke to another, its edge is no line
                mx, my = mouths.pop()
                ex, ey = _facing(points, mx, my)
                out = (abs(ex) + r * (side[0] * ex + side[1] * ey)) / max(mx * ex + my * ey, 0.5)
                moves.append((mx * min(out, 1), my * min(out, 1)))
        dx = sum(x for x, _ in moves) * amount
        dy = sum(y for _, y in moves) * amount
        gap = gap.transform(1, 0, 0, 1, dx, dy)
        points = [(x + dx, y + dy) for x, y in points]
        widened = sideways(gap, amount, pointed=False)
        for tip in tips:
            tip = embolden(tip.transform(1, 0, 0, 1, dx, dy), amount + CUT / 2, round=True)
            widened = pathops.op(widened, tip, pathops.PathOp.DIFFERENCE)
        around.append(widened)
        for mx, my in mouths:
            far = 2 * amount + CUT
            out = union([_hull(points + [(x + mx * far, y + my * far) for x, y in points])])
            through.append(pathops.op(out, grown, pathops.PathOp.INTERSECTION))
    return union_paths(around), union_paths(through)


def carving(p):
    """Where strokes of `p` stop short of others, and more: what `p`
    emboldened by CUT and thinned back fills, but slivers (SLIVER)."""
    filled = pathops.op(embolden(embolden(p, CUT), -CUT), p, pathops.PathOp.DIFFERENCE)
    # Within it, and without holes: thinning a needle, its edges cross
    opened = embolden(embolden(filled, -SLIVER), SLIVER)
    return pathops.op(opened, filled, pathops.PathOp.INTERSECTION)


def _band(p, gap, points, side, amount):
    """The cut for a gap of `p` along a bowl, `p` grown by `amount` across
    only: the bowl's new edge carried on, as Redaction's carving reads. A
    band as wide as its carving (BAND) along the bowl grown, over where the
    gap was, out through the new edges where it opens, and, open at one end,
    shorter at the other, by as far as that edge moved and SHORTER of what
    shows, and to DEEP at most: the strokes it cuts through are thicker.
    Edges move as much as they face across."""
    nx, ny, (qx, qy), _ = side
    moved = abs(nx) * amount
    (ux, uy) = _extent(points)[0]
    reach = 3 * amount + CUT
    x0, y0, x1, y1 = gap.bounds
    box = rect(x0 - reach, y0 - reach, x1 + reach, y1 + reach)
    # The bowl: beyond the gap's edge along it, near it
    tx, ty, far = -ny, nx, 4 * reach
    beyond = union(
        [
            [
                (qx - tx * far - nx, qy - ty * far - ny),
                (qx + tx * far - nx, qy + ty * far - ny),
                (qx + tx * far + nx * far, qy + ty * far + ny * far),
                (qx - tx * far + nx * far, qy - ty * far + ny * far),
            ]
        ]
    )
    bowl = pathops.op(
        pathops.op(p, beyond, pathops.PathOp.INTERSECTION), box, pathops.PathOp.INTERSECTION
    )
    bolder = sideways(bowl, amount, pointed=False)
    band = pathops.op(embolden(bolder, BAND, round=True), bolder, pathops.PathOp.DIFFERENCE)
    # Where the gap was, moved off the bowl with its edge, and on out where it opens
    zone = points + [(x - nx * moved, y - ny * moved) for x, y in points]
    opens, _ = _mouths(p, gap, points, math.inf)
    ends = [(ux, uy) if mx * ux + my * uy > 0 else (-ux, -uy) for mx, my in opens]
    for dx, dy in ends:
        zone += [(x + dx * reach, y + dy * reach) for x, y in zone]
    cut = pathops.op(band, union([_hull(zone)]), pathops.PathOp.INTERSECTION)
    if len(ends) == 1:
        (dx, dy), far = ends[0], 10 * reach

        def kept(start):
            corners = ((start, -far), (start + far, -far), (start + far, far), (start, far))
            strip = union([[(dx * u - dy * v, dy * u + dx * v) for u, v in corners]])
            return pathops.op(cut, strip, pathops.PathOp.INTERSECTION)

        cut = kept(min(x * dx + y * dy for x, y in points) + abs(dx) * amount)
        # And shorter still by SHORTER of what shows of it in the glyph, and
        # through its strokes as drawn by DEEP at most
        shown = pathops.op(cut, sideways(p, amount, pointed=False), pathops.PathOp.INTERSECTION)
        us = [x * dx + y * dy for c in shown.contours for x, y in c.points]
        if us:
            cut = kept(min(us) + SHORTER * (max(us) - min(us)))
        inside = pathops.op(cut, p, pathops.PathOp.INTERSECTION)
        us = [x * dx + y * dy for c in inside.contours for x, y in c.points]
        if us and max(us) - min(us) > DEEP:
            cut = kept(max(us) - DEEP)
    return cut


def _mouths(p, gap, points, amount):
    """Where a gap of `p`, `points` its hull, opens narrower than strokes
    emboldened by `amount` on both sides would close: the directions from it
    to the air it touches. And the air it only touches at a point."""
    cx, cy = _centroid(points)
    air = pathops.op(embolden(gap, 2), union_paths([p, gap]), pathops.PathOp.DIFFERENCE)
    mouths, tips = [], []
    for mouth in air.contours:
        if abs(mouth.area) < 2:
            continue
        mx, my = _centroid(list(mouth.points))
        length = math.hypot(mx - cx, my - cy)
        dx, dy = (mx - cx) / length, (my - cy) / length
        across = [y * dx - x * dy for x, y in mouth.points]
        if max(across) - min(across) < CUT / 2:
            tips.append(mouth)
        elif max(across) - min(across) < 2 * amount:
            mouths.append((dx, dy))
    return mouths, tips


def _side(p, points):
    """The stroke a gap of `p`, `points` its hull, runs along (the one the
    other stops short of): its longest edge with ink all along it outside,
    and past its ends, as the direction to it, a point of that edge and
    whether it is straight: ink all along, not curving away. None if none."""
    cx, cy = _centroid(points)
    best, side = 0, None
    for (x0, y0), (x1, y1) in zip(points, points[1:] + points[:1]):
        length = math.hypot(x1 - x0, y1 - y0)
        if length < CUT or length <= best:
            continue
        ux, uy = (x1 - x0) / length, (y1 - y0) / length
        nx, ny = -uy, ux  # away from the gap
        if nx * (x0 - cx) + ny * (y0 - cy) < 0:
            nx, ny = -nx, -ny
        a, b = (x0 - ux * 2 * CUT, y0 - uy * 2 * CUT), (x1 + ux * 2 * CUT, y1 + uy * 2 * CUT)
        d = CUT / 2
        strip = union([[a, b, (b[0] + nx * d, b[1] + ny * d), (a[0] + nx * d, a[1] + ny * d)]])
        covered = pathops.op(strip, p, pathops.PathOp.INTERSECTION)
        inked = sum(abs(c.area) for c in covered.contours) / abs(strip.area)
        if inked > SIDE:
            best, side = length, (nx, ny, (x0, y0), inked > STRAIGHT)
    return side


def _facing(points, dx, dy):
    """The outward normal of the edge of a convex polygon, counterclockwise,
    that faces most towards (dx, dy)."""
    normals = []
    for (x0, y0), (x1, y1) in zip(points, points[1:] + points[:1]):
        length = math.hypot(x1 - x0, y1 - y0)
        if length:
            normals.append(((y1 - y0) / length, (x0 - x1) / length))
    return max(normals, key=lambda n: n[0] * dx + n[1] * dy)


def _within(inner, outer):
    return all(i >= o for i, o in zip(inner[:2], outer[:2])) and all(
        i <= o for i, o in zip(inner[2:], outer[2:])
    )


def _centroid(points):
    return sum(x for x, _ in points) / len(points), sum(y for _, y in points) / len(points)


def _extent(points):
    """The smallest rectangle around `points`, a convex polygon: the unit
    vector along its length, and the spans of `points` along it and across."""
    best = None
    for (x0, y0), (x1, y1) in zip(points, points[1:] + points[:1]):
        angle = math.atan2(y1 - y0, x1 - x0)
        for a in (angle, angle + math.pi / 2):
            ux, uy = math.cos(a), math.sin(a)
            us = [x * ux + y * uy for x, y in points]
            vs = [y * ux - x * uy for x, y in points]
            u, v = (min(us), max(us)), (min(vs), max(vs))
            if u[1] - u[0] >= v[1] - v[0] and (
                best is None or (u[1] - u[0]) * (v[1] - v[0]) < best[0]
            ):
                best = ((u[1] - u[0]) * (v[1] - v[0]), (ux, uy), u, v)
    return best[1:]


def _hull(points):
    """The convex hull of `points`, counterclockwise (Andrew's monotone chain)."""
    points = sorted(set(points))

    def half(points):
        out = []
        for p in points:
            while (
                len(out) > 1
                and (
                    (out[-1][0] - out[-2][0]) * (p[1] - out[-2][1])
                    - (out[-1][1] - out[-2][1]) * (p[0] - out[-2][0])
                )
                <= 0
            ):
                out.pop()
            out.append(p)
        return out

    lower, upper = half(points), half(points[::-1])
    return lower[:-1] + upper[:-1]


def shrunk(smooth, scale, weight=1, target=None, of="n"):
    """The font to shrink `smooth`'s glyphs by `scale` from, and how much to
    embolden them first (or thin them, below 0), so the stems of `of` match
    `target`, those of n of `smooth` (times `weight`) by default.

    Emboldened, strokes lose their carving (where stems meet bowls): thinned,
    they keep it. Bold is heavier shrunk, for an upright Regular `smooth`:
    thinned a little (up to THIN), it keeps its carving."""
    target = target or stem(path(smooth, "n")) * weight
    sources = [smooth]
    if smooth["OS/2"].usWeightClass < 700 and not slope(smooth):
        sources.insert(0, redaction(None, "Bold"))
    for source in sources:
        amount = (target / scale - stem(path(source, of))) / 2
        if amount >= -THIN or source is smooth:
            return source, amount


@functools.cache
def masters():
    """Redaction's Regular and Bold, smooth, to blend glyphs between."""
    return redaction(None, "Regular"), redaction(None, "Bold")


def blend(font, regular, bold, char, t, sliver=False):
    """`char` of `font` made heavier as Redaction's Bold is of its Regular, a
    path: its outline plus `t` times the way from `regular`'s to `bold`'s
    (beyond Bold past 1). Italic has no masters: it gets the upright way,
    slanted. Strokes grow as MCKL drew them, hairlines and carving kept.
    Outlines are matched first (_match); None when they do not. Grown too
    far, strokes run into each other: it raises where the outline turns
    back (_smooth), pieces or counters are not those of `font`'s, or the
    middle of a gap of its carving, moved as the outline around it
    (NEARBY), is ink. With `sliver`, it does not take for gaps the edges of
    slivers round a stroke, whose middle is ink, which skia-pathops leaves
    where edges nearly meet: only for enclosed content, as the superscripts
    rely on what it refuses."""
    run = slope(font)
    a, b = cubics(regular, char), cubics(bold, char)
    matched = _match([a], b, 0)
    if not matched:
        return None
    [a], b = matched
    matched = _match([a, b], cubics(font, char), run)
    if not matched:
        return None
    [a, b], own = matched
    p, moves = pathops.Path(), []
    for ca, cb, co in zip(a, b, own):
        out = []
        for sa, sb, so in zip(ca, cb, co):
            out.append(
                [
                    (x + t * (xb - xa + (yb - ya) * run), y + t * (yb - ya))
                    for (xa, ya), (xb, yb), (x, y) in zip(sa, sb, so)
                ]
            )
            for i in range(ALONG):
                was, now = _at(so, i / ALONG), _at(out[-1], i / ALONG)
                moves.append((was, (now[0] - was[0], now[1] - was[1])))
        _smooth(out, co, char)
        p.moveTo(*out[0][0])
        for seg in out:
            if len(seg) == 2:
                p.lineTo(*seg[1])
            else:
                p.cubicTo(*seg[1], *seg[2], *seg[3])
        p.close()
    p = pathops.op(p, pathops.Path(), pathops.PathOp.UNION)
    source = path(font, char)
    if _pieces(p) != _pieces(source):
        raise ValueError(f"{char} blended by {t:.2f}: its pieces or counters change")
    for gap in carving(source).contours:
        x, y = _centroid(list(gap.points))
        if sliver and source.contains((x, y)):  # a sliver round a stroke
            continue
        near = sorted(moves, key=lambda m: math.dist(m[0], (x, y)))[:NEARBY]
        dx, dy = (sum(m[1][k] for m in near) / len(near) for k in (0, 1))
        if p.contains((x + dx, y + dy)):
            raise ValueError(f"{char} blended by {t:.2f}: its carving closes")
    return p


def blend_text(font, text, t):
    """`text` in `font`, each glyph blended by `t` (blend) between Redaction's
    Regular and Bold (masters), as a path. Each stands where its own is
    set as typed, plus `t` times the way from where Regular's is to where
    Bold's is, as its points: heavier, letters are wider. Raises if one
    does not blend. `font` is not to change."""
    regular, bold = masters()
    sets = [_set(f, _shaper(f), text)[0] for f in (font, regular, bold)]
    run = slope(font)
    out = pathops.Path()
    for char, (_, x, y), (_, xa, ya), (_, xb, yb) in zip(text, *sets):
        p = blend(font, regular, bold, char, t)
        if p is None:
            raise ValueError(f"{char} of Redaction's Regular, Bold and this style do not match")
        out = pathops.op(
            out,
            p.transform(1, 0, 0, 1, x + t * (xb - xa + (yb - ya) * run), y + t * (yb - ya)),
            pathops.PathOp.UNION,
        )
    return out


@functools.cache
def _shaper(font):
    return shaper(font)


def _at(seg, s):
    """The point at `s` along a segment, a line or a cubic."""
    if len(seg) == 2:
        (x0, y0), (x1, y1) = seg
        return x0 + (x1 - x0) * s, y0 + (y1 - y0) * s
    u = 1 - s
    w = (u**3, 3 * u * u * s, 3 * u * s * s, s**3)
    return tuple(sum(c * pt[k] for c, pt in zip(w, seg)) for k in (0, 1))


def _pieces(p):
    """How many pieces and counters `p` has."""
    contours = list(p.contours)
    outer = max(contours, key=lambda c: abs(c.area)).clockwise
    counters = sum(c.clockwise != outer for c in contours)
    return len(contours) - counters, counters


def _smooth(contour, source, char):
    """Turn the handles of `contour` (segments as lists) where `source`, the
    contour it was made from, is smooth (SMOOTH), for it to stay so: along
    a line, or between both. Blending turns handles each its own way. Where
    they turn back, the outline folds: it raises (`char` to say which)."""
    for i, (seg, was) in enumerate(zip(contour, source)):
        before, came = contour[i - 1], source[i - 1]
        if len(seg) == len(before) == 2:
            continue
        node = seg[0]
        into, out = _unit(came[-2], was[0]), _unit(was[0], was[1])
        a, b = _unit(before[-2], node), _unit(node, seg[1])
        if not (into and out and a and b):
            continue
        if into[0] * out[0] + into[1] * out[1] < math.cos(math.radians(SMOOTH)):
            continue
        if a[0] * b[0] + a[1] * b[1] < 0:
            raise ValueError(f"{char} blended folds at {node}")
        if len(before) == 2:
            d = a
        elif len(seg) == 2:
            d = b
        else:
            d = _unit((0, 0), (a[0] + b[0], a[1] + b[1]))
        if len(before) == 4:
            r = math.dist(before[2], node)
            before[2] = (node[0] - d[0] * r, node[1] - d[1] * r)
        if len(seg) == 4:
            r = math.dist(seg[1], node)
            seg[1] = (node[0] + d[0] * r, node[1] + d[1] * r)


def cubics(font, char):
    """The outline of `char` in `font` as contours of segments, lines (two
    points) and cubics (four), for blend. Redaction's TrueType curves are
    its cubics cut evenly (cu2qu): each run of them between on-curve points
    is fitted back into one. Slips (SLIP) are left out."""
    gs = font.getGlyphSet()
    pen = DecomposingRecordingPen(gs)
    gs[font.getBestCmap()[ord(char)]].draw(pen)
    contours = []
    for op, args in pen.value:
        if op == "moveTo":
            contours.append([])
            start = current = args[0]
        elif op == "lineTo" and math.dist(current, args[0]) > SLIP:
            contours[-1].append((current, args[0]))
            current = args[0]
        elif op == "qCurveTo":
            contours[-1].append(_cubic(current, args))
            current = args[-1]
        elif op == "closePath" and math.dist(current, start) > SLIP:
            contours[-1].append((current, start))
    return contours


def _cubic(start, quads):
    """The cubic from `start` through the TrueType curves `quads` (off-curve
    points, then the end), as cu2qu cut it: evenly, so the piece i of n
    runs from i/n to (i + 1)/n of it, along the same tangents at its ends.
    How long its handles are is fitted (least squares). This takes
    Redaction's curves to be cut so: cut otherwise, the fit is off."""
    *offs, end = quads
    u, v = _unit(start, offs[0]), _unit(end, offs[-1])
    uv = u[0] * v[0] + u[1] * v[1]
    ons = [start, *(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2) for a, b in zip(offs, offs[1:])), end]
    m11 = m12 = m22 = r1 = r2 = 0
    n, steps = len(offs), 8
    for i, (a, c, b) in enumerate(zip(ons, offs, ons[1:])):
        for j in range(steps + (i == n - 1)):
            s = j / steps
            pt = [(1 - s) ** 2 * a[k] + 2 * (1 - s) * s * c[k] + s * s * b[k] for k in (0, 1)]
            t = (i + s) / n
            b0, b1, b2, b3 = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t**3
            rest = [pt[k] - (b0 + b1) * start[k] - (b2 + b3) * end[k] for k in (0, 1)]
            m11, m12, m22 = m11 + b1 * b1, m12 + b1 * b2 * uv, m22 + b2 * b2
            r1 += b1 * (u[0] * rest[0] + u[1] * rest[1])
            r2 += b2 * (v[0] * rest[0] + v[1] * rest[1])
    det = m11 * m22 - m12 * m12
    a, b = (r1 * m22 - r2 * m12) / det, (m11 * r2 - m12 * r1) / det
    return (
        tuple(start),
        (start[0] + u[0] * a, start[1] + u[1] * a),
        (end[0] + v[0] * b, end[1] + v[1] * b),
        tuple(end),
    )


def _match(masters, other, run):
    """`masters`, outlines that match (cubics), and `other` (slanted by
    `run`) made to match: each contour started where it does in the
    masters, and where one has a segment more, the other's cut in two where
    their points then fall nearest (_cost). None if they cannot."""
    if any(len(m) != len(other) for m in masters):
        return None
    masters, other = [list(m) for m in masters], list(other)
    for k, contour in enumerate(other):
        ours = [m[k] for m in masters]
        found = _pair(ours, contour, run)
        if not found:
            return None
        ours, other[k] = found
        for m, c in zip(masters, ours):
            m[k] = c
    return masters, other


def _pair(ours, contour, run):
    """Contours `ours`, which match, and `contour` made to match them, as
    _match does: cut once at most, lines and curves alike. None if not."""
    if abs(len(ours[0]) - len(contour)) > 1:
        return None
    if len(ours[0]) < len(contour):
        candidates = [([_cut(c, i, u) for c in ours], contour) for i, u in _cuts(ours[0])]
    elif len(ours[0]) > len(contour):
        candidates = [(ours, _cut(contour, i, u)) for i, u in _cuts(contour)]
    else:
        candidates = [(ours, contour)]
    (cost, turn), ours, contour = min(
        ((_cost(o[0], c, run), o, c) for o, c in candidates),
        key=lambda x: x[0][0],
        default=((math.inf, 0), None, None),
    )
    if cost == math.inf:
        return None
    return ours, contour[turn:] + contour[:turn]


def _cuts(contour):
    """Where a segment of `contour` can be cut: (index, t). Lines only at
    their start, their point doubled: where Bold has a line more, it is
    flat where Regular's strokes meet at a point (the apex of A, the foot
    of N)."""
    return [
        (i, u / 20) for i, s in enumerate(contour) for u in (range(1, 20) if len(s) == 4 else [0])
    ]


def _cut(contour, i, t):
    """`contour` with its segment `i` cut in two at `t` (de Casteljau)."""
    if len(contour[i]) == 2:
        (x0, y0), (x1, y1) = contour[i]
        mid = (x0 + (x1 - x0) * t, y0 + (y1 - y0) * t)
        return contour[:i] + [((x0, y0), mid), (mid, (x1, y1))] + contour[i + 1 :]
    p0, p1, p2, p3 = contour[i]

    def at(a, b):
        return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)

    a, b, c = at(p0, p1), at(p1, p2), at(p2, p3)
    d, e = at(a, b), at(b, c)
    f = at(d, e)
    return contour[:i] + [(p0, a, d, f), (f, e, c, p3)] + contour[i + 1 :]


def _cost(ours, theirs, run):
    """How far the on-curve points of contour `theirs` (slanted by `run`)
    fall from those of `ours`, each centred, at the start it fits best: the
    sum of their squared distances, and that start. inf if lines and
    curves do not fall alike."""

    def points(contour, run):
        pts = [(x - y * run, y) for x, y in (s[0] for s in contour)]
        cx, cy = _centroid(pts)
        return [(x - cx, y - cy) for x, y in pts]

    best = (math.inf, 0)
    if len(ours) != len(theirs):
        return best
    kinds = [len(s) for s in ours]
    a, b = points(ours, 0), points(theirs, run)
    for turn in range(len(theirs)):
        if [len(s) for s in theirs[turn:] + theirs[:turn]] != kinds:
            continue
        cost = sum(math.dist(p, q) ** 2 for p, q in zip(a, b[turn:] + b[:turn]))
        best = min(best, (cost, turn))
    return best


def _unit(a, b):
    """The unit vector from `a` to `b`, None if they are the same."""
    length = math.dist(a, b)
    return ((b[0] - a[0]) / length, (b[1] - a[1]) / length) if length else None


def runs(p, y=None, x=None):
    """The strokes `p` crosses along the line at height `y` (or abscissa
    `x`): sorted (start, end) pairs, to measure stems and hairlines."""
    x0, y0, x1, y1 = p.bounds
    axis = 0 if y is not None else 1
    if axis == 0:
        line = rect(x0 - 1, y - 0.5, x1 + 1, y + 0.5)
    else:
        line = rect(x - 0.5, y0 - 1, x + 0.5, y1 + 1)
    cut = pathops.op(p, line, pathops.PathOp.INTERSECTION)
    return sorted((c.bounds[axis], c.bounds[axis + 2]) for c in cut.contours)


def rect(x0, y0, x1, y1):
    p = pathops.Path()
    p.moveTo(x0, y0)
    for pt in ((x1, y0), (x1, y1), (x0, y1)):
        p.lineTo(*pt)
    p.close()
    return p


def circle(cx, cy, r):
    p = pathops.Path()
    k = r * KAPPA
    p.moveTo(cx + r, cy)
    p.cubicTo(cx + r, cy + k, cx + k, cy + r, cx, cy + r)
    p.cubicTo(cx - k, cy + r, cx - r, cy + k, cx - r, cy)
    p.cubicTo(cx - r, cy - k, cx - k, cy - r, cx, cy - r)
    p.cubicTo(cx + k, cy - r, cx + r, cy - k, cx + r, cy)
    p.close()
    return p


def glyph(p):
    """A TrueType glyph of the path `p`, curves made quadratic."""
    p = pathops.op(p, pathops.Path(), pathops.PathOp.UNION, clockwise=True)
    pen = TTGlyphPen(None)
    p.draw(Cu2QuPen(pen, 1, reverse_direction=False))
    g = pen.glyph()
    g.recalcBounds(None)
    return g


def union_paths(paths):
    p = pathops.Path()
    for q in paths:
        p = pathops.op(p, q, pathops.PathOp.UNION)
    return p


def content(font, shape, text, lines=1.25):
    """`text` in `font`, as typed (`shape`, its shaper), as a path centred on
    x = 0, its lines one under the other, `lines` cap heights apart."""
    rows = []
    for i, line in enumerate(text.split("\n")):
        glyphs = []
        for name, x, y in _set(font, shape, line)[0]:
            g = pathops.Path()
            font.getGlyphSet()[name].draw(pathops.PathPen(g))
            glyphs.append(g.transform(1, 0, 0, 1, x, y))
        row = union_paths(glyphs)
        x0, _, x1, _ = row.bounds
        down = i * font["OS/2"].sCapHeight * lines
        rows.append(row.transform(1, 0, 0, 1, -(x0 + x1) / 2, -down))
    return union_paths(rows)


def union(polygons):
    path = pathops.Path()
    for points in polygons:
        p = pathops.Path()
        p.moveTo(*points[0])
        for pt in points[1:]:
            p.lineTo(*pt)
        p.close()
        path = pathops.op(path, p, pathops.PathOp.UNION, clockwise=True)
    return path


def composite(font, parts, grid):
    """A glyph made of (glyph name, dx, dy) components of `font`, offsets on
    the grid. Renderers draw outlines at their side bearing, a few of
    Redaction's a unit off their leftmost point; components are drawn where
    they are, so they get the difference added."""
    glyf, pen = font["glyf"], TTGlyphPen(font["glyf"])
    for name, dx, dy in parts:
        dx = pixel.snap(dx, grid or 1)
        if glyf[name].numberOfContours:
            glyf[name].recalcBounds(glyf)
            dx += font["hmtx"][name][1] - glyf[name].xMin
        pen.addComponent(name, (1, 0, 0, 1, dx, pixel.snap(dy, grid or 1)))
    return pen.glyph()


def shaper(font):
    """A HarfBuzz font of `font` as it is now, to set text with its kerning.
    HarfBuzz cannot read WOFF2, which Redaction's are."""
    data, flavor = io.BytesIO(), font.flavor
    font.flavor = None
    font.save(data)
    font.flavor = flavor
    return hb.Font(hb.Face(hb.Blob(data.getvalue())))


def typed(font, shaper, text, grid):
    """`text` as typed in `font`, kerning included (`shaper`, of `font`): a
    glyph made of its glyphs (components), offsets on the grid, and its
    advance."""
    parts, x = _set(font, shaper, text)
    return composite(font, parts, grid), pixel.snap(x, grid or 1)


def _set(font, shaper, text):
    """`text` set in `font` without ligatures: [(glyph name, x, y)], and its
    advance."""
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(shaper, buf, {"liga": False})
    order, parts, x = font.getGlyphOrder(), [], 0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        parts.append((order[info.codepoint], x + pos.x_offset, pos.y_offset))
        x += pos.x_advance
    return parts, x


def add(font, glyphs, codepoints):
    """Add {name: (glyph, advance)} to `font`, and map `codepoints` (code
    point: name) to them. Redaction's cmaps are format 4, which stop at
    U+FFFF: code points past it (🄰) get a format 12 one."""
    glyf, hmtx = font["glyf"], font["hmtx"]
    for name, (g, advance) in glyphs.items():
        g.recalcBounds(glyf)
        glyf[name] = g  # also appends the name to the glyph order
        hmtx[name] = (advance, g.xMin)
    font.setGlyphOrder(glyf.glyphOrder)
    cmap = font["cmap"]
    if max(codepoints, default=0) > 0xFFFF and not any(t.format == 12 for t in cmap.tables):
        table = cmap_format_12(12)
        table.platformID, table.platEncID, table.language = 3, 10, 0
        table.cmap = dict(font.getBestCmap())
        cmap.tables.append(table)
    for table in cmap.tables:
        if table.isUnicode():
            table.cmap.update(
                {c: n for c, n in codepoints.items() if c <= 0xFFFF or table.format == 12}
            )


def phased(glyphs, grid, rows, like, carved=False, distinct=False, away=None, heavy=False):
    """Glyphs drawn outside a font {name: glyph} pixelated on the grid, each
    where in a cell it falls best: hairlines of about half a cell fill one
    or not as they fall. Tried SHIFTS across, and up or down where its
    bottom and top rows stay `rows` (yMin, yMax), or its own where it was
    drawn (a flag above, a tail below): only its own if `rows` is None.
    Kept, first, with `away` ({name: {(x, y)}}, cells by their corner, over
    the grid), off those cells, at an edge or a corner: an enclosure. Then,
    if `carved`: each gap of its carving, a gap of the pixels' there
    (carving), or beside it, to half a cell, if smaller than a cell.
    Then its pieces and counters as drawn (carving closed), each counter
    where one is drawn, whether pixels joined only at a corner close it or
    not (cells), and no pixel hanging off a bowl; then on `rows`, counters
    as big as drawn, nearest where it was drawn, and strokes as thick as
    those of `like`, pixel glyphs of MCKL's (widths), or, if `heavy`, strokes
    as thick first, then nearest: stems drawn a little under a whole number
    of cells fill the cell more often than not.
    If `distinct`, no two come out alike: of two that would, the one that
    reads less as drawn (a counter drawn its pixels do not close, then the
    above) is placed where it falls best of those not alike; it raises if
    there are none."""
    theirs = [widths(cells(g, grid)[0]) for g in like]
    theirs = [sum(w) / len(w) for w in zip(*theirs)]
    placed = _placed(glyphs, grid, rows, theirs, carved, away, heavy)
    chosen = {name: options[0] for name, options in placed.items()}
    if distinct:
        names = list(placed)
        for k, name in enumerate(names):

            def yields(other, name=name, k=k):
                worse = chosen[name][:2] > chosen[other][:2]
                return worse or (chosen[name][:2] == chosen[other][:2] and names.index(other) < k)

            alike = [m for m in names if m != name and _bits(chosen[m]) == _bits(chosen[name])]
            if not any(yields(m) for m in alike):
                continue
            taken = {_bits(chosen[m]) for m in names if m != name}
            unlike = [o for o in placed[name] if _bits(o) not in taken]
            if not unlike:
                raise ValueError(f"{name} comes out as another on the {grid} grid")
            chosen[name] = unlike[0]
    return {name: option[2] for name, option in chosen.items()}


def _bits(option):
    """The cells of a placement (_placed), to tell placements alike."""
    on = cells(option[2], option[3])[0]
    return on.shape, on.tobytes()


def _placed(glyphs, grid, rows, theirs, carved, away, heavy):
    """phased: {name: its placements, best first: (how many counters drawn
    its pixels do not close, its rank, its pixels, the grid, and the spot
    it was tried at, (i, j) SHIFTS of a cell across and up)}, strokes
    against `theirs` (widths), off `away`."""
    spots = [(i, j) for i in range(SHIFTS) for j in range(1 - SHIFTS // 2, 1 + SHIFTS // 2)]
    shifted = {}
    for name, g in glyphs.items():
        for i, j in spots:
            shifted[name, i, j] = copy.deepcopy(g)
            shifted[name, i, j].coordinates.translate((i * grid / SHIFTS, j * grid / SHIFTS))
    keys = list(shifted)
    pixels = pixelate_glyphs({f"g{k}": shifted[key] for k, key in enumerate(keys)}, grid)
    pixels = {key: pixels[f"g{k}"] for k, key in enumerate(keys)}
    out = {}
    for name, g in glyphs.items():
        drawn = pathops.Path()
        g.draw(pathops.PathPen(drawn), None)
        closed = list(embolden(embolden(drawn, CUT), -CUT).contours)
        outer = max(closed, key=lambda c: abs(c.area)).clockwise
        holes = [c for c in closed if c.clockwise != outer]
        pieces = len(closed) - len(holes)
        # Where its cuts show; one smaller than a cell can show beside it, to half a cell
        gaps = [
            embolden(c, grid / 2, round=True) if abs(c.area) < grid * grid else c
            for c in (carving(drawn).contours if carved else [])
        ]

        unread = {}

        def rank(key, drawn=drawn, pieces=pieces, holes=holes, gaps=gaps, unread=unread):
            _, i, j = key
            there = drawn.transform(1, 0, 0, 1, i * grid / SHIFTS, j * grid / SHIFTS)
            lost = 0
            if gaps:
                cut = pathops.Path()
                pixels[key].draw(pathops.PathPen(cut), None)
                cut = carving(cut)
                for gap in gaps:
                    gap = gap.transform(1, 0, 0, 1, i * grid / SHIFTS, j * grid / SHIFTS)
                    lost += not pathops.op(cut, gap, pathops.PathOp.INTERSECTION).area
            on, (left, top), (n, both, spurs) = cells(pixels[key], grid, there)
            near = (away or {}).get(key[0], ())
            touch = near and any(
                (left + c + dx, top - r - 1 + dy) in near
                for r, c in zip(*np.nonzero(on))
                for dx in (-1, 0, 1)
                for dy in (-1, 0, 1)
            )
            off, hollow = abs(n - pieces), 0
            for kind, counters in enumerate(both):
                # Each in one drawn, each drawn one in one, of its size
                found = [
                    {
                        h
                        for h, hole in enumerate(holes)
                        for r, c in counter
                        if hole.contains(
                            (
                                (left + c + 0.5 - i / SHIFTS) * grid,
                                (top - r - 0.5 - j / SHIFTS) * grid,
                            )
                        )
                    }
                    for counter in counters
                ]
                off += sum(len(f) != 1 for f in found)
                missing = sum(not any(h in f for f in found) for h in range(len(holes)))
                off += missing
                if kind == 0:  # closed by every pixel, as they read
                    unread[key] = missing
                for h, hole in enumerate(holes):
                    size = sum(len(c) for f, c in zip(found, counters) if h in f) * grid * grid
                    hollow += abs(size - abs(hole.area))
            elsewhere = rows and (pixels[key].yMin, pixels[key].yMax) != rows
            thin, mid, thick = (w / t - 1 for w, t in zip(widths(on), theirs))
            strokes = abs(mid) + (abs(thin) + abs(thick)) / 2
            near = min(i, SHIFTS - i) + abs(j)
            return (
                bool(touch),
                lost,
                off,
                spurs,
                elsewhere,
                hollow,
                *((strokes, near) if heavy else (near, strokes)),
            )

        own = pixels[name, 0, 0]
        bottoms, tops = {own.yMin}, {own.yMax}
        if rows:
            bottoms.add(rows[0])
            tops.add(rows[1])
        tried = [
            (name, i, j)
            for i, j in spots
            if not j or (pixels[name, i, j].yMin in bottoms and pixels[name, i, j].yMax in tops)
        ]
        ranks = {key: rank(key) for key in tried}
        out[name] = [
            (unread[k], ranks[k], pixels[k], grid, k[1:]) for k in sorted(tried, key=ranks.get)
        ]
    return out


def cells(g, grid, drawn=None):
    """The cells of a pixel glyph, rows top down; the grid x of its left and
    y of its top; how many pieces it is in (touching at corners too: MCKL
    steps round strokes so); its counters ([[(row, column)]]), closed by
    every pixel, as they read, and by those joined to another along an
    edge or on `drawn`, covering half their cell, as they are built (not
    put back by pixel.py's dropout pass); and how many pixels hang off a
    bowl: out of the side of a stroke, joined to it along an edge only, or
    alone in its top or bottom row."""
    coords, start = [(int(x // grid), int(y // grid)) for x, y in g.coordinates], 0
    x0, y0 = min(x for x, _ in coords), min(y for _, y in coords)
    x1, y1 = max(x for x, _ in coords), max(y for _, y in coords)
    wind = np.zeros((y1 - y0, x1 - x0 + 1), int)
    for end in g.endPtsOfContours:
        pts = coords[start : end + 1]
        for (ax, ay), (bx, by) in zip(pts, pts[1:] + pts[:1]):
            if ax == bx:
                wind[min(ay, by) - y0 : max(ay, by) - y0, ax - x0] += 1 if by > ay else -1
        start = end + 1
    on = (np.cumsum(wind, axis=1)[:, :-1] != 0)[::-1]
    padded = np.pad(on, 1)
    edges = ((0, 1), (1, 0), (0, -1), (-1, 0))
    corners = edges + ((1, 1), (1, -1), (-1, 1), (-1, -1))
    pieces = len(_regions(padded, True, corners))
    joined = padded.copy()
    for i, j in zip(*np.nonzero(padded)):
        joined[i, j] = any(padded[i + di, j + dj] for di, dj in edges)
        if not joined[i, j] and drawn is not None:
            x, y = (x0 + j - 1) * grid, (y1 - i) * grid
            cell = pathops.op(drawn, rect(x, y, x + grid, y + grid), pathops.PathOp.INTERSECTION)
            joined[i, j] = abs(cell.area) >= pixel.FILL * grid * grid
    # The first region is the air around
    counters = [_regions(cells, False, edges)[1:] for cells in (padded, joined)]
    inside = np.zeros(padded.shape, bool)
    for counter in counters[0]:
        inside[tuple(zip(*counter))] = True
    spurs = 0
    for i, di in ((1, 1), (len(padded) - 2, -1)):  # alone in its top or bottom row, at a gap
        (cols,) = np.nonzero(padded[i])
        spurs += len(cols) == 1 and inside[i + di, cols[0]]
    for i, j in zip(*np.nonzero(padded & ~inside)):
        near = [(di, dj) for di, dj in edges if padded[i + di, j + dj]]
        if len(near) == 1:
            (di, dj), (ni, nj) = near[0], (i + near[0][0], j + near[0][1])
            sides = padded[ni + dj, nj + di] and padded[ni - dj, nj - di]
            spurs += bool(sides and inside[ni + di, nj + dj])
    counters = [[[(i - 1, j - 1) for i, j in c] for c in found] for found in counters]
    return on, (x0, y1), (pieces, counters, spurs)


def _regions(cells, ink, steps):
    """The regions of `cells` that are `ink`, connected by `steps`."""
    seen, regions = np.zeros(cells.shape, bool), []
    for start in zip(*np.nonzero(cells == ink)):
        if seen[start]:
            continue
        seen[start], todo, region = True, [start], []
        while todo:
            i, j = todo.pop()
            region.append((i, j))
            for di, dj in steps:
                n = i + di, j + dj
                if 0 <= n[0] < cells.shape[0] and 0 <= n[1] < cells.shape[1]:
                    if cells[n] == ink and not seen[n]:
                        seen[n] = True
                        todo.append(n)
        regions.append(region)
    return regions


def widths(on):
    """The thin, mid and thick strokes of cells `on`, as score.py measures
    them (10th, 50th and 90th percentiles): each cell's, the shortest run of
    ink through it, across or down."""
    spans = []  # across, then down
    for m in (on, on.T):
        lengths = np.zeros(m.shape)
        for i, row in enumerate(m):
            edges = np.flatnonzero(np.diff(np.concatenate([[0], row.astype(int), [0]])))
            for a, b in zip(edges[::2], edges[1::2]):
                lengths[i, a:b] = b - a
        spans.append(lengths)
    return np.percentile(np.minimum(spans[0], spans[1].T)[on], [10, 50, 90])


def pixelate_glyphs(glyphs, grid):
    """Pixelate glyphs drawn outside a font onto the grid, in place: a
    {name: glyph} dict of new glyphs."""
    # pixel.py works on a font. It keeps outlines in place if advances are
    # zero and side bearings true (FreeType moves outlines to match them).
    fb = FontBuilder(1000)
    fb.setupGlyphOrder([".notdef", *glyphs])
    fb.setupGlyf({".notdef": TTGlyphPen(None).glyph(), **glyphs})
    metrics = {n: (0, getattr(g, "xMin", 0)) for n, g in fb.font["glyf"].glyphs.items()}
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader()
    fb.setupVerticalMetrics({n: (0, 0) for n in metrics})
    fb.setupVerticalHeader()
    pixelated = pixel.pixelate_font(fb.font, grid)["glyf"]
    return {name: pixelated[name] for name in glyphs}
