"""Figures drawn from Redaction's own: superscript and subscript digits,
numerators and denominators, and vulgar fractions: ⁰ ⁴ ⁹, ₀ ₂, ⅓ ⅔ ⅛ ⅒
↉ ⅟ ℀ ℅, and the features for them.

Redaction has ¹ ² ³, and ¼ ½ ¾ ⅗ made of them, its fraction slash, and the
same digits on the baseline: 2, and 4 and 5, which are raised for ⁴ ⁵. The
others (0, 6 to 9) are drawn to match: Redaction's digits made heavier as
its Bold is of its Regular (shapes.blend), so their stems match those of ¹
shrunk to its height, on its baseline, hairlines and carving as MCKL's
own. Fractions are made of them (components): numerators, and
denominators, superscripts on the baseline as in ½.

Subscripts are superscripts (components) below the baseline, a third of
their height down, and denominators on it, as in ½. Superscript letters, for
℀ ℅ and the ordinals (ordinals.py), are Redaction's shrunk as the digits,
their x-height at the top of ¹: in Regular, Bold's thinned; in Italic and
Bold, made heavier as Bold is of Regular where their outlines match, else
grown across only, their carving cut again.

`frac` (font-variant-numeric: diagonal-fractions) sets any fraction of
digits from the same parts, 1/2 as 11/12 and 489/603, and sets them where
the fractions drawn set them (_Parts, the one model of both): n1/3n is n⅓n,
side bearings and advance included, and 1/10 is ⅒. Its parts are glyphs of
their own (.numr.frac, .dnom.frac), set by kerning pairs of their own, in
GPOS, which `kern` shares (the same lookups, which apply once): a place
between two parts depends on those two only. Its digits are as far apart as
¹ ² ³ are set (each with its own side bearings, as superiors() gives
them), but no nearer than MCKL sets any two of them, a cell at
least on a grid, where pixels touching at a corner read as one, and a cell
exactly on 50 to 100 where their outlines allow it; parts as far from the
slash as in ½, but no nearer than MCKL sets any part of ½ ¼ ¾ ⅗, a cell at
least on a grid. A fraction holds its ink, the slash's too, ending as far
past it as ½ past its own, and keeps clear of every glyph of the merged
font before and after it, kanji and kana too: no nearer what is before it
than the full-size digit would be (T1/2, f1/2, (1/2), touching nothing, a
cell apart on a grid (_beside, once the font is merged). In fractions only: superscripts (x²) and
subscripts keep their own spacing. MCKL's ½ ¼ ¾ ⅗ are not swapped in for
1/2, nor redrawn: on a grid he drew them otherwise (the 4 of ¼ is not ⁴),
and 1/4 would not match 11/14 beside it. In vertical text they are, as are
Kuronuri's: a fraction there is a glyph for is that glyph, any other is set
as typed (_frac).

What is a fraction: digits, a slash, digits, the run not next to another
slash, / and ⁄ alike. So 1 1/2 keeps its integer, 1.5/2 its 1, and a run of
two slashes or more stays as typed, digits and slashes: 2024/05/06, 3/4/5,
1/2⁄3, and x.com/1/2, /1/2 and 1/2/ in paths, which no reader takes for
fractions. As many digits as there are, before the slash as after it. ⁄
typed between digits is the shaper's too: HarfBuzz turns `frac` on around
it, and `numr` before it and `dnom` after it, which `frac` undoes in a run
as typed. `frac` comes first: in a fraction, its digits are numerators and
denominators whatever else is on, and `tnum`, `sups`, `subs`, `sinf` and
`ordn` apply around it (1 1/2 with `tnum`, its 1 tabular).

On 50, 70 and 100, Italic's fraction slash broke into pieces, two cells on
100, and upright, MCKL's has rows of air: it is drawn by hand there
(drawn/figures.txt), one stroke a cell a row.

`sups` gives the digits Redaction lacks, `numr` all of them as glyphs of its
own, drawn as the superscripts. `subs` and `sinf` turn digits into
subscripts (font-variant-position: sub), and `dnom` into superscripts on the
baseline as in ½, as wide as the superscripts: alone, these are as they
were before fractions were made of parts.
"""

import functools
import io
import itertools
import math
import unicodedata
from types import SimpleNamespace

import numpy as np
import pathops
import uharfbuzz
from fontTools.otlLib import builder as otl
from fontTools.pens.basePen import BasePen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

import layout
import pixel

from .shapes import (
    _set,
    add,
    blend,
    composite,
    drawn_cells,
    embolden,
    glyph,
    masters,
    path,
    phased,
    pixelate_glyphs,
    rect,
    shaper,
    shrunk,
    sideways,
    slope,
    stem,
    union,
    union_paths,
)

# Glyphs of superscript digits, Redaction's first, as numerators too
SUPERIORS = {
    "0": "uni2070",
    "1": "onesuperior",
    "2": "twosuperior",
    "3": "threesuperior",
    **{str(d): f"uni{0x2070 + d:04X}" for d in range(4, 10)},
}
DRAWN = {d: name for d, name in SUPERIORS.items() if name.startswith("uni")}
# code point: (numerator, denominator); Redaction has ¼ ½ ¾ ⅗
FRACTIONS = {
    0x2150: ("1", "7"),
    0x2151: ("1", "9"),
    0x2152: ("1", "10"),
    0x2153: ("1", "3"),
    0x2154: ("2", "3"),
    0x2155: ("1", "5"),
    0x2156: ("2", "5"),
    0x2158: ("4", "5"),
    0x2159: ("1", "6"),
    0x215A: ("5", "6"),
    0x215B: ("1", "8"),
    0x215C: ("3", "8"),
    0x215D: ("5", "8"),
    0x215E: ("7", "8"),
    0x215F: ("1", ""),
    0x2189: ("0", "3"),
    0x2100: ("a", "c"),  # account of
    0x2105: ("c", "o"),  # care of
}
REDACTION = {0xBC: ("1", "4"), 0xBD: ("1", "2"), 0xBE: ("3", "4"), 0x2157: ("3", "5")}
INFERIORS = {str(d): f"uni{0x2080 + d:04X}" for d in range(10)}
DROP = 1 / 3  # of the height of subscripts, below the baseline
# Digits Redaction has small, as denominators: in which fraction
OWN = {"4": "¼", "5": "⅗"}
# `numr` and `dnom` alone: superscripts as they are, and on the baseline, as
# before `frac` set fractions of parts
NUMR = {d: f"{name}.numr" for d, name in SUPERIORS.items()}
DENOMINATORS = {d: f"{name}.dnom" for d, name in SUPERIORS.items()}
# The parts of fractions, which only `frac` and the fractions drawn use
PARTS = {
    role: {d: f"{name}.{role}.frac" for d, name in SUPERIORS.items()} for role in ("numr", "dnom")
}
# Superscript letters of ℀ and ℅, those of ordinals.py, drawn first
LETTERS = {"a": "ordfeminine", "c": "c.superior", "o": "ordmasculine"}
CODEPOINTS = (
    {0x2070 + int(d): name for d, name in DRAWN.items()}
    | {0x2080 + int(d): name for d, name in INFERIORS.items()}
    | {cp: f"uni{cp:04X}" for cp in FRACTIONS}
)
CELLS = "figures.txt"  # the fraction slash drawn by hand on a grid, cell by cell
PHASED = (35, 50, 70)  # grids figures are placed on so: finer, they keep the drawing's
CARVED = (10, 20)  # grids letters are placed on where their carving comes out
COARSE = 50  # from this grid up, digits in fractions a cell apart exactly: two sprawl
ALTERNATES = []
# Redaction's glyphs drawn anew here on some grids, shown with the rest
REDRAWN = ["fraction"]
SAMPLES = [
    "x⁰ x¹ x² x³ x⁴ x⁵ x⁶ x⁷ x⁸ x⁹",
    "H₂O CO₂ x₀ x₁ x₉ C₆H₁₂O₆",
    "¼ ½ ¾ ⅐ ⅑ ⅒ ⅓ ⅔ ⅕ ⅖ ⅗ ⅘ ⅙ ⅚ ⅛ ⅜ ⅝ ⅞ ⅟ ↉ ⁄",
    "n1/3n n⅓n n1/2n n½n n1/10n n⅒n, 489/603 111/444 7/16, 1 1/2 (frac)",
    "n3/4n n¾n n3/5n n⅗n, 1/2, 1/2. (1/2) 1/1回 0/1, T1/2 V1/2 f1/2 H7/8",
    "1234567890123456789012345/6 1⁄2 11⁄12 (⁄ typed)",
    "as typed: 2024/05/06 3/4/5 x.com/1/2 /1/2 1/2/ 1/2⁄3 1⁄2/3",
    "砂糖1/2カップ、全体の11/12 (frac, japanese)",
    "H2O 1st 10 2 日123円 (subs, sinf, sups, ordn)",
]
FEATURES = ["frac"]


