#!/usr/bin/env python3
"""Score the glyphs drawn from Redaction's own against those MCKL drew.

Redaction has small figures and capitals of its own: ¹ ² ³, the 4 of ¼ and
the 5 of ⅗, and the T and M of ™, in every variant. Drawn again from 1 2 3
4 5, T and M the way glyphs/ draws those it lacks (figures._superior,
symbols.small_caps), then pixelated as the numbered variants are, they
should come out as MCKL drew them: that is the score, for each style and
variant. Then how the superscripts drawn (⁰ ⁴ to ⁹) compare with
Redaction's ¹ ² ³ in the same font, and how clean the outlines of every
drawn glyph are, against Redaction's own.

The superscript letters (ª º, those of ordinals, ℀ ℅: letters), against
MCKL's ¹ ² ³ and Redaction's letters in the same font, each and as a set
(their percentiles averaged), with the worst letter:
- stem: their mid stroke over that of ¹, 1 when as heavy (± 0.05)
- hairline: their thin strokes over those of ¹ ² ³, 1 when as thin
- contrast: their thin over thick strokes, over those of the letters they
  are shrunk from, against ¹ ² ³ over 1 2 3 (mckl)
- x-height: how far the top of their n is from that of ¹, and how big it
  is against ¹, over n against 1: 1 when as big
- carving, where a pixel shows it (CARVED): their gaps matched one to one
  with those of the fonts approved (APPROVED), moved onto them, notches
  touching at a corner one gap on a grid: kept, a gap matched no more than
  DEPTH longer or shorter, and at least WIDE as wide; missing, those
  approved unmatched, and extra, those not approved
- hygiene: what is not clean in their outlines (hygiene), over a glyph

For each glyph drawn again, against Redaction's, its ink aligned on theirs:
- iou: the ink both have, over the ink either has, 1 when the same
- thin, mid, thick: the thickness of its strokes (10th, 50th and 90th
  percentiles across its ink), over Redaction's: 1 when as thick
- carving: how far its carving is from Redaction's, 0 when the same: where
  stems meet bowls, gaps Redaction's ink closed by CUT fills, matched one
  to one, their length and width compared; one missing or extra counts 1
- loss: 1 - iou, |mid - 1|, half of |thin - 1| and |thick - 1|, and half of
  carving where a pixel is small enough to show it (CARVED). Lower is better

Enclosed digits and capitals (glyphs/enclosed.py) have no glyph of MCKL's
to be scored against: their content is measured against n, the
superscripts, the small caps of ℡ ℻ and the superscript letters in the
same font, and Redaction's own as typed at its size, for each glyph and as
a mean and worst glyph per group (digit ①, number ⑳, capital Ⓐ, lowercase
ⓐ, word 🆒), in the fonts drawn and in those last approved
(.cache/approved): see enclosed_glyphs.

Writes temp/score: score.json, everything measured, and, per style, PNGs
of the glyphs drawn again over Redaction's (redrawn-<style>.png: shared
ink black, ink only Redaction has blue, ink only the drawing has orange,
the drawing's points green, on the curve, and grey, off it, carving pale:
Redaction's blue, the drawing's orange, both grey, and the loss of each as
a bar), the smooth ones twice as big (redrawn-base.png, a row a style), and
the superscripts as built (superiors-<style>.png: Redaction's blue, drawn
ones black). Draws the fonts first (draw.py).

usage: score.py [--variants base,10,...] [--styles Regular,Italic,Bold] [--no-draw]
"""

import argparse
import json
import math
import struct
import sys
import zlib
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pathops
from fontTools.pens.basePen import BasePen
from fontTools.ttLib import TTFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import draw  # noqa: E402
import pixel  # noqa: E402
from family import CACHE, GRIDS, ROOT, STYLES, log, ps_name, redaction, variants  # noqa: E402
from glyphs import MODULES, enclosed, figures, ordinals, symbols  # noqa: E402
from glyphs.shapes import (  # noqa: E402
    CUT,
    SLIVER,
    _pieces,
    _regions,
    blend_text,
    content,
    embolden,
    glyph,
    masters,
    path,
    phased,
    pixelate_glyphs,
    shaper,
    slope,
    stem,
    union_paths,
)

OUT = ROOT / "temp" / "score"
CARVED = 20  # largest pixel that shows carving
NEAR = 40  # farthest a gap is from Redaction's to be the same
SPECK = 20  # least area of a gap, under which it is noise
SHORT = 2  # shortest length between points
KINK = (1, 10)  # degrees off smooth where curves meet, for a joint to be a kink
SPIKE = 165  # degrees a contour turns back at a point, for it to be a spike
TINY = 100  # least area of a contour of a smooth glyph
# Redaction's superscripts, and those drawn, in every font; Redaction's own:
# ¹ ² ³, and ⁴ ⁵ from its ¼ and ⅗
SUPERIORS = dict(figures.SUPERIORS)
OWN = {n for d, n in SUPERIORS.items() if n not in figures.DRAWN.values() or d in figures.OWN}
# Superscript letters, of ordinals and ℀ ℅: their glyphs
LETTERS = {c: n for c, n in sorted((figures.LETTERS | ordinals.LETTERS).items())}
# The fonts last approved (review.py): letters keep their carving, enclosed
# glyphs are scored against theirs
APPROVED = CACHE / "approved"
DEPTH = 0.1  # most a gap is longer or shorter than the one approved, of its length
WIDE = 0.9  # least a gap is as wide as the one approved
SHIFT = 16  # farthest letters are moved from centred alike onto those approved
BLUE, ORANGE, INK = (40, 90, 230), (255, 120, 30), (20, 20, 20)
PALE_BLUE, PALE_ORANGE, PALE = (170, 200, 255), (255, 205, 160), (200, 200, 200)


# Raster


class _Flat(BasePen):
    """Polygons of an outline, its curves cut into STEPS lines."""

    STEPS = 16

    def __init__(self):
        super().__init__(None)
        self.polygons = []

    def _moveTo(self, pt):
        self.polygons.append([pt])

    def _lineTo(self, pt):
        self.polygons[-1].append(pt)

    def _curveToOne(self, a, b, c):
        (x0, y0) = self._getCurrentPoint()
        for i in range(1, self.STEPS + 1):
            t = i / self.STEPS
            u = 1 - t
            self.polygons[-1].append(
                (
                    u**3 * x0 + 3 * u * u * t * a[0] + 3 * u * t * t * b[0] + t**3 * c[0],
                    u**3 * y0 + 3 * u * u * t * a[1] + 3 * u * t * t * b[1] + t**3 * c[1],
                )
            )

    def _qCurveToOne(self, a, b):
        (x0, y0) = self._getCurrentPoint()
        for i in range(1, self.STEPS + 1):
            t = i / self.STEPS
            u = 1 - t
            self.polygons[-1].append(
                (
                    u * u * x0 + 2 * u * t * a[0] + t * t * b[0],
                    u * u * y0 + 2 * u * t * a[1] + t * t * b[1],
                )
            )


def mask(p, frame):
    """The ink of `p` in `frame` (x0, y0, x1, y1), one pixel a unit, rows from
    the bottom: where the winding at the centre of a pixel is not 0."""
    x0, y0, x1, y1 = frame
    w, h = x1 - x0, y1 - y0
    pen = _Flat()
    p.draw(pen)
    edges = [
        np.hstack([np.array(poly), np.roll(np.array(poly), -1, 0)])
        for poly in pen.polygons
        if len(poly) > 1
    ]
    if not edges:
        return np.zeros((h, w), bool)
    ex0, ey0, ex1, ey1 = np.vstack(edges).T
    lo, hi = np.minimum(ey0, ey1), np.maximum(ey0, ey1)
    r0 = np.clip(np.ceil(lo - y0 - 0.5), 0, h).astype(int)
    r1 = np.clip(np.ceil(hi - y0 - 0.5), 0, h).astype(int)
    counts = r1 - r0
    keep = counts > 0
    ex0, ey0, ex1, ey1, r0, counts = (a[keep] for a in (ex0, ey0, ex1, ey1, r0, counts))
    edge = np.repeat(np.arange(len(counts)), counts)
    rows = r0[edge] + np.arange(counts.sum()) - np.repeat(np.cumsum(counts) - counts, counts)
    yc = y0 + rows + 0.5
    x = ex0[edge] + (yc - ey0[edge]) * (ex1[edge] - ex0[edge]) / (ey1[edge] - ey0[edge])
    cols = np.clip(np.ceil(x - x0 - 0.5), 0, w).astype(int)
    diff = np.zeros((h, w + 1), int)
    np.add.at(diff, (rows, cols), np.sign(ey1[edge] - ey0[edge]).astype(int))
    return np.cumsum(diff, axis=1)[:, :w] != 0


def _run_lengths(m):
    """For each pixel of `m`, the length of the run of ink along its row
    that it is in."""
    h, w = m.shape
    flat = np.hstack([m, np.zeros((h, 1), bool)]).ravel()
    d = np.diff(flat.astype(np.int8), prepend=0)
    starts, ends = np.flatnonzero(d == 1), np.flatnonzero(d == -1)
    out = np.zeros(flat.shape)
    lengths = ends - starts
    out[flat] = np.repeat(lengths, lengths)
    return out.reshape(h, w + 1)[:, :w]


def _sheared(m, sign):
    """`m` with row i moved i pixels along, so its diagonals are columns,
    and how to undo it."""
    h, w = m.shape
    out = np.zeros((h, w + h), bool)
    rows = np.arange(h)[:, None]
    cols = np.arange(w)[None, :] + (rows if sign > 0 else h - 1 - rows)
    out[np.broadcast_to(rows, (h, w)), cols] = m
    return out, (rows, cols)


def thickness(m):
    """The thickness of the stroke each pixel of ink is in: the shortest
    run of ink through it, along rows, columns and diagonals."""
    runs = [_run_lengths(m), _run_lengths(m.T).T]
    for sign in (1, -1):
        s, (rows, cols) = _sheared(m, sign)
        runs.append(_run_lengths(s.T).T[np.broadcast_to(rows, m.shape), cols] * math.sqrt(2))
    return np.min(runs, axis=0)[m]


# Measures


def strokes(m):
    t = thickness(m)
    if not len(t):
        return dict(thin=0, mid=0, thick=0, ink=0)
    thin, mid, thick = np.percentile(t, [10, 50, 90])
    return dict(thin=float(thin), mid=float(mid), thick=float(thick), ink=int(m.sum()))


def carved(p):
    """Redaction's carving in `p`, as glyphs/shapes.py finds it: what `p`
    emboldened by CUT and thinned back fills, but slivers and specks."""
    filled = pathops.op(embolden(embolden(p, CUT), -CUT), p, pathops.PathOp.DIFFERENCE)
    opened = embolden(embolden(filled, -SLIVER), SLIVER)
    out = pathops.Path()
    for c in pathops.op(opened, filled, pathops.PathOp.INTERSECTION).contours:
        if abs(c.area) >= SPECK:
            out.addPath(c)
    return out


def gaps(p, grid=None):
    """The carving of `p` (carved): [(x, y, length, width)], about where
    each gap is, how long and wide. On a `grid`, notches touching at a
    corner are one gap, as pixels are one stroke (shapes.cells)."""
    pieces = [[c] for c in carved(p).contours]
    if grid:
        joined = list(embolden(union_paths([c for [c] in pieces]), 1).contours)
        pieces = [[c for [c] in pieces if j.contains(c.points[0])] for j in joined]
    out = []
    for group in pieces:
        x0, y0 = min(c.bounds[0] for c in group), min(c.bounds[1] for c in group)
        x1, y1 = max(c.bounds[2] for c in group), max(c.bounds[3] for c in group)
        length = math.hypot(x1 - x0, y1 - y0)
        out.append(((x0 + x1) / 2, (y0 + y1) / 2, length, sum(abs(c.area) for c in group) / length))
    return out