def _letters(smooth):
    """What superscript letters are shrunk from, by how much they are made
    heavier (shapes.shrunk), how much they are shrunk, and how tall and
    where they stand: their x-height at the top of ¹, as tall as
    emboldened, their baseline below."""
    one, sup = path(smooth, "1"), path(smooth, "¹")
    scale = (sup.bounds[3] - sup.bounds[1]) / (one.bounds[3] - one.bounds[1])
    source, amount = shrunk(smooth, scale, target=stem(sup))
    height = (source["OS/2"].sxHeight + 2 * amount) * scale
    return source, amount, scale, height, sup.bounds[3] - height


@functools.cache
def _ink(char):
    """How much ink Redaction's Bold adds to its Regular's `char`, over how
    much growing it across by a unit adds (shapes.sideways)."""
    regular, bold = masters()
    a, b = path(regular, char), path(bold, char)
    return (abs(b.area) - abs(a.area)) / (abs(sideways(a, 1, pointed=False).area) - abs(a.area))


def _heavier(source, char, amount, scale, height):
    """`char` of `source` made heavier, its stems as those of n emboldened
    by `amount` shrunk by `scale`, its x-height `height`: as Bold is of
    Regular (shapes.blend) where their outlines match it and it grows
    clean, its own carving MCKL's; else grown across only (shapes.sideways),
    its carving cut again, as much as n, or, where it matches but would run
    into itself (Bold's s), adding as much ink as blending would (_ink).
    Either, its x-height grows less than emboldened: it is shrunk less, and
    made that less heavier."""
    regular, bold = masters()
    x, s = source["OS/2"].sxHeight, stem(path(source, "n"))
    dx = bold["OS/2"].sxHeight - regular["OS/2"].sxHeight
    ds = stem(path(bold, "n")) - stem(path(regular, "n"))
    h, target = height / scale, s + 2 * amount  # what n emboldened would be
    # (s + t ds) / (x + t dx) = target / h
    t = (target * x - s * h) / (ds * h - dx * target)
    ink = 1
    try:
        p = blend(source, regular, bold, char, t)
    except ValueError:
        p, ink = None, _ink(char) / _ink("n")
    if p is not None:
        k = height / (x + t * dx)
        return p.transform(k, 0, 0, k, 0, 0)
    k = height / x
    p = sideways(path(source, char), (target * scale / k - s) / 2 * ink, carve=True, thick=s)
    return p.transform(k, 0, 0, k, 0, 0)


def _superior(smooth, char, own=True):
    """`char` of `smooth` as a superscript, on the baseline of ¹: 4 and 5 are
    those of Redaction's ¼ and ⅗, raised (unless not `own`, for score.py to
    draw them as the others); other digits are its own, made heavier as
    Bold is of Regular (shapes.blend: Bold's past Bold) till the stem of its
    1 shrunk as tall as ¹ is that of ¹, set as that 1 would be on ¹; it
    raises if Regular's, Bold's and its own do not match. Letters are
    shrunk as much, their x-height at its top, their stems as those of ¹
    (shapes.shrunk): an upright Regular's are Bold's thinned, which keeps
    their carving; others are made heavier (_heavier), keeping theirs."""
    one, sup = path(smooth, "1"), path(smooth, "¹")
    scale = (sup.bounds[3] - sup.bounds[1]) / (one.bounds[3] - one.bounds[1])
    if char.isalpha():
        source, amount, scale, height, base = _letters(smooth)
        if amount < 0:  # Bold thinned, which keeps its carving
            p = embolden(path(source, char), amount)
            return glyph(p.transform(scale, 0, 0, scale, 0, base + amount * scale))
        p = _heavier(source, char, amount, scale, height)
        return glyph(p.transform(1, 0, 0, 1, 0, base))
    up = sup.bounds[1] - one.bounds[1] * scale
    if own and char in OWN:  # the denominator of a fraction of Redaction's: not slash nor ¹ ³
        pieces = sorted(path(smooth, OWN[char]).contours, key=lambda c: c.bounds[3] - c.bounds[1])
        pieces.pop()  # the slash, the tallest
        denominator = union([])
        for c in pieces:
            if c.bounds[1] < sup.bounds[1] / 2:
                denominator.addPath(c)
        return glyph(denominator.transform(1, 0, 0, 1, 0, up))
    regular, bold = masters()
    t = (stem(sup) / scale - stem(one)) / (stem(path(bold, "1")) - stem(path(regular, "1")))
    heavier = blend(smooth, regular, bold, "1", t), blend(smooth, regular, bold, char, t)
    if not all(heavier):  # drawn another way, it would stand out of the set
        raise ValueError(f"{char} of Redaction's Regular, Bold and this style do not match")
    one, p = heavier
    scale = (sup.bounds[3] - sup.bounds[1]) / (one.bounds[3] - one.bounds[1])
    # On the grid as ¹ is, pixelated: the side bearings come after
    dx, dy = sup.bounds[0] - one.bounds[0] * scale, sup.bounds[1] - one.bounds[1] * scale
    return glyph(p.transform(scale, 0, 0, scale, dx, dy))


def pixelated(font, glyphs, grid, rows=None):
    """Drawn figures {name: glyph} pixelated on the grid of `font`, on 35 to
    70 (PHASED) each where in a cell it falls best (shapes.phased): its
    hairlines are about half a cell, which a cell fills or not as they
    fall. On the rows of ¹, strokes as thick as MCKL's ² ³ on the grid.
    Letters, on their own `rows`, so too, and on 10 and 20 (CARVED) where
    their carving comes out first, and none as another."""
    letters = rows is not None
    if grid not in PHASED and not (letters and grid in CARVED):
        return pixelate_glyphs(glyphs, grid)
    glyf = font["glyf"]
    for name in ("onesuperior", "twosuperior", "threesuperior"):
        glyf[name].recalcBounds(glyf)
    rows = rows or (glyf["onesuperior"].yMin, glyf["onesuperior"].yMax)
    like = [glyf["twosuperior"], glyf["threesuperior"]]
    return phased(glyphs, grid, rows, like, letters and grid in CARVED, distinct=letters)


def _bearings(font, char):
    """The left and right side bearings of `char` in `font`, and its height."""
    name = font.getBestCmap()[ord(char)]
    g = font["glyf"][name]
    g.recalcBounds(font["glyf"])
    return g.xMin, font["hmtx"][name][0] - g.xMax, g.yMax - g.yMin


@functools.cache
def _spacing(smooth):
    """How much farther from their neighbours MCKL sets ¹ ² ³ than 1 2 3
    shrunk as tall: on both sides alike, and to the right of the left
    (in italic, along the slant, as they are raised)."""
    track = shift = 0
    for d, s in zip("123", "¹²³"):
        (l0, r0, h0), (l1, r1, h1) = _bearings(smooth, d), _bearings(smooth, s)
        dl, dr = l1 - l0 * h1 / h0, r1 - r0 * h1 / h0
        track, shift = track + (dl + dr) / 6, shift + (dl - dr) / 6
    return track, shift


def superiors(font, smooth, grid, chars):
    """{glyph name: (glyph, advance)} of `chars` ({character: glyph name})
    as superscripts, digits and letters with their own side bearings,
    shrunk as they are (digits as tall as ¹, letters their x-height at its
    top), set as MCKL sets ¹ ² ³ against 1 2 3 (_spacing): so ⁰⁰ is to 00
    as ¹² is to 12, and in italic a round digit is not given the overhang
    of ¹. On a grid, digits from MCKL's ¹ there: its side bearings, and
    the difference of the digit's to those of ¹ measured smooth (cells of
    their own spacing would round to none)."""
    g = grid or 1
    track, shift = _spacing(smooth)
    size = _letters(smooth)[3] / smooth["OS/2"].sxHeight
    figure = _bearings(smooth, "¹")[2] / _bearings(smooth, "1")[2]
    # MCKL's ¹ on the grid against smooth: nothing at grade 0
    one, pixel_one = _bearings(smooth, "¹"), _bearings(font, "¹")
    moved = pixel_one[0] - one[0], pixel_one[1] - one[1]

    def bearings(c):
        lsb, rsb, _ = _bearings(smooth, c)
        if not c.isdigit():
            return lsb * size + track + shift, rsb * size + track - shift
        return lsb * figure + track + shift + moved[0], rsb * figure + track - shift + moved[1]

    drawn = {name: _superior(smooth, c) for c, name in chars.items()}
    if grid:  # in the order of `chars`, for the same glyph order every build
        digits = {n: drawn[n] for c, n in chars.items() if c.isdigit()}
        letters = {n: drawn[n] for c, n in chars.items() if not c.isdigit()}
        done = pixelated(font, digits, grid) if digits else {}
        if letters:  # on their baseline and x-height
            *_, height, base = _letters(smooth)
            rows = pixel.snap(base, grid), pixel.snap(base + height, grid)
            done |= pixelated(font, letters, grid, rows)
        drawn = {n: done[n] for n in drawn}
    out = {}
    for c, name in chars.items():
        gl, (lsb, rsb) = drawn[name], bearings(c)
        gl.coordinates.translate((pixel.snap(lsb, g) - gl.coordinates.calcIntBounds()[0], 0))
        gl.recalcBounds(None)
        out[name] = gl, pixel.snap(gl.xMax + rsb, g)
    return out


def add_glyphs(font, smooth, grid=None):
    g = grid or 1
    glyf, hmtx, cmap = font["glyf"], font["hmtx"], font.getBestCmap()
    add(
        font,
        superiors(font, smooth, grid, DRAWN),
        {0x2070 + int(d): name for d, name in DRAWN.items()},
    )
    # Subscripts: superscripts, their top as far below the baseline as DROP of
    # them, back along the slant in italic, all as far: spaced as the
    # superscripts are, their ink as far from what is before and after them.
    # From COARSE up, where pixel letters reach their advance, each moves
    # back but not past its side bearing, its advance ending as far past its
    # ink as ¹'s if that is more than its superscript's
    sup = path(font, "¹")
    height = sup.bounds[3] - sup.bounds[1]
    down = pixel.snap(-height * DROP - sup.bounds[1], g)
    back = pixel.snap(down * slope(smooth), g)
    glyf["onesuperior"].recalcBounds(glyf)
    right = hmtx["onesuperior"][0] - glyf["onesuperior"].xMax
    inferiors = {}
    for d, name in INFERIORS.items():
        superior, advance = glyf[SUPERIORS[d]], hmtx[SUPERIORS[d]][0]
        if (grid or 0) >= COARSE:
            superior.recalcBounds(glyf)
            back = pixel.snap(max(down * slope(smooth), -superior.xMin), g)
            advance = max(advance, pixel.snap(superior.xMax + back + right, g))
        inferiors[name] = composite(font, [(SUPERIORS[d], back, down)], grid), advance
    add(font, inferiors, {0x2080 + int(d): name for d, name in INFERIORS.items()})

    _slash(font, smooth, grid)
    # `numr` and `dnom` alone: superscripts, and those on the baseline as in
    # ½, each with the advance of its superscript, as before fractions were
    # set of parts; glyphs of their own, which `frac` can tell from typed ones
    den_shift = _Parts.baseline(smooth, grid)
    add(
        font,
        {
            forms[d]: (composite(font, [(sup, 0, dy)], grid), hmtx[sup][0])
            for forms, dy in ((NUMR, 0), (DENOMINATORS, den_shift))
            for d, sup in SUPERIORS.items()
        },
        {},
    )
    parts = _Parts(font, smooth, grid)
    add(font, parts.glyphs(), {})
    add(font, {CODEPOINTS[cp]: parts.drawn(*nd) for cp, nd in FRACTIONS.items()}, CODEPOINTS)

    # sups gives the digits Redaction lacks, numr all of them its own glyphs
    gsub = font["GSUB"].table
    lookups = {
        tag: {
            i
            for r in gsub.FeatureList.FeatureRecord
            if r.FeatureTag == tag
            for i in r.Feature.LookupListIndex
        }
        for tag in ("sups", "numr", "frac")
    }
    for i in lookups["sups"]:
        for st in gsub.LookupList.Lookup[i].SubTable:
            st.mapping.update({cmap[ord(d)]: name for d, name in DRAWN.items()})
    for i in lookups["numr"]:
        for st in gsub.LookupList.Lookup[i].SubTable:
            st.mapping.update({cmap[ord(d)]: name for d, name in NUMR.items()})
    # subs, sinf and dnom, which Redaction does not have
    for tag, forms in (("subs", INFERIORS), ("sinf", INFERIORS), ("dnom", DENOMINATORS)):
        mapping = {cmap[ord(d)]: name for d, name in forms.items()}
        layout.add_feature(gsub, tag, otl.buildLookup([otl.buildSingleSubstSubtable(mapping)]))
    # frac, of parts, in place of Redaction's, which turns 1/2 into ½ and
    # 0/0 into %; its parts set as the drawn fractions, by its own GPOS,
    # which `kern` uses too
    layout.remove_lookups(gsub, lookups["frac"])
    _frac(font)
    gpos = font["GPOS"].table
    shared = parts.lookups(gpos)
    for tag in ("frac", "kern"):
        layout.use_lookups(gpos, tag, shared)
    if raised := _raised(font, smooth, grid):
        layout.extend_feature(gpos, "kern", raised)
    if close := _close(font, smooth, grid):
        layout.extend_feature(gpos, "kern", close)
    if lettered := _lettered(font, smooth, grid):
        layout.extend_feature(gpos, "kern", lettered)


def add_features(font):
    """Share the vertical forms `frac` needs (_frac) with the scripts and
    language systems of the merged font: Noto Serif JP's `vert` and `vrt2`
    get its lookups. And keep fractions clear of every glyph of it, before
    and after them (_beside), by lookups `frac` and `kern` share."""
    layout.share_features(font["GSUB"].table, {"vert", "vrt2"})
    gpos = font["GPOS"].table
    beside = _beside(font)
    for tag in ("frac", "kern"):
        layout.use_lookups(gpos, tag, beside)


def _slash(font, smooth, grid):
    """The fraction slash drawn by hand on `grid` (CELLS), where MCKL's
    breaks into pieces or has rows of air: its bottom left cell where the
    cells say, its advance MCKL's."""
    cells = drawn_cells(CELLS).get((grid, smooth["name"].getDebugName(2), "⁄"))
    if not cells:
        return
    name = font.getBestCmap()[0x2044]
    x, y = cells.at
    top = y + len(cells)
    p = union_paths(
        [
            rect((x + j) * grid, (top - i - 1) * grid, (x + j + 1) * grid, (top - i) * grid)
            for i, row in enumerate(cells)
            for j, c in enumerate(row)
            if c == "#"
        ]
    )
    add(font, {name: (glyph(p), font["hmtx"][name][0])}, {})


def _half(smooth):
    """The slash, numerator and denominator of Redaction's ½, measured
    smooth: the pieces of a pixel ½ can be one."""
    pieces = sorted(path(smooth, "½").contours, key=lambda c: c.bounds[3] - c.bounds[1])
    slash = pieces.pop()  # the tallest
    numerator = max(pieces, key=lambda c: c.bounds[1])
    return slash, numerator, min(pieces, key=lambda c: c.bounds[1])