def carving(drawn, theirs):
    """How far the gaps of `drawn` are from those of `theirs`: matched
    nearest first, each pair the mean of how much longer or shorter and
    wider or thinner, at most 1, a gap missing or extra 1, over how many
    `theirs` has."""
    pairs = _paired(drawn, theirs)
    total = 0
    for i, j in pairs:
        (_, _, lt, wt), (_, _, ld, wd) = theirs[i], drawn[j]
        total += min(1, (abs(ld - lt) / lt + abs(wd - wt) / wt) / 2)
    total += len(theirs) - len(pairs) + len(drawn) - len(pairs)
    return total / max(1, len(theirs))


def _paired(drawn, theirs):
    """The gaps of `drawn` and `theirs` matched nearest first, NEAR at most
    apart: [(i of theirs, j of drawn)]."""
    pairs = sorted(
        (math.hypot(a[0] - b[0], a[1] - b[1]), i, j)
        for i, a in enumerate(theirs)
        for j, b in enumerate(drawn)
    )
    used_t, used_d, out = set(), set(), []
    for dist, i, j in pairs:
        if dist > NEAR or i in used_t or j in used_d:
            continue
        used_t.add(i)
        used_d.add(j)
        out.append((i, j))
    return out


def _frame(*paths, pad=12):
    bounds = [p.bounds for p in paths if p.bounds != (0, 0, 0, 0)]
    return (
        math.floor(min(b[0] for b in bounds)) - pad,
        math.floor(min(b[1] for b in bounds)) - pad,
        math.ceil(max(b[2] for b in bounds)) + pad,
        math.ceil(max(b[3] for b in bounds)) + pad,
    )


def _centroid(m, frame):
    ys, xs = np.nonzero(m)
    return frame[0] + xs.mean() + 0.5, frame[1] + ys.mean() + 0.5


def _iou(a, b):
    return float((a & b).sum() / max(1, (a | b).sum()))


def compare(drawn, theirs, grid):
    """`drawn` against `theirs`, paths: its ink moved onto theirs (by whole
    pixels in a numbered variant, where it shares the most), and the scores
    of the docstring."""
    f = _frame(drawn, theirs)
    (dx, dy), (tx, ty) = _centroid(mask(drawn, f), f), _centroid(mask(theirs, f), f)
    g = grid or 1
    drawn = drawn.transform(1, 0, 0, 1, pixel.snap(tx - dx, g), pixel.snap(ty - dy, g))
    if grid:  # a pixel either way can be nearer: the one most ink is shared at
        f = _frame(drawn, theirs, pad=grid + 12)
        mt = mask(theirs, f)
        shifts = [(x * grid, y * grid) for x in (-1, 0, 1) for y in (-1, 0, 1)]
        drawn = max(
            (drawn.transform(1, 0, 0, 1, x, y) for x, y in shifts),
            key=lambda p: _iou(mask(p, f), mt),
        )
    f = _frame(drawn, theirs)
    md, mt = mask(drawn, f), mask(theirs, f)
    sd, st = strokes(md), strokes(mt)
    ratio = {k: sd[k] / st[k] if st[k] else 0 for k in ("thin", "mid", "thick", "ink")}
    shows = not grid or grid <= CARVED
    carve = carving(gaps(drawn), gaps(theirs)) if shows else 0
    iou = _iou(md, mt)
    loss = (
        (1 - iou)
        + abs(ratio["mid"] - 1)
        + (abs(ratio["thin"] - 1) + abs(ratio["thick"] - 1)) / 2
        + carve / 2
    )
    scores = dict(iou=iou, **ratio, carving=carve, loss=loss)
    if shows:
        cuts = (mask(carved(drawn), f), mask(carved(theirs), f))
    else:
        cuts = (np.zeros_like(md), np.zeros_like(mt))
    return {k: round(v, 3) for k, v in scores.items()}, (md, mt, f, drawn, *cuts)


def hygiene(g, grid):
    """What is not clean in a TrueType glyph's outline: points too close
    (SHORT), on-curve points on a straight line, spikes (SPIKE), kinks
    where curves meet (KINK), tiny contours (TINY); in a numbered variant,
    points off the grid and lines neither straight across nor up."""
    if g.isComposite() or not g.numberOfContours:
        return None
    coords, ends, flags = g.getCoordinates(None)
    out = dict(points=len(coords), contours=len(ends))
    out.update(dict.fromkeys(("short", "straight", "spikes", "kinks", "tiny"), 0))
    if grid:
        out.update(offgrid=0, slanted=0)
    start = 0
    for end in ends:
        pts = [tuple(map(float, p)) for p in coords[start : end + 1]]
        on = [bool(f & 1) for f in flags[start : end + 1]]
        start = end + 1
        n = len(pts)
        area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(pts, pts[1:] + pts[:1])) / 2
        if not grid and abs(area) < TINY:
            out["tiny"] += 1
        for i in range(n):
            a, b, c = pts[i - 1], pts[i], pts[(i + 1) % n]
            if math.dist(a, b) < SHORT:
                out["short"] += 1
            if grid:
                out["offgrid"] += any(v % grid for v in b)
                out["slanted"] += a[0] != b[0] and a[1] != b[1]
            if not on[i] or math.dist(a, b) < SHORT or math.dist(b, c) < SHORT:
                continue
            u = (b[0] - a[0], b[1] - a[1])
            v = (c[0] - b[0], c[1] - b[1])
            turn = math.degrees(math.atan2(u[0] * v[1] - u[1] * v[0], u[0] * v[0] + u[1] * v[1]))
            if abs(turn) > SPIKE:
                out["spikes"] += 1
            elif on[i - 1] and on[(i + 1) % n] and abs(turn) < KINK[0]:
                out["straight"] += 1
            elif (not on[i - 1] or not on[(i + 1) % n]) and KINK[0] <= abs(turn) < KINK[1]:
                out["kinks"] += 1
    return out


# Glyphs drawn again


def _trademark(font, smooth):
    """The T and M of ™ in `font`, cut apart along the slant halfway between
    them in `smooth`, where they are apart: pixelated, they can touch."""
    t, m = sorted(path(smooth, "™").contours, key=lambda c: c.bounds[0])
    run = slope(smooth)

    def across(c):  # where its points are across the slant
        return [x - y * run for x, y in c.points]

    cut = (max(across(t)) + min(across(m))) / 2
    p = path(font, "™")
    x0, y0, x1, y1 = p.bounds
    y0, y1 = y0 - 1, y1 + 1
    left = pathops.Path()
    left.moveTo(x0 - 1 - abs(run) * y1, y0)
    for pt in ((cut + y0 * run, y0), (cut + y1 * run, y1), (x0 - 1 - abs(run) * y1, y1)):
        left.lineTo(*pt)
    left.close()
    return [
        pathops.op(p, left, pathops.PathOp.INTERSECTION),
        pathops.op(p, left, pathops.PathOp.DIFFERENCE),
    ], t


def _denominator(p, smooth):
    """The figure under the slash of a fraction of Redaction's: the contours
    below the bottom of ¹, but the slash, the tallest."""
    contours = sorted(p.contours, key=lambda c: c.bounds[3] - c.bounds[1])
    contours.pop()
    low = path(smooth, "¹").bounds[1] / 2
    q = pathops.Path()
    for c in contours:
        if c.bounds[1] < low:
            q.addPath(c)
    return q


def references(grid, style):
    """{name: (Redaction's, drawn again)}, paths."""
    font, smooth = redaction(grid, style), redaction(None, style)
    out = {}
    for char, own in (("1", "¹"), ("2", "²"), ("3", "³")):
        out[own] = (path(font, own), figures._superior(smooth, char, own=False))
    if not grid:  # pixelated, the pieces of a fraction can be one
        for char, frac in (("4", "¼"), ("5", "⅗")):
            out[f"{char} of {frac}"] = (
                _denominator(path(font, frac), smooth),
                figures._superior(smooth, char, own=False),
            )
    # The T and M of ™: shrunk as tall as its T, on its rows on a grid as ℡ is
    # on those of z, their stems as thick as its T's
    tm, smooth_t = _trademark(font, smooth)
    bottom, top = tm[0].bounds[1], tm[0].bounds[3]
    scale = (top - bottom) / smooth["OS/2"].sCapHeight
    target = stem(smooth_t)
    for char, theirs in zip("TM", tm):
        drawn = symbols.small_caps(smooth, char, scale, target)
        out[f"{char} of ™"] = (theirs, glyph(drawn.transform(1, 0, 0, 1, 0, bottom)))
    if grid:  # figures and small caps where in a cell they fall best, as drawn ones are
        digits = {f"g{i}": out[n][1] for i, n in enumerate(out) if n in ("¹", "²", "³")}
        caps = {f"g{i}": out[n][1] for i, n in enumerate(out) if n.endswith("™")}
        others = {f"g{i}": out[n][1] for i, n in enumerate(out)}
        others = {k: g for k, g in others.items() if k not in digits | caps}
        mark = font["glyf"][font.getBestCmap()[ord("™")]]
        mark.recalcBounds(font["glyf"])
        pixelated = (
            figures.pixelated(font, digits, grid)
            | phased(caps, grid, (mark.yMin, mark.yMax), [mark])
            | pixelate_glyphs(others, grid)
        )
        out = {n: (out[n][0], pixelated[f"g{i}"]) for i, n in enumerate(out)}
    return out


def _path(g):
    p = pathops.Path()
    g.draw(pathops.PathPen(p), None)
    return p


def score_font(task):
    grid, style = task
    redrawn = {}
    pictures = {}
    for name, (theirs, drawn) in references(grid, style).items():
        scores, picture = compare(_path(drawn), theirs, grid)
        scores["hygiene"] = hygiene(drawn, grid)
        redrawn[name] = scores
        pictures[name] = picture
    font = TTFont(draw.path(grid, style))
    glyf = font["glyf"]
    own = [strokes(_raster(glyf, n)) for n in ("onesuperior", "twosuperior", "threesuperior")]
    mean = {k: sum(s[k] for s in own) / len(own) for k in own[0]}
    superiors = {}
    for d, name in SUPERIORS.items():
        s = strokes(_raster(glyf, name))
        superiors[d] = {k: round(s[k] / mean[k], 3) for k in ("thin", "mid", "thick")}
        superiors[d]["hygiene"] = hygiene(glyf[name], grid)
    drawn_names = {n for m in MODULES for n in [*m.CODEPOINTS.values(), *m.ALTERNATES]}
    clean = {}
    for n in sorted(drawn_names & set(font.getGlyphOrder())):
        h = hygiene(glyf[n], grid)
        if h:
            clean[n] = h
    # Redaction's own, as the measure of clean
    theirs = redaction(grid, style)
    baseline = [hygiene(theirs["glyf"][n], grid) for n in theirs.getGlyphOrder()]
    baseline = [h for h in baseline if h]
    base = {k: round(sum(h[k] for h in baseline) / len(baseline), 3) for k in baseline[0]}
    sheets = (_sheet(pictures, redrawn, grid), _superior_strip(glyf, grid))
    boxed = enclosed_glyphs(draw.path(grid, style), grid, style)
    boxes = dict(glyphs=boxed, summary=enclosed_summary(boxed))
    approved = APPROVED / draw.path(grid, style).name
    if approved.exists():
        boxes["approved"] = enclosed_summary(enclosed_glyphs(approved, grid, style))
    return (
        ps_name(grid, style),
        dict(
            redrawn=redrawn,
            superiors=superiors,
            letters=letters(font, grid, style),
            hygiene=clean,
            redaction=base,
            enclosed=boxes,
        ),
        sheets,
    )