class _Parts:
    """The parts of fractions, and where they go, the one model of the
    fractions drawn (⅓) and of those `frac` sets (1/3), which are so the
    same, side bearings and advance included: numerators and denominators
    of their own (.numr.frac, .dnom.frac: `numr` and `dnom` alone keep
    their glyphs) are superscripts with their side bearings (superiors;
    letters those of ¹), the denominator's right one that of ½ (a cell at
    least on a grid, clear of the letter after it), and every place between
    two parts is a kerning pair: of two digits, as ¹ ² ³ are set (their ink
    as far apart as their side bearings), but no nearer than MCKL sets any two of them (_gap), a
    cell at least on a grid; of a numerator and the slash, and of the slash
    and a denominator, as far apart as in ½, at their height along it, but
    no nearer than MCKL sets any part of ½ ¼ ¾ ⅗ (_clearance), a cell at
    least on a grid. Each a unit or cell further at a time, till clear. A
    place depends on the two parts it is between only: the parts stand on
    a line, the slash between them, and a numerator further from the slash
    than the one next to it is clear of it.

    A fraction holds its ink: its advance ends past all of it, the slash's
    too, as far as ½'s past its denominator, measured along the slant in
    Italic, as its letters stand: where the slash leans past a narrow
    denominator (upright, 1/1 on 35), the last denominator grows by as much
    (extra), in context, for the denominators that need it. Measured
    upright, Italic's slash hung over every denominator but 3 and 7, which
    grew for it, and left a hole after 1/1 three times the gap after 1/3;
    along the slant it reaches past none. How it keeps clear of its
    neighbours is set once the font is merged, every glyph there (_beside)."""

    @staticmethod
    def baseline(smooth, grid):
        """How far below numerators denominators stand: on the baseline, as
        in ½."""
        _, numerator, denominator = _half(smooth)
        return pixel.snap(denominator.bounds[1] - numerator.bounds[1], grid or 1)

    def __init__(self, font, smooth, grid):
        self.font, self.grid, self.g = font, grid, grid or 1
        self.upright = (1, 0, -slope(smooth), 1, 0, 0)  # stands Italic's ink up
        g, glyf, hmtx = self.g, font["glyf"], font["hmtx"]
        glyf["onesuperior"].recalcBounds(glyf)
        self.left = hmtx["onesuperior"][1]
        self.right = hmtx["onesuperior"][0] - glyf["onesuperior"].xMax
        slash, numerator, denominator = _half(smooth)
        self.den_shift = self.baseline(smooth, grid)
        half = smooth["hmtx"][smooth.getBestCmap()[0xBD]][0]
        # ½'s right side bearing; a cell at least on a grid, where letters
        # start at their advance (n on 100, in Italic and Bold) and touched it
        self.end = max(pixel.snap(half - denominator.bounds[2], g), grid or 0)
        # From the slash, where its ink starts: where the numerator's ink
        # ends, and the denominator's starts, as in ½, measured smooth
        self.fraction = font.getBestCmap()[0x2044]
        glyf[self.fraction].recalcBounds(glyf)
        self.slash = glyf[self.fraction].xMin
        self.num_end = numerator.bounds[2] - slash.bounds[0]
        self.den_start = denominator.bounds[0] - slash.bounds[0]
        clear, gap = _clearance(smooth), _gap(smooth)
        self.need = max(pixel.snap(clear, g), g) if grid else clear
        self.apart = max(pixel.snap(gap, g), g) if grid else gap
        # Letters on the baseline too: they stand higher than digits
        _, amount, scale, _, base = _letters(smooth)
        self.letter_drop = -pixel.snap(base + min(amount, 0) * scale, g)
        self.kerns, self.extras = {}, {}

    def part(self, part):
        """(glyph, component, dx, dy, advance) of `part`, (character,
        "numr" or "dnom"), or "⁄": the component the glyph is of, where."""
        if part == "⁄":
            return self.fraction, self.fraction, 0, 0, self.font["hmtx"][self.fraction][0]
        char, role = part
        glyf, base = self.font["glyf"], (SUPERIORS | LETTERS)[char]
        glyf[base].recalcBounds(glyf)
        left, right = self.sides(char)
        dx, width = left - glyf[base].xMin, glyf[base].xMax - glyf[base].xMin
        if role == "numr":
            return PARTS[role].get(char), base, dx, 0, left + width + right
        dy = self.letter_drop if char in LETTERS else self.den_shift
        return PARTS[role].get(char), base, dx, dy, left + width + self.end

    def sides(self, char):
        """The side bearings of the superscript `char` is: its own for a
        digit, those of ¹ for a letter (℀ ℅)."""
        if char in LETTERS:
            return self.left, self.right
        glyf, hmtx, name = self.font["glyf"], self.font["hmtx"], SUPERIORS[char]
        glyf[name].recalcBounds(glyf)
        return hmtx[name][1], hmtx[name][0] - glyf[name].xMax

    def glyphs(self):
        """{name: (glyph, advance)} of the numerators and denominators."""
        out = {}
        for d in SUPERIORS:
            for role in PARTS:
                name, base, dx, dy, advance = self.part((d, role))
                out[name] = composite(self.font, [(base, dx, dy)], self.grid), advance
        return out

    def kern(self, a, b):
        """How much the advance of part `a` grows before part `b`, the one
        after it in a fraction."""
        if (a, b) in self.kerns:
            return self.kerns[a, b]
        g = self.g
        *_, advance = self.part(a)
        if a == "⁄":  # the denominator's ink from the slash's
            k, need = self.slash + self.den_start - self.sides(b[0])[0] - advance, self.need
        elif b == "⁄":  # the slash's ink from the numerator's
            k, need = -self.sides(a[0])[1] - self.num_end - self.slash, self.need
        else:  # the ink of two digits as far apart as their side bearings
            k, need = (self.sides(a[0])[1] - self.end if a[1] == "dnom" else 0), self.apart
        k = pixel.snap(k, g)
        first = _outline(self.font, self._set([a])[0])

        def clear(k):
            return _apart(first, _outline(self.font, self._set([b], advance + k)[0]), need)

        if (self.grid or 0) >= COARSE and "⁄" not in (a, b):  # a cell, where they allow it
            while clear(k - g):
                k -= g
        while not clear(k):
            k += g
        self.kerns[a, b] = k
        return k

    def extra(self, den):
        """How much the last denominator of `den` (digits) after the slash
        grows, for the fraction to end as far past the slash's ink as past
        its own: a whole cell at a time on a grid."""
        if den not in self.extras:
            components, x = self._set(["⁄", *((c, "dnom") for c in den)], whole=False)
            # past the denominator's ink, which the advance ends `end` after
            ink = _outline(self.font, components).transform(*self.upright)
            last = _outline(self.font, components[1:]).transform(*self.upright)
            over = ink.bounds[2] - last.bounds[2]
            self.extras[den] = max(0, math.ceil(over / self.g) * self.g)
        return self.extras[den]

    def extras_needed(self):
        """{denominator: extra} of those that grow, as long as some of a
        length do; a denominator only grows less with each digit."""
        out, length = {}, 1
        while True:
            grown = {
                den: k
                for den in map("".join, itertools.product(SUPERIORS, repeat=length))
                if (k := self.extra(den))
            }
            if not grown:
                return out
            out |= grown
            length += 1

    def _set(self, parts, x=0, whole=True):
        """[(component, dx, dy)] of `parts` set from `x`, and where they end:
        past the extra of the last denominator, if `whole`."""
        components = []
        for i, p in enumerate(parts):
            _, base, dx, dy, advance = self.part(p)
            components.append((base, x + dx, dy))
            x += advance + (self.kern(p, parts[i + 1]) if i + 1 < len(parts) else 0)
        if whole and "⁄" in parts and parts[-1] != "⁄":
            x += self.extra("".join(c for c, _ in parts[parts.index("⁄") + 1 :]))
        return components, x

    def drawn(self, num, den):
        """The fraction `num`/`den` as a glyph, and its advance: as `frac`
        sets it."""
        components, x = self._set([(c, "numr") for c in num] + ["⁄"] + [(c, "dnom") for c in den])
        return composite(self.font, components, self.grid), x

    def lookups(self, gpos):
        """The lookups setting fractions, the same for `frac` and `kern`: a
        pair of parts; and the last denominator grown (extra), in context,
        which applies single positionings, appended to the lookup list of
        `gpos` first. Their neighbours are set once the font is merged
        (_beside)."""
        digits, nums, dens = list(SUPERIORS), PARTS["numr"], PARTS["dnom"]
        order = self.font.getReverseGlyphMap()
        pairs = {}
        for a in digits:
            pairs[nums[a], self.fraction] = self.kern((a, "numr"), "⁄")
            pairs[self.fraction, dens[a]] = self.kern("⁄", (a, "dnom"))
            for b in digits:
                for role in ("numr", "dnom"):
                    pairs[PARTS[role][a], PARTS[role][b]] = self.kern((a, role), (b, role))
        records = {pair: (otl.buildValue({"XAdvance": k}), None) for pair, k in pairs.items() if k}
        lookups = [otl.buildLookup([otl.buildPairPosGlyphsSubtable(records, order)])]
        extras = self.extras_needed()
        if not extras:
            return lookups
        grow = {}
        for k in sorted(set(extras.values())):
            values = {name: otl.buildValue({"XAdvance": k}) for name in dens.values()}
            gpos.LookupList.Lookup.append(
                otl.buildLookup([otl.buildSinglePosSubtable(values, order)])
            )
            grow[k] = SimpleNamespace(lookup_index=len(gpos.LookupList.Lookup) - 1)
        builder = otl.ChainContextPosBuilder(self.font, None)
        for den in sorted(extras, key=len, reverse=True):  # longer first
            glyphs = [{self.fraction}, *({dens[c]} for c in den)]
            # not when more denominators follow: that one is not the last
            builder.rules.append(
                otl.ChainContextualRule([], glyphs, [set(dens.values())], [None] * len(glyphs))
            )
            grown = [None] * len(den) + [[grow[extras[den]]]]
            builder.rules.append(otl.ChainContextualRule([], glyphs, [], grown))
        return [*lookups, builder.build()]


PUNCTUATION = ";:,."  # what raised glyphs are kerned off (_raised)
# Raised letters, of ordinals.py, for what letter
RAISED = {"ordfeminine": "a", "ordmasculine": "o"}


def _raised(font, smooth, grid):
    """A kerning lookup keeping superscripts (¹ ⁴, the letters `ordn`
    raises) off the punctuation after them (4th; x²,), no nearer than the
    digit or letter they are of is to it, and on a grid not touching it,
    nor, there, each other (4th): pixels touching at a corner read as one.
    As far as they are set, with Redaction's kerning (¹ ² ³ ª º)."""
    g, glyf, hmtx, cmap = grid or 1, font["glyf"], font["hmtx"], font.getBestCmap()
    letters = {
        name: RAISED.get(name, name.split(".")[0])
        for name in font.getGlyphOrder()
        if name.endswith(".superior") or name in RAISED
    }
    raised = {name: d for d, name in SUPERIORS.items()} | letters
    hb, typed = shaper(font), {name: cp for cp, name in cmap.items()}

    def placed(a, b):  # the outlines of a and b set side by side, kerned if typed
        x = hmtx[a][0]
        if a in typed and b in typed:
            x = _set(font, hb, chr(typed[a]) + chr(typed[b]))[0][1][1]
        return _outline(font, [(a, 0, 0)]), _outline(font, [(b, x, 0)])

    pairs = {}
    for a, of in raised.items():
        if not glyf[a].numberOfContours:
            continue
        after = [
            (cmap[ord(p)], _distance(*placed(cmap[ord(of)], cmap[ord(p)]))) for p in PUNCTUATION
        ]
        if grid and a in letters:
            after += [(b, g) for b in letters]
        for b, need in after:
            need = max(need, g) if grid else need
            first, second = placed(a, b)
            k = 0
            while not _apart(first, second.transform(1, 0, 0, 1, k, 0), need):
                k += g
            if k:
                pairs[a, b] = (otl.buildValue({"XAdvance": k}), None)
    if pairs:
        subtable = otl.buildPairPosGlyphsSubtable(pairs, font.getReverseGlyphMap())
        return otl.buildLookup([subtable])


def _close(font, smooth, grid):
    """A kerning lookup keeping two small digits side by side (superscripts,
    subscripts, `numr` and `dnom` alone: fractions kern their own parts) no
    nearer than MCKL sets any two of ¹ ² ³ (_gap), where their own side
    bearings bring them nearer (Italic ⁷⁷); on a grid, where MCKL's touch,
    not over each other. Each form alike, as they are drawn alike: but
    pairs of ¹ ² ³, as MCKL sets them."""
    g, cmap = grid or 1, font.getBestCmap()
    need = 0 if grid else _gap(smooth)
    hb, pairs = shaper(font), {}
    forms = (SUPERIORS, INFERIORS, NUMR, DENOMINATORS)
    for a, b in itertools.product(SUPERIORS, repeat=2):
        if a in "123" and b in "123":
            continue
        (_, (_, x, _)), _ = _set(font, hb, chr(_cp(a)) + chr(_cp(b)))
        first = _outline(font, [(cmap[_cp(a)], 0, 0)])
        second = _outline(font, [(cmap[_cp(b)], x, 0)])
        k = 0
        while not _apart(first, second.transform(1, 0, 0, 1, k, 0), need):
            k += g
        for form in forms if k else ():
            pairs[form[a], form[b]] = (otl.buildValue({"XAdvance": k}), None)
    if pairs:
        subtable = otl.buildPairPosGlyphsSubtable(pairs, font.getReverseGlyphMap())
        return otl.buildLookup([subtable])


def _lettered(font, smooth, grid):
    """A kerning lookup keeping Italic's subscripts (typed, `subs` and
    `sinf`: the same glyphs), moved back along the slant, off a Latin letter
    before them, what hangs below it (g₂ x₀), and off one after them hanging
    back under them (₂j): no nearer than MCKL sets any two of ¹ ² ³ (_gap),
    a cell on a grid, where pixels touching at a corner read as one, but
    not over each other from COARSE up, where MCKL's letters touch. Pairs
    that far apart already are left as set, and upright, as MCKL sets them
    (Regular's g₂)."""
    if not slope(smooth):
        return None
    g, cmap = grid or 1, font.getBestCmap()
    need = (g if g < COARSE else 0) if grid else _gap(smooth)
    letters = {
        name: cp
        for cp, name in cmap.items()
        if unicodedata.category(chr(cp)) in ("Lu", "Ll")
        and unicodedata.name(chr(cp), "").startswith("LATIN")
    }
    hb, pairs = shaper(font), {}
    inks = {letter: _outline(font, [(letter, 0, 0)]) for letter in letters}
    for d, sub in INFERIORS.items():
        grown = _outline(font, [(sub, 0, 0)])
        grown = embolden(grown, need - 0.5, round=True) if need > 0.5 else grown
        for (letter, cp), after in itertools.product(letters.items(), (False, True)):
            pair = (sub, letter) if after else (letter, sub)
            text = "".join(chr(0x2080 + int(d)) if n == sub else chr(cp) for n in pair)
            (_, (_, x, _)), _ = _set(font, hb, text)
            x = x if after else -x  # the letter, the subscript at 0
            k, way = 0, 1 if after else -1  # the second moved away from the first
            while not _clear(grown, inks[letter].transform(1, 0, 0, 1, x + way * k, 0)):
                k += g
            if k:
                pairs[pair] = (otl.buildValue({"XAdvance": k}), None)
    if pairs:
        subtable = otl.buildPairPosGlyphsSubtable(pairs, font.getReverseGlyphMap())
        return otl.buildLookup([subtable])


def _cp(d):
    """The code point of the superscript digit `d`."""
    return {"1": 0xB9, "2": 0xB2, "3": 0xB3}.get(d, 0x2070 + int(d))


@functools.cache
def _gap(smooth):
    """The least air MCKL leaves between two of ¹ ² ³ set side by side in
    `smooth`: 30 units in Regular, 25 in Italic, 15 in Bold, each ¹²."""
    hmtx, cmap, least = smooth["hmtx"], smooth.getBestCmap(), float("inf")
    for a in "¹²³":
        for b in "¹²³":
            pa = path(smooth, a)
            pb = path(smooth, b, (1, 0, 0, 1, hmtx[cmap[ord(a)]][0], 0))
            least = min(least, _distance(pa, pb))
    return int(least)


def _distance(a, b, most=200):
    """How far apart the outlines `a` and `b` are, to half a unit, `most` at
    most."""
    lo, hi = 0, most
    while hi - lo > 0.5:
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if _apart(a, b, mid) else (lo, mid)
    return lo


@functools.cache
def _clearance(smooth):
    """The least air MCKL leaves between the slash of his fractions in
    `smooth` (REDACTION: ½ ¼ ¾ ⅗) and their numerator or denominator, its
    pieces above or below the middle of the slash: 45 units in Regular, 39
    in Italic, 34 in Bold, each the 1 of ½ and ¼."""
    least = float("inf")
    for cp in REDACTION:
        pieces = sorted(path(smooth, chr(cp)).contours, key=lambda c: c.bounds[3] - c.bounds[1])
        slash = pieces.pop()  # the tallest
        middle = (slash.bounds[1] + slash.bounds[3]) / 2
        for side in (True, False):
            part = pathops.Path()
            for c in pieces:
                if ((c.bounds[1] + c.bounds[3]) / 2 > middle) == side:
                    part.addPath(c)
            least = min(least, _distance(part, slash))
    return int(least)


def _apart(a, b, distance):
    """Whether the outlines `a` and `b` are `distance` apart at least, to
    half a unit."""
    return _clear(embolden(a, distance - 0.5, round=True) if distance > 0.5 else a, b)


def _clear(grown, b):
    """Whether `b` keeps off `grown`, an outline emboldened as far as it
    must be from it."""
    return abs(pathops.op(grown, b, pathops.PathOp.INTERSECTION).area) < 1e-6


def _outline(font, parts):
    """The outline of [(glyph name, dx, dy)] of `font`, as composite() puts
    them."""
    glyf, gs, p = font["glyf"], font.getGlyphSet(), pathops.Path()
    for name, dx, dy in parts:
        glyf[name].recalcBounds(glyf)
        dx += font["hmtx"][name][1] - glyf[name].xMin if glyf[name].numberOfContours else 0
        gs[name].draw(TransformPen(pathops.PathPen(p, glyphSet=gs), (1, 0, 0, 1, dx, dy)))
    return p


class _Sampler(BasePen):
    """Points along outlines, `step` apart at most, their ends included."""

    def __init__(self, step):
        super().__init__(None)
        self.step, self.points, self.start = step, [], None

    def _along(self, at, length):
        n = max(1, math.ceil(length / self.step))
        self.points += [at(i / n) for i in range(1, n + 1)]

    def _moveTo(self, pt):
        self.start = pt
        self.points.append(pt)

    def _lineTo(self, pt):
        p0 = self._getCurrentPoint()
        self._along(
            lambda t: (p0[0] + (pt[0] - p0[0]) * t, p0[1] + (pt[1] - p0[1]) * t), math.dist(p0, pt)
        )

    def _qCurveToOne(self, p1, p2):
        p0 = self._getCurrentPoint()
        self._along(
            lambda t: tuple(
                (1 - t) ** 2 * a + 2 * (1 - t) * t * b + t * t * c for a, b, c in zip(p0, p1, p2)
            ),
            math.dist(p0, p1) + math.dist(p1, p2),  # no shorter than the curve
        )

    def _curveToOne(self, p1, p2, p3):
        p0 = self._getCurrentPoint()
        self._along(
            lambda t: tuple(
                (1 - t) ** 3 * a + 3 * (1 - t) ** 2 * t * b + 3 * (1 - t) * t * t * c + t**3 * e
                for a, b, c, e in zip(p0, p1, p2, p3)
            ),
            math.dist(p0, p1) + math.dist(p1, p2) + math.dist(p2, p3),
        )

    def _closePath(self):
        if self.start is not None and self._getCurrentPoint() != self.start:
            self._lineTo(self.start)