def letters(font, grid, style):
    """The superscript letters of `font` against MCKL's ¹ ² ³, Redaction's
    letters and the fonts approved, as the docstring says."""
    glyf, cmap = font["glyf"], font.getBestCmap()
    measured = {}

    def measure(name):
        if name not in measured:
            measured[name] = strokes(_raster(glyf, name))
        return measured[name]

    def mean(names):
        return {k: np.mean([measure(n)[k] for n in names]) for k in ("thin", "mid", "thick")}

    def contrast(s):
        return s["thin"] / s["thick"]

    one, own = measure("onesuperior"), mean(["onesuperior", "twosuperior", "threesuperior"])
    big = {c: cmap[ord(c)] for c in LETTERS}
    mckl = contrast(own) / contrast(mean([cmap[ord(d)] for d in "123"]))

    def scores(small, large):
        return dict(
            stem=small["mid"] / one["mid"],
            hairline=small["thin"] / own["thin"],
            contrast=contrast(small) / contrast(large),
        )

    each = {c: scores(measure(n), measure(big[c])) for c, n in LETTERS.items()}
    whole = scores(mean(LETTERS.values()), mean(big.values()))
    targets = dict(stem=1, hairline=1, contrast=mckl)
    out = {k: dict(mean=round(whole[k], 3)) | _summary(each, k, t) for k, t in targets.items()}
    out["contrast"]["mckl"] = round(mckl, 3)

    bounds = {}
    for name in ("onesuperior", LETTERS["n"], cmap[ord("1")], cmap[ord("n")]):
        glyf[name].recalcBounds(glyf)
        bounds[name] = glyf[name].yMin, glyf[name].yMax
    height = {n: b[1] - b[0] for n, b in bounds.items()}
    out["x-height"] = dict(
        top=bounds[LETTERS["n"]][1] - bounds["onesuperior"][1],
        size=round(
            height[LETTERS["n"]]
            / height["onesuperior"]
            / (height[cmap[ord("n")]] / height[cmap[ord("1")]]),
            3,
        ),
    )

    approved = APPROVED / f"{ps_name(grid, style)}.ttf"
    if (not grid or grid <= CARVED) and approved.exists():
        theirs = TTFont(approved)["glyf"]
        carvings = {c: _kept(_path(glyf[n]), _path(theirs[n]), grid) for c, n in LETTERS.items()}
        total = {
            k: sum(v[k] for v in carvings.values())
            for k in ("approved", "kept", "missing", "extra")
        }
        depths = [d for v in carvings.values() for d in v["depth"]]
        widths = [w for v in carvings.values() for w in v["width"]]
        worst = min(
            carvings,
            key=lambda c: carvings[c]["kept"] - carvings[c]["approved"] - carvings[c]["extra"],
        )
        out["carving"] = dict(
            total,
            depth=[round(min(depths), 3), round(max(depths), 3)] if depths else None,
            width=round(min(widths), 3) if widths else None,
            worst=worst,
            letters=carvings,
        )

    clean = {c: hygiene(glyf[n], grid) for c, n in LETTERS.items()}
    issues = {
        c: sum(v for k, v in h.items() if k not in ("points", "contours")) for c, h in clean.items()
    }
    worst = max(issues, key=issues.get)
    out["hygiene"] = dict(
        mean=round(sum(issues.values()) / len(issues), 3), worst=worst, issues=issues[worst]
    )
    out["letters"] = {c: {k: round(v, 3) for k, v in s.items()} for c, s in each.items()}
    return out


def _summary(each, key, target):
    """The letter of `each` farthest from `target` by `key`, and by how much."""
    worst = max(each, key=lambda c: abs(each[c][key] - target))
    return dict(worst=worst, of=round(each[worst][key], 3))


def _safe_gaps(p, grid):
    """gaps(p, grid): pathops fails on a few outlines where they sit, moved
    a unit it does not."""
    for dx in (0, 1, -1, 2):
        try:
            return [
                (x - dx, y, length, width)
                for x, y, length, width in gaps(p.transform(1, 0, 0, 1, dx, 0), grid)
            ]
        except pathops.PathOpsError:
            continue
    raise ValueError("pathops fails on these gaps")


def _onto(drawn, theirs, grid, reach=SHIFT):
    """`drawn` moved where it shares the most ink with `theirs`: centred
    alike, then up to `reach` either way (a pixel in a numbered variant).
    Grown otherwise, their ink does not centre alike."""
    g = grid or 1
    f = _frame(drawn, theirs, pad=reach + g + 12)
    (dx, dy), (tx, ty) = _centroid(mask(drawn, f), f), _centroid(mask(theirs, f), f)
    drawn = drawn.transform(1, 0, 0, 1, pixel.snap(tx - dx, g), pixel.snap(ty - dy, g))
    md, mt = mask(drawn, f), mask(theirs, f)
    steps = range(-reach, reach + 1, 2) if not grid else (-grid, 0, grid)
    x, y = max(
        ((x, y) for x in steps for y in steps),
        key=lambda s: (_iou(np.roll(md, (s[1], s[0]), (0, 1)), mt), -abs(s[0]) - abs(s[1])),
    )
    return drawn.transform(1, 0, 0, 1, x, y)


def _kept(drawn, theirs, grid):
    """The gaps of `drawn` matched one to one with those of `theirs`, the
    glyph approved, moved onto it (_onto), as carving() does: how many
    `theirs` has, kept (DEPTH, WIDE), missing and extra, and the length and
    width of each matched over theirs."""
    drawn = _onto(drawn, theirs, grid)
    mine, approved = _safe_gaps(drawn, grid), _safe_gaps(theirs, grid)
    pairs = sorted(
        (math.hypot(a[0] - b[0], a[1] - b[1]), i, j)
        for i, a in enumerate(approved)
        for j, b in enumerate(mine)
    )
    used_t, used_d, depth, width = set(), set(), [], []
    for dist, i, j in pairs:
        if dist > NEAR or i in used_t or j in used_d:
            continue
        used_t.add(i)
        used_d.add(j)
        depth.append(mine[j][2] / approved[i][2])
        width.append(mine[j][3] / approved[i][3])
    kept = sum(abs(d - 1) <= DEPTH and w >= WIDE for d, w in zip(depth, width))
    return dict(
        approved=len(approved),
        kept=kept,
        missing=len(approved) - len(used_t),
        extra=len(mine) - len(used_d),
        depth=[round(d, 3) for d in depth],
        width=[round(w, 3) for w in width],
    )


def _raster(glyf, name):
    p = pathops.Path()
    glyf[name].draw(pathops.PathPen(p), glyf)
    return mask(p, _frame(p))