def _points(p, step=1):
    """Points along the outline `p`, a pathops.Path, an array (n, 2)."""
    pen = _Sampler(step)
    p.draw(pen)
    return np.array(pen.points, dtype=float).reshape(-1, 2)


MOST = 150  # how near neighbours are measured, at most (_Reaching)


def _profile(p, right):
    """The rightmost (or leftmost, unless `right`) ink of the outline `p` in
    each unit of its height: the first unit, and an array of x, -inf (or
    inf) where there is none."""
    pts = _points(p)
    if not len(pts):
        return 0, np.zeros(0)
    rows = np.floor(pts[:, 1]).astype(int)
    xs = np.full(rows.max() - rows.min() + 1, -np.inf if right else np.inf)
    (np.maximum if right else np.minimum).at(xs, rows - rows.min(), pts[:, 0])
    return int(rows.min()), xs


def _shift(profile, dx):
    return profile[0], profile[1] + dx


def _window(profile, reach, right=False):
    """`profile` widened by `reach` units up and down: in each unit, the
    leftmost (or rightmost) of those `reach` units away at most."""
    start, xs = profile
    edge = -np.inf if right else np.inf
    padded = np.concatenate([np.full(2 * reach, edge), xs, np.full(2 * reach, edge)])
    n = len(xs) + 2 * reach
    out = padded[:n].copy()
    for i in range(1, 2 * reach + 1):
        out = (np.maximum if right else np.minimum)(out, padded[i : i + n])
    return start - reach, out


def _air(left, right):
    """The least horizontal air between `left`, a right profile, and
    `right`, a left one, in the units both have ink."""
    (a0, ax), (b0, bx) = left, right
    lo, hi = max(a0, b0), min(a0 + len(ax), b0 + len(bx))
    if lo >= hi:
        return np.inf
    gap = bx[lo - b0 : hi - b0] - ax[lo - a0 : hi - a0]
    gap = gap[np.isfinite(gap)]
    return gap.min() if len(gap) else np.inf


def _rows(left, right, reach):
    """How far right of each unit of `left`, a right profile, each of
    `right`, a left one, is, and how far above or below at least: those
    `reach` apart vertically at most."""
    (a0, ax), (b0, bx) = left, right
    ay, by = a0 + np.arange(len(ax)), b0 + np.arange(len(bx))
    a = np.isfinite(ax) & (ay >= b0 - reach) & (ay <= b0 + len(bx) + reach)
    b = np.isfinite(bx) & (by >= a0 - reach) & (by <= a0 + len(ax) + reach)
    dy = np.maximum(np.abs(by[b][None] - ay[a][:, None]) - 1, 0)  # units a unit high
    return bx[b][None] - ax[a][:, None], dy


def _within(left, right, reach):
    """`left`, a right profile, and `right`, a left one, but for the units
    of either further than `reach` across from all of the other: they come
    no nearer it."""
    (a0, ax), (b0, bx) = left, right
    if not np.isfinite(ax).any() or not np.isfinite(bx).any():
        return left, right
    lo, hi = bx[np.isfinite(bx)].min(), ax[np.isfinite(ax)].max()
    return (a0, np.where(ax >= lo - reach, ax, -np.inf)), (
        b0,
        np.where(bx <= hi + reach, bx, np.inf),
    )


def _nearest(left, right):
    """How near `left`, a right profile, and `right`, a left one after it,
    come, MOST at most."""
    dx, dy = _rows(*_within(left, right, MOST), MOST)
    if not dx.size:
        return MOST
    return min(MOST, float(np.sqrt(np.maximum(dx, 0) ** 2 + dy**2).min()))


def _clearing(left, right, need):
    """How far right `right`, a left profile, goes for its ink to be `need`
    from that of `left`, a right profile before it, at least."""
    dx, dy = _rows(*_within(left, right, need), need)
    near = dy < need
    if not near.any():
        return 0
    return max(0, float((np.sqrt(np.maximum(need**2 - dy**2, 0)) - dx)[near].max()))


def _grid(font):
    """The grid of `font`, a Redaction 10 to 100 or a font drawn and merged
    from it, by its family name; None if smooth."""
    family = font["name"].getDebugName(1).split()
    return int(family[-1]) if family[-1].isdigit() else None


def _samples(font, placed):
    """The outline of the glyphs [(name, x, y)] of `font` set there, in
    straight pieces a unit long at most: arrays (n, 2) of where each starts
    and where it ends."""
    glyf, starts, ends = font["glyf"], [], []
    for name, dx, dy in placed:
        coords, last, flags = glyf[name].getCoordinates(glyf)
        pts = np.array(coords, dtype=float).reshape(-1, 2)
        if not len(pts):
            continue
        on = np.array(flags, dtype=int).reshape(-1) & 1 == 1
        last = np.array(last)
        first = np.concatenate([[0], last[:-1] + 1])
        after = np.arange(len(pts)) + 1  # the next point of the same contour
        after[last] = first
        # TrueType: between two off-curve points, an on-curve one midway
        both = ~on & ~on[after]
        at = np.arange(len(pts)) + np.cumsum(both) - both
        q, qo = np.empty((len(pts) + both.sum(), 2)), np.ones(len(pts) + both.sum(), dtype=bool)
        q[at], qo[at] = pts, on
        q[at[both] + 1] = (pts[both] + pts[after[both]]) / 2
        qa = np.arange(len(q)) + 1
        qa[at[last] + both[last]] = at[first]
        ons = np.flatnonzero(qo)
        a, k = q[ons], qa[ons]
        curve = ~qo[k]
        b = np.where(curve[:, None], q[qa[k]], q[k])
        c = np.where(curve[:, None], q[k], (a + b) / 2)
        n = np.maximum(1, np.ceil(np.hypot(*(c - a).T) + np.hypot(*(b - c).T))).astype(int)
        i = (np.arange(n.sum()) - np.repeat(np.cumsum(n) - n, n))[:, None]
        a, b, c, n = (np.repeat(v, n, axis=0) for v in (a, b, c, n[:, None]))
        for t, out in ((i / n, starts), ((i + 1) / n, ends)):
            out.append((1 - t) ** 2 * a + 2 * (1 - t) * t * c + t * t * b + (dx, dy))
    if not starts:
        return np.zeros((0, 2)), np.zeros((0, 2))
    return np.concatenate(starts), np.concatenate(ends)


def _extent(pieces, y0, y1):
    """The leftmost and rightmost ink of the outline in `pieces` (_samples)
    in each unit of height from `y0` to `y1`: arrays of x, inf and -inf
    where there is none. A unit holds ink where the outline passes inside
    it, not where it only touches it: a cell's top is not ink in the unit
    above it."""
    left, right = np.full(y1 - y0, np.inf), np.full(y1 - y0, -np.inf)
    a, b = pieces
    lo, hi = np.minimum(a[:, 1], b[:, 1]), np.maximum(a[:, 1], b[:, 1])
    x0, x1 = np.minimum(a[:, 0], b[:, 0]), np.maximum(a[:, 0], b[:, 0])
    # to a millionth: a level edge worked out as a curve is a hair off its row
    first, last = np.floor(lo + 1e-6).astype(int), np.ceil(hi - 1e-6).astype(int) - 1
    for row in (first, first + 1):
        keep = (row <= last) & (row >= y0) & (row < y1)
        np.minimum.at(left, row[keep] - y0, x0[keep])
        np.maximum.at(right, row[keep] - y0, x1[keep])
    return left, right


def _near(xs, reach, right):
    """In each unit of `xs`, the leftmost (or rightmost) of those `reach`
    units away at most."""
    pad = np.full(reach, -np.inf if right else np.inf)
    padded, out = np.concatenate([pad, xs, pad]), xs.copy()
    for i in range(2 * reach + 1):
        out = (np.maximum if right else np.minimum)(out, padded[i : i + len(xs)])
    return out


def _shaper(font):
    """A HarfBuzz font of `font` as it is now, for its layout only: without
    outlines, which shaping does not read and take long to compile."""
    light = TTFont()
    light.setGlyphOrder(font.getGlyphOrder())
    for tag in ("head", "hhea", "maxp", "hmtx", "cmap", "GDEF", "GSUB", "GPOS"):
        if tag in font:
            light[tag] = font[tag]
    data = io.BytesIO()
    light.save(data)
    return uharfbuzz.Font(uharfbuzz.Face(uharfbuzz.Blob(data.getvalue())))


def _beside(font):
    """The lookups keeping fractions clear of what is set before and after
    them: every glyph of the merged font, kanji, kana, halfwidth kana,
    fullwidth forms, punctuation of both scripts and Latin. A glyph whose
    ink passes its advance (T V f in Italic) is no nearer a fraction after
    it than to the full-size digit (T1, with its kerning), unless that is
    further than the fraction would be were its ink to stop at its advance
    (T's bar no longer hangs over the numerator; _reaching); and no glyph
    touches a fraction, before or after it: a unit apart at least, a cell on
    a grid, where pixels touching at a corner read as one. Measured on the
    ink of each unit of height (_extent), the fraction as `frac` sets it.
    Glyphs already clear stay where they are: n1/3n is n⅓n.

    A contextual adjustment, not a side bearing: one large enough for T
    would loosen fractions beside every other glyph. It is on the
    fraction's own glyphs, which `frac` is on wherever it is on, the glyph
    beside it in context: the first numerator moves right after it, the
    last denominator's advance grows before it. HarfBuzz turns `frac` on
    only around ⁄ typed between digits (f7⁄8), not on what is beside. A
    first numerator is that of a fraction of one digit, before the slash
    (1/8), or more (12/8); a last denominator after the slash (7/1) or
    another (7/11), as far as either grows (_Parts.extra). A fraction drawn
    (⅓ ½ ℅) moves the glyph before it (kerned) and grows before that after.

    Glyphs go by class, those that need the same everywhere together, not
    a pair a glyph: how much one needs depends on its side towards the
    fraction only."""
    grid = _grid(font)
    g = grid or 1
    glyf, hmtx, cmap = font["glyf"], font["hmtx"], font.getBestCmap()
    hb, names = _shaper(font), font.getGlyphOrder()
    fraction, nums, dens = cmap[0x2044], PARTS["numr"], PARTS["dnom"]
    drawn = {
        cmap[cp]: (num + den)[0] for cp, (num, den) in (FRACTIONS | REDACTION).items() if cp in cmap
    }

    def shaped(text):  # [(glyph name, x, y)] of `text` set with `frac`, and its advance
        buf = uharfbuzz.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        uharfbuzz.shape(hb, buf, {"frac": True})
        placed, x = [], 0
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            placed.append((names[info.codepoint], x + pos.x_offset, pos.y_offset))
            x += pos.x_advance
        return placed, x

    def moved(placed, dx):
        return [(n, x + dx, y) for n, x, y in placed]

    # The sides of fractions, by (first glyph, what follows it) and (what
    # precedes it, last glyph): the glyphs set there, the end of the advance
    # of those that end it at 0, and the character of the full-size digit
    starts, ends = {}, {}
    for d in SUPERIORS:
        placed, _ = shaped(f"{d}/1")
        starts[nums[d], fraction] = placed[:2], d
        starts[nums[d], "numr"] = placed[:1], d
        placed, x = shaped(f"1/{d}")
        ends[fraction, dens[d]] = moved(placed[1:], -x)
        ends["dnom", dens[d]] = []
        for e in SUPERIORS:  # the last of two, as far as either grows
            placed, x = shaped(f"1/{e}{d}")
            ends["dnom", dens[d]] += moved(placed[2:], -x)
    for name, c in drawn.items():
        starts[name, None] = [(name, 0, 0)], c
        ends[None, name] = [(name, -hmtx[name][0], 0)]
    sampled = {
        key: _samples(font, placed)
        for key, placed in [*((k, p) for k, (p, _) in starts.items()), *ends.items()]
    }
    ys = np.concatenate([a[:, 1] for a, _ in sampled.values()])
    y0, y1 = math.floor(ys.min()) - MOST - 2, math.ceil(ys.max()) + MOST + 2
    lefts = np.array([_near(_extent(sampled[key], y0, y1)[0], g, False) for key in starts])
    rights = np.array([_near(_extent(sampled[key], y0, y1)[1], g, True) for key in ends])

    def cells(k):
        k = np.where(np.isfinite(k) & (k > 1e-9), k, 0)
        return np.ceil(k / g - 1e-9).astype(int) * g

    own = {n for forms in PARTS.values() for n in forms.values()}
    typed = {}
    for cp, name in sorted(cmap.items()):
        typed.setdefault(name, chr(cp))
    reaching = _Reaching(font, hb, starts, g)
    before, after = {}, {}
    for name in names:
        advance = hmtx[name][0]
        if name in own or not advance or not glyf[name].numberOfContours:
            continue
        left, right = _extent(_samples(font, [(name, 0, 0)]), y0, y1)
        k = cells((right - advance + g - lefts).max(axis=1))
        glyf[name].recalcBounds(glyf)
        if glyf[name].xMax > advance:
            k = np.maximum(k, reaching(name, typed.get(name)))
        before[name] = tuple(int(v) for v in k)
        after[name] = tuple(int(v) for v in cells((rights + g - left).max(axis=1)))
    return _beside_lookups(font, list(starts), list(ends), before, after)


class _Reaching:
    """How far each start of a fraction (_beside) moves after a glyph whose
    ink passes its advance: its ink no nearer than the full-size digit's is
    there, typed (with kerning), but no further than its usual air (the
    median for every digit), and touching nothing, a cell apart at least on
    a grid; within MOST units. Measured on the ink of each unit of height,
    as the drawn fractions were set before the merge."""

    def __init__(self, font, hb, starts, g):
        self.font, self.hb, self.g, self.profiles = font, hb, g, {}
        self.starts = {
            key: (_profile(_outline(font, placed), False), c) for key, (placed, c) in starts.items()
        }
        self.windows = {key: _window(first, MOST) for key, (first, _) in self.starts.items()}

    def profile(self, name, right):
        if (name, right) not in self.profiles:
            self.profiles[name, right] = _profile(_outline(self.font, [(name, 0, 0)]), right)
        return self.profiles[name, right]

    def full(self, text):  # how near a glyph and a character after it come, typed
        (a, xa, _), (b, xb, _) = _set(self.font, self.hb, text)[0]
        return _nearest(_shift(self.profile(a, True), xa), _shift(self.profile(b, False), xb))

    def __call__(self, name, char):
        g = self.g
        ink = _shift(self.profile(name, True), -self.font["hmtx"][name][0])
        nearest = {}
        out = []
        for key, (first, c) in self.starts.items():
            if _air(ink, self.windows[key]) >= MOST:
                out.append(0)
                continue
            need = g
            if char is not None:
                for e in [*SUPERIORS, c]:
                    if e not in nearest:
                        nearest[e] = self.full(char + e)
                usual = float(np.median([nearest[e] for e in SUPERIORS]))
                need = max(g, min(nearest[c], usual))
            k = _clearing(ink, first, need)
            out.append(math.ceil(k / g - 1e-9) * g if k > 1e-9 else 0)
        return np.array(out, dtype=int)