# Enclosed glyphs


def _content(p, frame, kind):
    """The content of enclosed glyph `p` of `kind`, `frame` its enclosure
    alone (on a grid, pixelated): what it has but its enclosure, or, cut
    out of a disc or a block, what its enclosure has but it."""
    if kind in ("disc", "block"):
        return pathops.op(frame, p, pathops.PathOp.DIFFERENCE)
    return pathops.op(p, frame, pathops.PathOp.DIFFERENCE)


def _thickness(p, grid):
    """The thickness of the strokes of `p` at each pixel of its ink (units):
    on a grid, a pixel a cell."""
    g = grid or 1
    q = p.transform(1 / g, 0, 0, 1 / g, 0, 0)
    return thickness(mask(q, _frame(q, pad=2))) * g


def _percentiles(t):
    thin, mid, thick = np.percentile(t, [10, 50, 90]) if len(t) else (0, 0, 0)
    return float(thin), float(mid), float(thick)


def _apart(g, frame, kind, grid):
    """Whether the content of pixel glyph `g` touches its enclosure `frame`
    (pixelated alone), at an edge or a corner, how many pieces it is in,
    joined at a corner too, and how many counters it has: white closed by
    its pixels, joined at a corner too, wider than carving (CUT), which
    closes into a cell or two on a fine grid."""
    p, f = (
        _path(g).transform(1 / grid, 0, 0, 1 / grid, 0, 0),
        frame.transform(1 / grid, 0, 0, 1 / grid, 0, 0),
    )
    box = _frame(p, f, pad=2)
    ink, around = mask(p, box), mask(f, box)
    negative = kind in ("disc", "block")
    content = around & ~ink if negative else ink & ~around
    near = content.copy()
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            near |= np.roll(np.roll(content, di, 0), dj, 1)
    touch = (near & ~around).any() if negative else (near & around).any()
    edges = ((0, 1), (1, 0), (0, -1), (-1, 0))
    holes = _regions(np.pad(content, 1), False, edges)[1:]  # the first is the air around
    corners = edges + ((1, 1), (1, -1), (-1, 1), (-1, -1))
    return (
        bool(touch),
        len(_regions(content, True, corners)),
        sum(len(h) * grid * grid > (2 * CUT) ** 2 for h in holes),
    )


def _small_caps(font, smooth, grid):
    """{capital: path} as the small caps of ℡ ℻ (symbols.small_caps), as tall
    as z of `font`, on a grid where in a cell they fall best, on its rows."""
    glyf, cmap = font["glyf"], font.getBestCmap()
    z, n = glyf[cmap[ord("z")]], glyf[cmap[ord("n")]]
    z.recalcBounds(glyf)
    scale = z.yMax / smooth["OS/2"].sCapHeight
    target = stem(path(smooth, "n"))
    regular, bold = masters()
    grow = stem(path(bold, "I")) - stem(path(regular, "I"))
    t = (target / scale - stem(path(smooth, "I"))) / grow
    caps = {}
    for c in enclosed.UPPER:
        p = blend_text(smooth, c, t, "I")
        caps[c] = glyph(p.transform(scale, 0, 0, scale, -p.bounds[0] * scale, 0))
    if grid:
        caps = phased(caps, grid, (z.yMin, z.yMax), [n])
    return {c: _path(g) for c, g in caps.items()}


def _plain(smooth, text, drawn, grid):
    """`text` of Redaction as typed (the style's, or Italic's for 🄫 🄬), as
    big as `drawn` and where it is, a glyph's outline: on a grid, pixelated."""
    p = content(smooth, shaper(smooth), text)
    (x0, y0, x1, y1), (a0, b0, a1, b1) = p.bounds, drawn.bounds
    s = (b1 - b0) / (y1 - y0)
    p = p.transform(s, 0, 0, s, (a0 + a1 - s * (x0 + x1)) / 2, (b0 + b1 - s * (y0 + y1)) / 2)
    if grid:
        return _path(pixelate_glyphs({"p": glyph(p)}, grid)["p"])
    return _path(glyph(p))  # on whole units, as the drawing is