def _beside_lookups(font, starts, ends, before, after):
    """The lookups of _beside, from {glyph: how far each of `starts` moves
    after it} (`before`), and {glyph: how far the advance of each of `ends`
    grows before it} (`after`): a rule for each amount, on the fraction's
    glyphs that need it there, with what follows or precedes them, beside
    the glyphs that need it there. On a grid, a rule for each class too,
    glyphs that need the same everywhere: few, their coverages shared by
    the rules; smooth, those are many and small. An amount, in cells
    (units, smooth), is a sum of powers of two, the rule a single
    positioning for each, applied in turn: a handful of them, appended to
    the lookup list first, whatever the amounts. A fraction drawn moves the
    glyph before it where `frac` is on both: by a rule taking the pair on a
    grid; kerned by classes when smooth, where it needs many amounts, and
    after a fraction drawn, which a rule would pass over (½½½)."""
    gpos, order = font["GPOS"].table, font.getReverseGlyphMap()
    nums, dens = set(PARTS["numr"].values()), set(PARTS["dnom"].values())
    fraction = font.getBestCmap()[0x2044]
    grid = _grid(font)
    following = {fraction: {fraction}, "numr": nums}  # a first numerator, by what follows it
    preceding = {fraction: {fraction}, "dnom": dens}  # a last denominator, by what precedes it
    drawn = {first for first, after_it in starts if after_it is None}
    singles = {}

    def needing(needs, keys):
        """[(amount, its kinds, the fraction's glyphs, the glyphs beside)],
        from `needs`, for each of `keys`, (fraction's glyph, kind)."""
        classes = {}
        for name, k in needs.items():
            classes.setdefault(k, set()).add(name)
        out = {}
        for k, glyphs in classes.items():
            kinds = {}
            for (part, kind), amount in zip(keys, k):
                if amount:
                    kinds.setdefault((amount, part), set()).add(kind)
            parts = {}
            for (amount, part), ks in kinds.items():
                parts.setdefault((amount, frozenset(ks)), set()).add(part)
            for (amount, ks), ps in parts.items():
                apart = grid or None in ks  # a class: a pair's must not overlap
                key = amount, ks, frozenset(ps), min(map(order.get, glyphs)) if apart else 0
                out.setdefault(key, set()).update(glyphs)
        return [
            (amount, ks, ps, glyphs)
            for (amount, ks, ps, _), glyphs in sorted(
                out.items(),
                key=lambda kv: (
                    kv[0][0],
                    kv[0][3],
                    sorted(map(str, kv[0][1])),
                    sorted(map(order.get, kv[0][2])),
                ),
            )
        ]

    def applied(amount, placed):  # the single positionings `amount` sums
        cells, rest = divmod(amount, grid or 1)
        assert not rest, amount
        out = []
        for bit in range(cells.bit_length()):
            if cells >> bit & 1:
                value = (grid or 1) << bit
                if (value, placed) not in singles:
                    v = otl.buildValue(
                        {"XAdvance": value} | ({"XPlacement": value} if placed else {})
                    )
                    st = otl.buildSinglePosSubtable(dict.fromkeys(font.getGlyphOrder(), v), order)
                    gpos.LookupList.Lookup.append(otl.buildLookup([st]))
                    singles[value, placed] = SimpleNamespace(
                        lookup_index=len(gpos.LookupList.Lookup) - 1
                    )
                out.append(singles[value, placed])
        return out

    rules, kerned = otl.ChainContextPosBuilder(font, None), {}
    for amount, kinds, parts, glyphs in needing(before, starts):
        if None not in kinds:
            suffix = set().union(*(following[kind] for kind in kinds))
            rule = [[glyphs], [set(parts)], [suffix], [applied(amount, True)]]
            rules.rules.append(otl.ChainContextualRule(*rule))
            continue
        ruled = glyphs - drawn if grid else set()  # a fraction drawn: the glyph before it, kerned
        if ruled:
            rule = [[], [ruled, set(parts)], [], [applied(amount, False), None]]
            rules.rules.append(otl.ChainContextualRule(*rule))
        if paired := tuple(sorted(glyphs - ruled, key=order.get)):
            value = otl.buildValue({"XAdvance": amount}), None
            kerned.update({(paired, (part,)): value for part in parts})
    lookups = [rules.build()] if rules.rules else []
    if kerned:
        lookups.append(otl.buildLookup([otl.buildPairPosClassesSubtable(kerned, order)]))
    rules = otl.ChainContextPosBuilder(font, None)
    for amount, kinds, parts, glyphs in needing(after, [(last, prev) for prev, last in ends]):
        prefix = [] if None in kinds else [set().union(*(preceding[kind] for kind in kinds))]
        rule = [prefix, [set(parts)], [glyphs], [applied(amount, False)]]
        rules.rules.append(otl.ChainContextualRule(*rule))
    if rules.rules:
        lookups.append(rules.build())
    return lookups


def _frac(font):
    """`frac`, its lookups first, so that it sets fractions before `numr`,
    `dnom`, `sups`, `subs`, `sinf`, `ordn` and `tnum` turn their digits into
    other forms. A slash is / or ⁄ alike: HarfBuzz turns `frac` on around ⁄
    typed between digits, and `numr` before it and `dnom` after it. In five
    steps, none bounded in length:
    1. digits after a slash after a digit become denominators, and digits
       after those, forward, as far as they go;
    2. digits before a slash before a denominator become numerators, and
       digits before those, in reverse, from the end of the text back (a
       reverse chaining lookup sees the glyphs after it already changed);
    3. a run of two slashes or more turns back as typed, in reverse: a
       denominator before a slash, a numerator before a slash before a
       digit, and a part before a digit as typed, back to the run's start;
    4. then forward: a numerator after a slash, a denominator after a slash
       after a digit, and a part after a digit as typed, on to its end;
    5. / between a numerator and a denominator becomes ⁄.
    In a fraction, parts never stand next to digits as typed, so only a run
    turned back has them. And last of all lookups, after `numr` and `dnom`:
    6. the forms they give (NUMR, DENOMINATORS) next to ⁄, and next to
       those, turn back as typed, before it in reverse and after it
       forward: only a run with ⁄ turned back has them there, given by the
       shaper's `numr` and `dnom` around ⁄ (1/2⁄3), which `frac` would
       otherwise leave half set.

    In vertical text (`vert` and `vrt2`, between steps 4 and 5), a fraction
    there is a glyph for, Kuronuri's or MCKL's (⅓ ½), becomes that glyph, as
    with Redaction's `frac`; any other is set as typed, digits and slash
    upright, an em each, as before `frac` set fractions of parts: those
    parts are an em apart there too, and a fraction across a column is the
    application's to set (text-combine-upright), horizontally, where `frac`
    sets it as here."""
    gsub, cmap = font["GSUB"].table, font.getBestCmap()
    digits = {cmap[ord(d)] for d in "0123456789"}
    slash, fraction = cmap[ord("/")], cmap[ord("⁄")]
    slashes = {slash, fraction}
    numerators = {cmap[ord(d)]: name for d, name in PARTS["numr"].items()}
    denominators = {cmap[ord(d)]: name for d, name in PARTS["dnom"].items()}
    nums, dens = set(numerators.values()), set(denominators.values())
    typed = {name: d for forms in (numerators, denominators) for d, name in forms.items()}
    alone = {name: cmap[ord(d)] for forms in (NUMR, DENOMINATORS) for d, name in forms.items()}
    # The fractions there is a glyph for, of parts, for vertical text
    whole = otl.LigatureSubstBuilder(font, None)
    for cp, (num, den) in (FRACTIONS | REDACTION).items():
        if (num + den).isdigit() and den:
            for s in (slash, fraction):  # in this order, every build
                parts = (*(PARTS["numr"][c] for c in num), s, *(PARTS["dnom"][c] for c in den))
                whole.ligatures[parts] = cmap[cp]
    singles = [
        otl.buildLookup([otl.buildSingleSubstSubtable(mapping)])
        for mapping in ({slash: fraction}, denominators, typed, alone)
    ]
    bar, dnom, back, again = (
        SimpleNamespace(lookup_index=i)
        for i in layout.insert_lookups(gsub, [*singles, whole.build()], 0)[:-1]
    )
    whole.lookup_index = len(singles)

    def chain(*rules):
        builder = otl.ChainContextSubstBuilder(font, None)
        builder.rules = [otl.ChainContextualRule(*rule) for rule in rules]
        return builder.build()

    def reverse(*rules):  # (glyphs, glyphs after them), each its own subtable
        builder = otl.ReverseChainSingleSubstBuilder(font, None)
        builder.rules = [
            ([], suffix, {k: v for k, v in mapping.items() if k in glyphs})
            for glyphs, suffix, mapping in rules
        ]
        return builder.build()

    vertical = [[[nums], [nums], [], [None]]]  # from its first numerator
    for parts in sorted(whole.ligatures, key=len, reverse=True):
        glyphs = [{g} for g in parts]
        vertical.append([[], glyphs, [dens], [None] * len(parts)])  # not its last denominator
        vertical.append([[], glyphs, [], [[whole]] + [None] * (len(parts) - 1)])
    steps = [
        chain(
            [[digits | dens, slashes], [digits], [], [[dnom]]],
            [[dens], [digits], [], [[dnom]]],
        ),
        reverse(
            (digits, [slashes, dens], numerators),
            (digits, [nums], numerators),
        ),
        reverse(
            (dens, [slashes], typed),
            (nums, [slashes, digits], typed),
            (nums | dens, [digits], typed),
        ),
        chain(
            [[slashes], [nums], [], [[back]]],
            [[digits, slashes], [dens], [], [[back]]],
            [[digits], [nums | dens], [], [[back]]],
        ),
        chain(*vertical),
        otl.buildLookup([otl.buildSingleSubstSubtable(typed)]),
        chain([[nums], [{slash}], [dens], [[bar]]]),
    ]
    indices = layout.insert_lookups(gsub, steps, len(singles) + 1)
    # 6, after every other lookup: `numr` and `dnom` are Redaction's and
    # add_glyphs'
    gsub.LookupList.Lookup += [
        reverse((set(alone), [{fraction}], alone), (set(alone), [digits], alone)),
        chain([[{fraction}], [set(alone)], [], [[again]]], [[digits], [set(alone)], [], [[again]]]),
    ]
    last = len(gsub.LookupList.Lookup)
    for rec in gsub.FeatureList.FeatureRecord:
        if rec.FeatureTag == "frac":
            rec.Feature.LookupListIndex = [*indices[:4], indices[6], last - 2, last - 1]
    for tag in ("vert", "vrt2"):
        layout.use_lookups(gsub, tag, [gsub.LookupList.Lookup[i] for i in indices[4:6]])