def enclosed_glyphs(file, grid, style):
    """{glyph name: scores} of the enclosed glyphs of digits and capitals
    (enclosed.blends) in the font at `file`, against the base font drawn
    (for its pieces and counters) and n, superscripts and small caps of
    ℡ ℻ in it:
    - stem, hair: the thick and thin of its content (90th and 10th
      percentiles of thickness), over those of n
    - contrast: thick over thin, over that of the superscripts of its
      digits, the small caps of its capitals, or the superscript letters
      of its lowercase (all of them, for letters there is none of), set
      alike: 1 when the same
    - carving: its carving against Redaction's own as typed at its size
      (carving), where a pixel shows it (CARVED); kept: how many of
      Redaction's gaps it has, of how many
    - on a grid, touch: 1 where its content touches its enclosure, at an
      edge or a corner; pieces, counters: 1 where its content has as many
      as drawn smooth
    - hygiene, of the whole glyph"""
    font, base = TTFont(file), TTFont(draw.path(None, style))
    smooth = redaction(None, style)
    italic = redaction(None, "Italic")
    glyf, names = font["glyf"], {}
    for kind, contents, _, slanted in enclosed.ENCLOSURES:
        for cp, text in contents.items():
            if enclosed.blends(text) and kind != "crossed":  # its diagonals cut its block apart
                names[enclosed.CODEPOINTS[cp]] = (kind, text, slanted)
    n = _percentiles(_thickness(_path(glyf[font.getBestCmap()[ord("n")]]), grid))
    sups = {d: _thickness(_path(glyf[name]), grid) for d, name in SUPERIORS.items()}
    caps = {c: _thickness(p, grid) for c, p in _small_caps(font, smooth, grid).items()}
    # Lowercase against the superscript letters, those it has none of against all
    letters = {c: _thickness(_path(glyf[name]), grid) for c, name in LETTERS.items()}
    lower = np.concatenate(list(letters.values()))
    frames = {kind: glyph(enclosed.enclosure(smooth, grid, kind)) for kind, *_ in names.values()}
    smooth_frames = {kind: _path(glyph(enclosed.enclosure(smooth, None, kind))) for kind in frames}
    if grid:
        frames = pixelate_glyphs(frames, grid)
    frames = {kind: _path(g) for kind, g in frames.items()}
    shows = not grid or grid <= CARVED
    out = {}
    for name, (kind, text, slanted) in names.items():
        p = _content(_path(glyf[name]), frames[kind], kind)
        if p.bounds == (0, 0, 0, 0):  # gone into its enclosure
            out[name] = dict(touch=1, pieces=0, counters=0, hygiene=hygiene(glyf[name], grid))
            continue
        thin, _, thick = _percentiles(_thickness(p, grid))
        refs = [
            sups.get(c) if c.isdigit() else letters.get(c, lower) if c.islower() else caps.get(c)
            for c in text
        ]
        ref_thin, _, ref_thick = _percentiles(np.concatenate([r for r in refs if r is not None]))
        scores = dict(
            stem=thick / n[2],
            hair=thin / n[0],
            contrast=(thick / thin) / (ref_thick / ref_thin) if thin and ref_thin else 0,
        )
        if grid:
            drawn = _content(_path(base["glyf"][name]), smooth_frames[kind], kind)
            touch, pieces, counters = _apart(glyf[name], frames[kind], kind, grid)
            scores.update(
                touch=touch,
                pieces=pieces == _pieces(drawn)[0],
                counters=counters == _pieces(drawn)[1],
            )
        if shows:
            try:
                theirs = _safe_gaps(_plain(italic if slanted else smooth, text, p, grid), None)
                drawn = _safe_gaps(p, None)
            except ValueError:  # pathops fails on it wherever it sits: unmeasured
                scores["unmeasured"] = 1
            else:
                scores.update(carving=carving(drawn, theirs), kept=len(_paired(drawn, theirs)))
                scores["gaps"] = len(theirs)
        out[name] = {k: round(v, 3) for k, v in scores.items()}
        out[name]["hygiene"] = hygiene(glyf[name], grid)
    return out


def _group(text):
    """Which group of enclosed glyphs `text` is in."""
    if text.isdigit():
        return "digit" if len(text) == 1 else "number"
    if len(text) == 1:
        return "lowercase" if text.islower() else "capital"
    return "word"


def enclosed_summary(glyphs):
    """{group: {measure: mean, worst: (glyph name, its value)}} of
    enclosed_glyphs(): worst the farthest from 1 (stem, hair, contrast),
    from 0 (carving); touch, pieces and counters: which glyphs touch their
    enclosure, or lose or gain a piece or a counter."""
    texts = {
        enclosed.CODEPOINTS[cp]: text
        for _, contents, _, _ in enclosed.ENCLOSURES
        for cp, text in contents.items()
    }
    out = {}
    for group in ("digit", "number", "capital", "lowercase", "word"):
        members = {n: s for n, s in glyphs.items() if _group(texts[n]) == group}
        if not members:
            continue
        summary = {}
        for k in ("stem", "hair", "contrast", "carving"):
            values = {n: s[k] for n, s in members.items() if k in s}
            if not values:
                continue
            far = (lambda v: v) if k == "carving" else (lambda v: abs(v - 1))
            worst = max(values, key=lambda n: far(values[n]))
            summary[k] = dict(
                mean=round(sum(values.values()) / len(values), 3), worst=[worst, values[worst]]
            )
        summary["unmeasured"] = [n for n, s in members.items() if s.get("unmeasured")]
        if any("gaps" in s for s in members.values()):
            summary["kept"] = [
                sum(s.get("kept", 0) for s in members.values()),
                sum(s.get("gaps", 0) for s in members.values()),
            ]
        if any("touch" in s for s in members.values()):
            summary["touch"] = [n for n, s in members.items() if s["touch"]]
            summary["pieces"] = [n for n, s in members.items() if not s["pieces"]]
            summary["counters"] = [n for n, s in members.items() if not s["counters"]]
        clean = [s["hygiene"] for s in members.values() if s["hygiene"]]
        summary["hygiene"] = {k: sum(h[k] for h in clean) for k in clean[0] if k != "contours"}
        summary["count"] = len(members)
        out[group] = summary
    return out


# Pictures


def _cell(md, mt, frame, drawn, cd, ct, grid, size):
    img = np.full(md.shape + (3,), 255, np.uint8)
    img[ct] = PALE_BLUE  # carving, Redaction's and the drawing's
    img[cd] = PALE_ORANGE
    img[cd & ct] = PALE
    img[mt & ~md] = BLUE
    img[md & ~mt] = ORANGE
    img[md & mt] = INK
    if not grid:
        g = glyph(drawn)
        coords, _, flags = g.getCoordinates(None)
        for (x, y), f in zip(coords, flags):
            cx, cy = int(x - frame[0]), int(y - frame[1])
            colour = (0, 170, 60) if f & 1 else (150, 150, 150)
            img[max(0, cy - 2) : cy + 3, max(0, cx - 2) : cx + 3] = colour
    img = img[::-1]
    h, w = img.shape[:2]
    out = np.full((size, size, 3), 255, np.uint8)
    out[: min(h, size), : min(w, size)] = img[:size, :size]
    return out


def _sheet(pictures, scores, grid, size=560):
    """A row of the glyphs drawn again over Redaction's, with their loss as
    a bar under each: a tenth of the cell for each 0.1."""
    cells = []
    for name, picture in pictures.items():
        cell = _cell(*picture, grid, size)
        bar = np.full((24, size, 3), 255, np.uint8)
        bar[6:18, : min(size, int(scores[name]["loss"] * size))] = ORANGE
        cells.append(np.vstack([cell, bar]))
    return cells


def _superior_strip(glyf, grid, height=460):
    """⁰ to ⁹ as built, side by side: Redaction's own (OWN) blue, drawn
    black."""
    parts = []
    for name in SUPERIORS.values():
        p = pathops.Path()
        glyf[name].draw(pathops.PathPen(p), glyf)
        f = (math.floor(p.bounds[0]) - 20, 280, math.ceil(p.bounds[2]) + 20, 280 + height)
        m = mask(p, f)[::-1]
        img = np.full(m.shape + (3,), 255, np.uint8)
        img[m] = BLUE if name in OWN else INK
        parts.append(img)
    return np.hstack(parts)


def png(file, img):
    h, w, _ = img.shape
    raw = b"".join(b"\0" + img[y].tobytes() for y in range(h))

    def chunk(kind, data):
        crc = struct.pack(">I", zlib.crc32(kind + data))
        return struct.pack(">I", len(data)) + kind + data + crc

    file.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 6))
        + chunk(b"IEND", b"")
    )


def _stack(rows, gap=16):
    width = max(r.shape[1] for r in rows)
    out = []
    for r in rows:
        pad = np.full((r.shape[0], width - r.shape[1], 3), 255, np.uint8)
        out += [np.hstack([r, pad]), np.full((gap, width, 3), 210, np.uint8)]
    return np.vstack(out[:-1])


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--variants", default="base," + ",".join(map(str, GRIDS)))
    ap.add_argument("--styles", default=",".join(STYLES))
    ap.add_argument("--no-draw", action="store_true", help="score the fonts drawn already")
    args = ap.parse_args()
    grids, styles = variants(args.variants), args.styles.split(",")
    if not args.no_draw:
        draw.draw_all(grids, styles)
    OUT.mkdir(parents=True, exist_ok=True)
    tasks = [(g, s) for s in styles for g in grids]
    with ProcessPoolExecutor() as ex:
        results = list(ex.map(score_font, tasks))
    report = {name: r for name, r, _ in results}
    (OUT / "score.json").write_text(json.dumps(report, ensure_ascii=False, indent="\t"))
    smooth = [cells for (g, _), (_, _, (cells, _)) in zip(tasks, results) if g is None]
    if smooth:
        big = _stack([np.hstack(cells) for cells in smooth])
        png(OUT / "redrawn-base.png", big.repeat(2, axis=0).repeat(2, axis=1))
    for style in styles:
        rows = [s for (g, st), (_, _, s) in zip(tasks, results) if st == style]
        png(OUT / f"redrawn-{style}.png", _stack([np.hstack(cells) for cells, _ in rows]))
        png(OUT / f"superiors-{style}.png", _stack([strip for _, strip in rows]))

    names = list(next(iter(report.values()))["redrawn"])
    print(f"{'loss':<16}" + "".join(f"{n:>9}" for n in names) + f"{'mean':>9}")
    for name, r in report.items():
        losses = [r["redrawn"][n]["loss"] if n in r["redrawn"] else None for n in names]
        known = [v for v in losses if v is not None]
        print(
            f"{name:<16}"
            + "".join(f"{v:>9.3f}" if v is not None else f"{'':>9}" for v in losses)
            + f"{sum(known) / len(known):>9.3f}"
        )
    print(_letters_table(report))
    _print_enclosed(report)
    log(f"{OUT.relative_to(ROOT)}: score.json, redrawn-*.png, superiors-<style>.png")


def _print_enclosed(report):
    """The enclosed summaries, each group a row: approved, then drawn."""
    print(
        f"\n{'enclosed':<22}{'stem':>12}{'hair':>12}{'contrast':>12}{'carving':>12}"
        f"{'kept':>14}{'touch':>9}{'pieces':>9}{'counters':>10}{'points':>12}{'kinks':>11}"
        f"{'short':>9}"
    )
    for name, r in report.items():
        now, was = r["enclosed"]["summary"], r["enclosed"].get("approved", {})
        for group, s in now.items():
            w = was.get(group, {})

            def pair(k, w=w, s=s):
                a, b = (x[k]["mean"] if k in x else None for x in (w, s))
                return f"{'' if a is None else f'{a:.2f}'}>{'' if b is None else f'{b:.2f}'}"

            def ratio(x):
                return f"{x['kept'][0]}/{x['kept'][1]}" if "kept" in x else ""

            def many(k, w=w, s=s):
                return f"{len(w[k]) if k in w else ''}>{len(s[k]) if k in s else ''}"

            def count(k, w=w, s=s):
                return f"{w.get('hygiene', {}).get(k, '')}>{s['hygiene'][k]}"

            print(
                f"{name + ' ' + group:<22}"
                + "".join(f"{pair(k):>12}" for k in ("stem", "hair", "contrast", "carving"))
                + f"{ratio(w) + '>' + ratio(s):>14}{many('touch'):>9}{many('pieces'):>9}"
                + f"{many('counters'):>10}"
                + f"{count('points'):>12}{count('kinks'):>11}{count('short'):>9}"
            )


def _letters_table(report):
    """The letters of each font: each measure as a set, and its worst letter."""
    rows = [
        f"{'letters':<16}{'stem':>13}{'hairline':>13}{'contrast':>13}{'mckl':>6}"
        f"{'top':>5}{'size':>6}{'carving kept':>14}{'depth':>12}{'width':>7}{'hygiene':>10}"
    ]
    for name, r in report.items():
        lt = r["letters"]
        row = f"{name:<16}"
        for k in ("stem", "hairline", "contrast"):
            row += f"{lt[k]['mean']:>7.2f} {lt[k]['worst']} {lt[k]['of']:.2f}"
        x = lt["x-height"]
        row += f"{lt['contrast']['mckl']:>6.2f}{x['top']:>5}{x['size']:>6.2f}"
        c = lt.get("carving")
        if c:
            kept = f"{c['kept']}/{c['approved']} -{c['missing']} +{c['extra']}"
            depth = "{:.2f}-{:.2f}".format(*c["depth"]) if c["depth"] else ""
            row += f"{kept:>14}{depth:>12}{c['width'] or 0:>7.2f}"
        else:
            row += f"{'':>33}"
        h = lt["hygiene"]
        row += f"{h['mean']:>6.1f} {h['worst']} {h['issues']}"
        rows.append(row)
    return "\n".join(rows)


if __name__ == "__main__":
    main()
