"""Enclosed numbers and letters drawn from Redaction's own: ① Ⓐ ❶ ⓵ 🄰 🅰 🆒,
and ⑴ ⒈ 🄁 🄯.

The enclosures are rings (①), two rings (⓵), discs (❶), squares (🄰) and
blocks (🅰), as thin as Redaction's minus, as its other signs are thin. They
sit where Noto Serif JP's ring does: across the em (but a cell from its
sides on a grid), centred on the ideographic em box, as Japanese text
expects. Their content is Redaction's glyphs as typed, the same size
across a family: as tall as the x-height for digits, or less if the
widest would not fit (⑳), and centred between their middle and the middle
of their ink, so ④, heavier on the right, looks centred. Words (🆒 COOL)
are each as big as fits. Discs and blocks are cut out by their content.
Japanese stays upright in italic, and so do enclosures, around italic
content.

Content is Redaction's own in every style, scaled and placed, made
heavier so the stems of its n, I or 1 (_of: I with a capital, n with
lowercase alone, else 1) are WEIGHT times as heavy against its n as the
heaviest style draws them, at the size upright styles draw them, and at
least K of its n at the size it is drawn, or, smaller than circled
numbers, as heavy as those (_plan): no style is thinned, and every style
is as heavy against its own n, so Bold's content is as much heavier than
Regular's as Redaction's Bold is. Heavier as Redaction's Bold is of its
Regular, where its outlines allow (shapes.blend, _blended): Regular's
towards Bold, Bold's past it, Italic's the upright way, slanted, so its
carving is MCKL's own. A glyph that does not blend so far (Italic's
lowercase, Q W w y, Bold's g s) is thickened all round (_thick: offset as
shapes.embolden does, dots scaled), no further than its carving stays
half open and its counters and pieces stay (_cap), lowercase no further
than its style's carved lowercase goes (_limit). Where that narrows
MCKL's carving (Q W in every style, Italic's R and lowercase, Regular's
w y, Bold's g s w y), it is drawn by hand instead, saved in DRAWN
(by_hand): as heavy, its slits and the gap of Q's tail cut open again,
as wide as MCKL's, and so the notches shapes.grooves does not take for
carving (Bold's s's top slot, its g's ear, cut as its y's tail). Italic's
R and W, lighter so than its capitals that blend, are then moved further,
as Redaction's upright R and W are from Regular to Bold, slanted, as far
as makes them as heavy as those: their slits move with them as Bold's
do, their tips (W's, R's tail) as pointed as Redaction's. Bold's 🄫 🄬
are Italic's C R, as heavy as Bold's content where they blend (C); its R,
Italic's drawn, is moved further still for Bold alone (by_hand, slanted),
as heavy as its Ⓡ, its slits as much wider than Redaction's as Bold's
are of Regular's: so _heavy knows the style of the enclosure.
Each glyph is shrunk back as tall as its own. Glyphs are spaced as near as
typed where their ink comes nearest, any way (_nearest); figures as far
apart as they look on average, all alike (_optically). Content is as big
as it fits typed in Redaction's Bold, upright, in every style, or smaller
where a style's own is wider (Italic's M): words take the room their
weight adds, up to ROOM, sets too, all together; a glyph nearer its
enclosure than CLEAR of its stroke is fitted alone, centred as the rest
(⓾): its figures nearer, narrowed, then shrunk. Lines (Hi-/Res) are set
one under the other, centred on their box. On a grid (PHASED), a number
or a letter is pixelated apart from its enclosure, where in a cell it
falls best, its stems filling cells first (shapes.phased); words are
pixelated with it, which keeps more of their counters and their letters
off it. On 35 to 70 (EASED), where its pixels lose a piece or a counter,
or a stroke thinner than a cell drops out, it is emboldened a little
(_ease). On 70, lowercase is placed, and emboldened, as like its smooth
drawing as its pixels come (_liken); on 35 to 70, a few that read as
other glyphs are drawn as before group 4 (EMBOLDENED), pixelated with
their enclosure, and where that ran into it too (Bold's 🅆 Ⓦ, Italic's 🅆
on 70), they are drawn by hand, cell by cell (CELLS, by_cells), as are a
few drawn anew by hand that pixelate worse than before (Bold's ⓖ on 70,
Regular's ⓨ on 50), as before. On 100
(COARSEST), all content is emboldened: from Bold thinned in an upright
Regular, which keeps its carving.

Parenthesized and full stop forms (⑴ ⒈ 🄁) are Redaction's glyphs as typed
(components), as the Roman numerals are, and 🄯 is its © turned over, so in
the numbered variants they keep MCKL's pixels.
"""

import functools
import math
import unicodedata

import numpy as np
import pathops
from fontTools.pens.statisticsPen import StatisticsPen
from fontTools.pens.ttGlyphPen import TTGlyphPen

import pixel
from family import STYLES, log, redaction

from .shapes import (
    SHIFTS,
    THIN,
    _pieces,
    _placed,
    _set,
    _shaper,
    add,
    blend,
    cells,
    circle,
    content,
    drawn,
    drawn_cells,
    embolden,
    glyph,
    grooves,
    masters,
    path,
    phased,
    pixelate_glyphs,
    rect,
    runs,
    shaper,
    shrunk,
    stem,
    typed,
    union_paths,
    widths,
)

# Content drawn by hand (by_hand), in DRAWN: each glyph Redaction's own made
# heavier, its lib saying how far
AMOUNT = "com.lihbr.kuronuri.amount"  # how far out a drawn glyph's outline was moved
# Enclosed glyphs drawn by hand on a grid, cell by cell (by_cells), in DRAWN
CELLS = "cells.txt"
# Least a drawn glyph is thinned by in a word (_heavy): _plan rounds its amount,
# and thinned by a hair, skia-pathops lost the curve under Italic's k's serif
HAIR = 0.1
RADIUS = 462  # of the ring, as in Noto Serif JP
CENTRE = 380  # of the ideographic em box (-120..880)
SQUARE = 0.86  # half the side of squares, over the radius of rings: they look as big
FIT = 0.8  # of the width inside the enclosure, that content may take
# of it, that content made heavier, wider, may take: as far as emboldened words
# came before (🆜, ㏑)
ROOM = 0.9
# Enclosures heavier content is kept half a stroke from, and those it is cut out of
ENCLOSING = ("ring", "double", "disc", "square", "block", "boxring")
NEGATIVE = ("disc", "block", "crossed")
LINES = 1.25  # cap heights between the lines of content (Hi-/Res), as content() sets them
# Least stems of its n, I or 1 content has, of those of n at the size it is
# drawn, in every style: Redaction's own are 0.54 (Bold's n, in ㎏) to 0.58
# (Bold's 1, in ①). Its carving takes 3 to 4.5 units all round before it is
# half closed (OPEN): at 0.75, the owner's first aim, every carved figure
# and lowercase letter closed, at 0.58 Bold's ㎏ ㎚ ... were capped
K = 0.56
# How much heavier than that content is, in every style: at 1, as approved
# in 1b3befc, the owner found it light, its figures' carving shy
WEIGHT = 1.15
# least of each gap of its carving content keeps thickened (_cap): more
# closed, Redaction's slits read as hairlines, Italic's a, Bold's g first
OPEN = 0.5
# of n's stem: pieces of content no bigger both ways (the dot of i, a full
# stop) are scaled as much as it is thickened, not thickened (_thick)
DOT = 2
# how near figures come, and how narrow, for content to fit its enclosure alone (⓾)
TIGHT = (1, 0.8, 0.6)
# how near figures come, of their nearest ink typed, spaced as they look
NEAREST = 0.7
ACROSS = (1, 0.98, 0.96, 0.94, 0.92)
# least of its stroke content keeps off its enclosure (⓾ at half stood crowded)
CLEAR = 0.75
SPACED = 300  # farthest glyphs are spaced by their nearest ink, not their boxes
# Of a cell, how far off centre content may stand on a grid to fit off its
# enclosure, as phasing it moves it anyway
SLACK = 0.5
INK = 0.5  # how far content is centred on the middle of its ink, from 0 to 1
# Coarsest grid digits and capitals are thickened on: on 100, abstract, their
# hairlines are under half a cell and drop out, letters with them (㍳)
COARSEST = 70
# Grids numbers and letters are placed on apart, where in a cell they fall
# best
PHASED = (10, 20, 35, 50, 70)
# Grids numbers and letters are emboldened on where their pixels lose a
# piece or a counter (_pixelated), by EASE of the way to n's stems at a time
EASED = (35, 50, 70)
EASE = 0.1
# Grids lowercase is emboldened and placed on as like the smooth font's as
# its pixels come (_liken)
LIKENED = (70,)
# Content drawn on a grid as before group 4, emboldened and pixelated with
# its enclosure: thickened, or as drawn, it reads as other glyphs, where so
# it did not. On 70, lowercase as like the smooth font's as it comes
# (_liken). Re-checked thickened (round 7): Regular's ㎢ as km³ and ㏇'s full
# stop a comma on 35, 🅊 as KV on 50, 🅸 as ], Ⓗ as K, Ⓜ as x, ⑧ ➇ as 6,
# 🆒 all but gone on 70, and, lighter, the words of 🆋–🆏, cut out thinner
# than a cell, broken on 50 and gone on 70, as Italic's and Bold's are; its
# ㉈–㉌ and 🅦 read without, and, WEIGHT heavier (round 8), ③ ➂ on 70, as
# before a J. Re-checked WEIGHT heavier, the rest still read as said, and
# on 70 Italic's c reads as <, z as C, Bold's I as [, R as A.
# Italic's ㏞ V/m in two, ㎮'s slash lost, ㎧ ㎨ their slash's foot, on 35
# and 50; on 50, ㎨ broken, ⓛ ⓣ as / and !, ④ as ≠ (its ㉊ reads without);
# on 70, its e as ρ, h as λ, f without its bar, 🄼 and the letters of ㎁ ㎃
# ㎄ ㎫ broken; Bold's Ⓜ as Ж, ⓗ a wedge on 70; the words of 🆋–🆏 gone on
# 50 (Italic's) and 70. Re-checked drawn by hand (by_hand), on 70: Italic's
# x as И, Regular's 🅆 as ?V; Italic's e h f z still read as said. The R
# of Regular's and Italic's 🄬 reads as Л, but as before it ran into its
# enclosure, as Regular's 🅦 blots. Bold's 🅆 read as P, its Ⓦ as TV,
# Italic's 🅆 as T over v, and ran into theirs as before: they are drawn
# by hand, cell by cell (by_cells).
EMBOLDENED = {
    35: {"Regular": "㎢㏇", "Italic": "㏞㎮㎧㎨"},
    50: {"Regular": "🅊🆋🆌🆍🆎🆏", "Italic": "㎮㎨ⓛⓣ④🆋🆌🆍🆎🆏"},
    70: {
        "Regular": "🅸ⒽⓂ⑧➇🆋🆌🆍🆎🆏🆒🅆",
        "Italic": "ⓔⓗⓕⓒⓩⓧ🄼㎁㎃㎄㎫🆋🆌🆍🆎🆏",
        "Bold": "ⓂⓗⒾⓇ🆋🆌🆍🆎🆏",
    },
}


def _name(cp):
    return f"uni{cp:04X}" if cp <= 0xFFFF else f"u{cp:05X}"


def _run(start, contents):
    return {start + i: c for i, c in enumerate(contents)}


DIGITS = [str(i) for i in range(1, 51)]


def _squared():
    """{code point: text} of the squared Latin words of Unicode (㎏ ㍱ ㋌)
    whose letters Redaction all has: as decomposed, ∕ as /."""
    letters = set(redaction(None, "Regular").getBestCmap())
    squared = {}
    for cp in [0x3250, *range(0x32CC, 0x32D0), *range(0x3371, 0x33E0), 0x33FF]:
        tag, *parts = unicodedata.decomposition(chr(cp)).split() or [""]
        text = "".join(chr(int(c, 16)) for c in parts).replace("∕", "/")
        if tag == "<square>" and all(ord(c) in letters for c in text):
            squared[cp] = text
    return squared


SQUARED = _squared()
UPPER = [chr(c) for c in range(ord("A"), ord("Z") + 1)]
LOWER = [c.lower() for c in UPPER]
# (enclosure, {code point: content}, each content as big as fits, content in italic)
# Circled numbers (① ㊿): the size of digits, as big as the widest fits
NUMBERS = (
    _run(0x2460, DIGITS[:20])
    | _run(0x3251, DIGITS[20:35])
    | _run(0x32B1, DIGITS[35:50])
    | _run(0x2780, DIGITS[:10])
    | {0x24EA: "0", 0x1F10B: "0"}
)
ENCLOSURES = [
    ("ring", NUMBERS, False, False),
    ("ring", _run(0x24B6, UPPER) | _run(0x24D0, LOWER), False, False),
    ("ring", {0x1F12D: "CD", 0x1F12E: "Wz"}, True, False),
    ("ring", {0x1F12B: "C", 0x1F12C: "R"}, False, True),
    ("double", _run(0x24F5, DIGITS[:10]), False, False),
    (
        "disc",
        _run(0x2776, DIGITS[:10])
        | _run(0x278A, DIGITS[:10])
        | _run(0x24EB, DIGITS[10:20])
        | {0x24FF: "0", 0x1F10C: "0"},
        False,
        False,
    ),
    ("disc", _run(0x1F150, UPPER), False, False),
    ("square", _run(0x1F130, UPPER), False, False),
    (
        "square",
        _run(0x1F14A, ["HV", "MV", "SD", "SS", "PPV", "WC"])
        | _run(
            0x1F191,
            ["CL", "COOL", "FREE", "ID", "NEW", "NG", "OK", "SOS", "UP!", "VS", "3D"],
        )
        | {0x1F19C: "2nd\nScr"}
        | _run(0x1F19D, ["2K", "4K", "8K", "5.1", "7.1", "22.2", "60P", "120P", "d"])
        | _run(0x1F1A6, ["HC", "HDR", "Hi-\nRes", "Loss\nless", "SHV", "UHD", "VOD"]),
        True,
        False,
    ),
    # Square words, as ㌀, without a square: Latin ones (units: ㎏ ㎑), what
    # Redaction has all the letters of
    ("none", {0x1F190: "DJ"} | SQUARED, True, False),
    ("boxring", _run(0x3248, [str(10 * i) for i in range(1, 9)]), False, False),
    ("raised", {0x1F16A: "MC", 0x1F16B: "MD", 0x1F16C: "MR"}, False, False),
    ("block", _run(0x1F170, UPPER), False, False),
    ("block", _run(0x1F18B, ["IC", "PA", "SA", "AB", "WC"]), True, False),
    ("crossed", {0x1F18A: "P"}, False, False),
]
# code point: the text it is, as typed
TYPED = (
    _run(0x2474, [f"({d})" for d in DIGITS[:20]])
    | _run(0x249C, [f"({c})" for c in LOWER])
    | _run(0x1F110, [f"({c})" for c in UPPER])
    | _run(0x2488, [f"{d}." for d in DIGITS[:20]])
    | {0x1F100: "0."}
    | _run(0x1F101, [f"{d}," for d in range(10)])
)
COPYLEFT = 0x1F12F
ENCLOSED = {cp for _, contents, _, _ in ENCLOSURES for cp in contents}
CODEPOINTS = {cp: _name(cp) for cp in sorted({*ENCLOSED, *TYPED, COPYLEFT})}
ALTERNATES = []
SAMPLES = [
    "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳",
    "❶❷❸ ⓫⓬⓴ ⓵⓶⓾ ⓪⓿",
    "ⒶⒷⒸ ⓐⓑⓒ 🅐🅑🅒",
    "🄰🄱🄲 🅰🅱🅲 🆊🆋",
    "🆒🆓🆕🆗🆘🆙 🆜 🆩",
    "⑴⑵⑶ ⒜⒝⒞ 🄐🄑🄒",
    "⒈⒉⒊ 🄀🄁🄂 🄫🄬🄯",
    "手順①と② ⑴と⑵",
]


def blends(text):
    """Whether `text` is drawn heavier (heavier): all content is, letters,
    figures and their punctuation."""
    return any(c.isalnum() for c in text)


def heavier(font, text, plan, tight=1, style=None):
    """`text` in `font` (smooth), Redaction's own, each glyph made heavier
    as `plan` says (_heavy), for an enclosure of `style`, spaced as typed around their own ink
    (_spaced), its lines (Hi-/Res) one under the other, as content() sets
    them, each centred on x = 0, each glyph as tall as `font`'s: its n, I
    or 1 (_of) as tall as drawn, its letters all one height."""
    out = pathops.Path()
    for i, line in enumerate(text.split("\n")):
        p = _spaced(font, line, plan, _of(text), tight, style)
        down = i * font["OS/2"].sCapHeight * LINES
        out.addPath(p.transform(1, 0, 0, 1, -(p.bounds[0] + p.bounds[2]) / 2, -down))
    return pathops.op(out, pathops.Path(), pathops.PathOp.UNION)


def _spaced(font, line, plan, of, tight=1, style=None):
    """`line` of `font`, each glyph made heavier (_heavy), its ink as near
    the last's as typed (_nearest): heavier, glyphs grow wider than their
    advances, and toward each other where they come nearest, not where
    their boxes do (Bold's 4 ran into ㊷'s 2, a 1's foot into ⓫'s other
    1)."""
    out, last = pathops.Path(), None
    for (char, (_, x, y)), was in zip(
        zip(line, _set(font, _shaper(font), line)[0]), _typed(font, line)
    ):
        if path(font, char).bounds == (0, 0, 0, 0):  # a space
            continue
        p = _heavy(font, char, plan, of, style)[0].transform(1, 0, 0, 1, x, y)
        if last is not None and line.isdigit():
            # Figures, as far apart as they look on average, all alike, but
            # no nearer than NEAREST of their nearest ink typed: ㉔'s 4 ran
            # under its 2
            moved = _optically(last, p, _apart(font) * tight)
            near = was[0]
            if near is not None:
                try:
                    slid = _slid(embolden(last, near * NEAREST, round=True), p)
                except pathops.PathOpsError:
                    slid = None
                moved = moved if slid is None else min(moved, slid)
            p = p.transform(1, 0, 0, 1, -moved, 0)
        elif last is not None:
            near, box = was
            # Moved along till it comes as near the last as typed, or their
            # boxes as far apart where their ink is far (a full stop)
            try:
                slid = None if near is None else _slid(embolden(last, near, round=True), p)
            except pathops.PathOpsError:  # boxes apart, where skia-pathops fails
                slid = None
            if slid is None:
                slid = p.bounds[0] - last.bounds[2] - box
            p = p.transform(1, 0, 0, 1, -slid, 0)
        out.addPath(p)
        last = p
    return pathops.op(out, pathops.Path(), pathops.PathOp.UNION)


@functools.cache
def _apart(font):
    """How far apart, on average across, two figures of `font` are typed
    (_across), over their height: the middle of all from 10 to 50. Typed or
    by their nearest ink, ㉔ looked far looser than ㉕."""
    gaps = []
    for n in range(10, 51):
        line = str(n)
        (_, x0, y0), (_, x1, y1) = _set(font, _shaper(font), line)[0]
        a = path(font, line[0]).transform(1, 0, 0, 1, x0, y0)
        b = path(font, line[1]).transform(1, 0, 0, 1, x1, y1)
        rights, lefts, tall = _across(a, b)
        gaps.append(_gap(rights, lefts, tall, 0) / tall)
    return sorted(gaps)[len(gaps) // 2]


def _across(a, b, rows=24):
    """The right edges of `a` and left edges of `b` on rows where both have
    ink, and how tall they are together."""
    y0, y1 = max(a.bounds[1], b.bounds[1]), min(a.bounds[3], b.bounds[3])
    rights, lefts = [], []
    for i in range(rows):
        y = y0 + (y1 - y0) * (i + 0.5) / rows
        ra, rb = runs(a, y=y), runs(b, y=y)
        if ra and rb:
            rights.append(ra[-1][1])
            lefts.append(rb[0][0])
    return (
        np.array(rights),
        np.array(lefts),
        max(a.bounds[3], b.bounds[3]) - min(a.bounds[1], b.bounds[1]),
    )


def _gap(rights, lefts, tall, moved):
    """How far apart across, on average, with `b` moved left by `moved`:
    each row no further than 0.3 `tall`, as an eye sees it."""
    return np.clip(lefts - moved - rights, 0, 0.3 * tall).mean()


def _optically(a, b, apart):
    """How far `b` moves left for it and `a` to be `apart` of their height
    apart, on average across (_gap)."""
    rights, lefts, tall = _across(a, b)
    if not len(rights):
        return 0
    lo, hi = -tall, tall  # moved left
    for _ in range(30):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if _gap(rights, lefts, tall, mid) > apart * tall else (lo, mid)
    return (lo + hi) / 2


@functools.cache
def _typed(font, line):
    """How near each glyph of `line` in `font` comes to the last as typed,
    and how far their boxes are apart: (nearest, across), None for the
    first and spaces; nearest None where it is far (_nearest)."""
    out, last = [], None
    for char, (_, x, y) in zip(line, _set(font, _shaper(font), line)[0]):
        p = path(font, char)
        if p.bounds == (0, 0, 0, 0):
            out.append(None)
            continue
        p = p.transform(1, 0, 0, 1, x, y)
        out.append(None if last is None else (_nearest(last, p), p.bounds[0] - last.bounds[2]))
        last = p
    return out


def _touch(a, b):
    return abs(pathops.op(a, b, pathops.PathOp.INTERSECTION).area) > 1


def _nearest(a, b, far=SPACED):
    """How near the ink of `b` comes to `a`'s, any way: as typed, ㉔'s 2
    comes nearest the 4 below its bar, not across. None past `far`."""
    if not _touch(embolden(a, far, round=True), b):
        return None
    lo, hi = 0, far
    while hi - lo > 0.5:
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if _touch(embolden(a, mid, round=True), b) else (mid, hi)
    return lo


def _slid(a, b, step=16):
    """How far `b` moves left, from where it is, till its ink touches `a`'s
    (on its left): less than 0, right. None if it never does."""
    lo = b.bounds[0] - a.bounds[2]  # their boxes side by side, apart
    end = lo + (a.bounds[2] - a.bounds[0]) + (b.bounds[2] - b.bounds[0])
    d = lo
    while d < end and not _touch(a, b.transform(1, 0, 0, 1, -(d + step), 0)):
        d += step
    if d >= end:
        return None
    hi = d + step  # touches there, not at d
    while hi - d > 0.5:
        mid = (d + hi) / 2
        d, hi = (d, mid) if _touch(a, b.transform(1, 0, 0, 1, -mid, 0)) else (mid, hi)
    return d


def _of(text):
    """The glyph whose stems `text` is made heavier by: I if it has a
    capital (℡), else n if it has a lowercase letter, else 1."""
    if any(c.isupper() for c in text):
        return "I"
    return "n" if any(c.islower() for c in text) else "1"


@functools.cache
def _font(style):
    return redaction(None, style)


@functools.cache
def _own(style, slanted, of):
    """The stems of `of` over those of n in `style` of Redaction, as drawn:
    of its Italic for slanted content (🄫 🄬)."""
    font = _font("Italic" if slanted else style)
    return stem(path(font, of)) / stem(path(font, "n"))


def _plan(font, text, scale, shared, floor, n, slanted):
    """How `text` of `font` is made heavier (_heavy), for the stems of its
    n, I or 1 (_of), as tall as drawn, to be WEIGHT times as heavy against
    `n`, those of n of the style drawn, at `scale`, as the heaviest of
    Redaction's styles draws them at `shared`, the size upright styles draw
    it (Italic's M is smaller), and at least K of `n`: so they are as heavy
    in every style, and none is thinned. Smaller than `floor` (circled
    numbers), as heavy as those. (t, amount, stems): its glyphs blended by
    t (_blended), those that do not, thickened by amount, as far as their
    carving and counters stay open (_limit), and the stems of its n, I or 1
    so. Also how much it would be thickened uncapped."""
    of = _of(text)
    own = max(_own(style, slanted, of) for style in STYLES)
    stems = n * WEIGHT * max(K, own * max(shared, floor)) / max(scale, floor)
    s, h = stem(path(font, of)), _height(font, of)
    regular, bold = masters()
    ds = stem(path(bold, of)) - stem(path(regular, of))
    dh = _height(bold, of) - _height(regular, of)
    # (s + t ds) h / (h + t dh) = stems
    t = max(0, h * (stems - s) / (ds * h - stems * dh))
    # (s + 2 a) h / (h + 2 a) = stems
    want = max(0, (stems - s) * h / (2 * (h - stems)))
    style = font["name"].getDebugName(2)
    chars = [c for c in text if c != "\n" and path(font, c).bounds[2]]
    thick = [c for c in chars if _blended(font, c, t) is None]
    # All as much, as far as each goes (_limit), so a word is one weight
    amount = min([want] + [_limit(style, c) for c in thick])
    now = max(s, stems)
    if _blended(font, of, t) is None:
        now = (s + 2 * amount) * h / (h + 2 * amount)
    return (round(t, 4), round(amount, 2), now), want


@functools.cache
def _limit(style, char):
    """Most `char` of `style`, that does not blend, is thickened by: as far
    as its carving stays half open (_cap), and lowercase no further than
    its style's carved lowercase goes (_most): Italic's c i l o s,
    uncarved, stood out of its lowercase."""
    return min(_cap(style, char), _most(style) if char.islower() else math.inf)


@functools.cache
def _most(style):
    """Most a lowercase letter of `style` with carving (shapes.grooves) is
    thickened by (_cap)."""
    font = _font(style)
    return max(_cap(style, c) for c in LOWER if grooves(path(font, c)))


@functools.cache
def _blended(font, char, t):
    """`char` of `font` blended by `t` (shapes.blend: past Bold for Bold,
    the upright way slanted for Italic), as tall as drawn, or None where it
    does not blend so far: its outlines do not match Redaction's Regular
    and Bold, it folds, or its carving closes. As drawn where `t` is 0."""
    if not t:
        return path(font, char)
    regular, bold = masters()
    for sliver in (False, True):
        try:
            p = blend(font, regular, bold, char, t, sliver)
        except (ValueError, pathops.PathOpsError):
            # Or slivers, which skia-pathops leaves where edges nearly meet,
            # are taken for carving (Bold's H)
            continue
        return p
    return None


@functools.cache
def by_hand(style, slanted=False):
    """{character: (outline, amount)} of the glyphs of `style` drawn by hand
    (DRAWN): Redaction's own made heavier, its outline moved out by
    `amount`, as thickened, but its carving cut open again as MCKL cut it,
    which thickening narrows (Italic's lowercase, Q W w y, Bold's g s),
    and Italic's R W moved further as blending moves the upright glyph, as
    tall. Or, `slanted`, those of its Italic drawn for `style` (Bold's 🄬):
    Italic's R moved further still, as heavy as `style`'s capitals."""
    return {c: (p, lib[AMOUNT]) for c, (p, lib) in drawn(style, slanted).items() if AMOUNT in lib}


def _by_hand(font, char, style=None):
    """`char` of `font` drawn by hand (by_hand), or None: for an enclosure
    of `style`, another than `font`'s (Bold's 🄬, of Italic's R), as drawn
    for it, if it is."""
    own = font["name"].getDebugName(2)
    if style not in (None, own) and char in by_hand(style, True):
        return by_hand(style, True)[char]
    return by_hand(own).get(char)


def _heavy(font, char, plan, of, style=None):
    """`char` of `font` made heavier as `plan` says (_plan), as tall as its
    own (`of` of `font` as tall as drawn), in an enclosure of `style`, and
    how: drawn by hand (by_hand, for `style`), blended (_blended), or where
    it does not blend, thickened (_thick).

    A glyph drawn by hand is as heavy as `char` thickened as far as it goes
    (_limit), Italic's R W as heavy as its capitals blended (by_hand),
    which every enclosure of it alone draws it; in a word thickened
    less, as the letters with it go (㎦ km³: as far as ³), it is thinned by
    as much, which opens its carving more."""
    t, amount, _ = plan
    h = _height(font, of)
    hand = _by_hand(font, char, style)
    if hand is not None:
        p, moved = hand
        less = amount - _limit(font["name"].getDebugName(2), char)
        less = less if less < -HAIR else 0
        k = h / (h + 2 * (moved + less))
        return embolden(p, less).transform(k, 0, 0, k, 0, 0), "drawn"
    p = _blended(font, char, t) if t else None
    if p is not None:
        regular, bold = masters()
        dh = _height(bold, of) - _height(regular, of)
        k = h / (h + t * dh)
        return p.transform(k, 0, 0, k, 0, 0), "blended"
    k = h / (h + 2 * amount)
    return _thick(font, char, amount).transform(k, 0, 0, k, 0, 0), "thickened"


@functools.cache
def _cap(style, char):
    """Most `char` of `style` of Redaction is thickened by (_thick), each gap
    of its carving (shapes.grooves) at least OPEN open, its pieces and
    counters kept: further, its slits close (Regular's 2 3 5 near 10,
    Italic's a d u near 8)."""
    font = _font(style)
    p, most = path(font, char), 2 * stem(path(font, "n"))
    gaps, pieces = [g for g, _ in grooves(p)], _pieces(p)

    def kept(a):
        q = _thick(font, char, a)
        return _pieces(q) == pieces and all(
            abs(pathops.op(g, q, pathops.PathOp.DIFFERENCE).area) >= OPEN * abs(g.area)
            for g in gaps
        )

    lo, hi = 0, most
    if kept(hi):
        return hi
    while hi - lo > 0.25:
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if kept(mid) else (lo, mid)
    return lo


@functools.cache
def _thick(font, char, amount):
    """`char` of `font` thickened by `amount` all round (shapes.embolden),
    but its dots, no bigger than DOT stems of n both ways (of i, j, !, a
    full stop), scaled about their middle as much as they would be
    thickened across, so they keep their shape."""
    p = path(font, char)
    if amount <= 0:
        return p
    contours = list(p.contours)
    outer = max(contours, key=lambda c: abs(c.area)).clockwise
    small = DOT * stem(path(font, "n"))
    rest, out = pathops.Path(), pathops.Path()
    for c in contours:
        x0, y0, x1, y1 = c.bounds
        holes = any(
            o.clockwise != outer and _inside(o.bounds, c.bounds) for o in contours if o is not c
        )
        if c.clockwise == outer and not holes and max(x1 - x0, y1 - y0) <= small:
            dot = pathops.Path()
            c.draw(pathops.PathPen(dot))
            k = 1 + 2 * amount / min(x1 - x0, y1 - y0)
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            out.addPath(dot.transform(k, 0, 0, k, cx * (1 - k), cy * (1 - k)))
        else:
            c.draw(pathops.PathPen(rest))
    out.addPath(embolden(pathops.op(rest, pathops.Path(), pathops.PathOp.UNION), amount))
    return pathops.op(out, pathops.Path(), pathops.PathOp.UNION)


def _inside(inner, outer):
    return (
        inner[0] >= outer[0]
        and inner[1] >= outer[1]
        and inner[2] <= outer[2]
        and inner[3] <= outer[3]
    )


def _height(font, of):
    """How tall `of` of `font` is."""
    b = path(font, of).bounds
    return b[3] - b[1]


def _fit(p, scale, inner, room=FIT):
    """`scale`, or less if `p` would take more than `room` of `inner` (a
    half width) across or up."""
    x0, y0, x1, y1 = p.bounds
    return min(scale, room * 2 * inner / (x1 - x0), room * 2 * inner / (y1 - y0))


def _enclosure(kind, cx, cy, r, s):
    """The enclosure of `kind`, centred on (cx, cy), `r` its radius or half
    side over SQUARE, and the half width inside it that content may take."""
    a = r * SQUARE

    def ring(q):
        return pathops.op(circle(cx, cy, q), circle(cx, cy, q - s), pathops.PathOp.DIFFERENCE)

    if kind == "ring":
        return ring(r), r - s
    if kind == "double":
        return union_paths([ring(r), ring(r - 2 * s)]), r - 3 * s
    if kind == "disc":
        return circle(cx, cy, r), r - s
    if kind == "square":
        inner = rect(cx - a + s, cy - a + s, cx + a - s, cy + a - s)
        return pathops.op(
            rect(cx - a, cy - a, cx + a, cy + a), inner, pathops.PathOp.DIFFERENCE
        ), a - s
    if kind in ("block", "crossed"):
        return rect(cx - a, cy - a, cx + a, cy + a), a - s
    if kind == "boxring":  # a white ring in a block
        return pathops.op(
            rect(cx - a, cy - a, cx + a, cy + a), circle(cx, cy, a - s), pathops.PathOp.DIFFERENCE
        ), a - 2 * s
    return pathops.Path(), a  # none, raised


def _enclosed(smooth, em, radius, stroke, cy, blended=True, notes=None, emboldened=(), grid=None):
    """{code point: (kind, enclosure, content)} of the enclosed glyphs,
    paths, centred on an advance of `em` and on `cy`, in enclosures of
    `radius` and `stroke`. Digits and letters (blends), unless not
    `blended`, are Redaction's own made heavier (heavier), as heavy against
    n in every style (_plan). It logs those thickened less, their carving
    closing (_cap), and how content is fitted, with `notes`, the variant
    drawn: each grid draws its own, as big as its enclosures. Also the
    content made heavier ({code point: 0}), and a function to draw it again
    where it stands, emboldened by a t of the way to the stems of n.
    Content of `emboldened` (code points) is emboldened, as on 100."""
    cx = em / 2
    # Content as tall as the x-height for digits, its stems as thick as those
    # of n once shrunk (shapes.shrunk)
    zero = path(smooth, "0")
    height = smooth["OS/2"].sxHeight / (zero.bounds[3] - zero.bounds[1])
    italic = _font("Italic")
    sources = {False: shrunk(smooth, height)[0], True: italic}
    # Upright content is as big as it fits typed in Redaction's Bold, the
    # widest of the family, as Regular's always was (shrunk): the same size
    # in every style, but smaller where a style's own is wider (Italic's M)
    wide = _font("Bold")
    shapers = {id(f): shaper(f) for f in (*sources.values(), smooth, wide)}
    target = stem(path(smooth, "n"))
    tm = path(smooth, "™")

    def fit(text, source, most, inner, slanted=False):
        p = content(source, shapers[id(source)], text)
        if slanted:
            return _fit(p, most, inner)
        return min(_fit(p, most, inner), _fit(content(wide, shapers[id(wide)], text), most, inner))

    ring = _enclosure("ring", cx, cy, radius, stroke)[1]
    digits = min(fit(text, sources[False], height, ring) for text in NUMBERS.values())
    style = smooth["name"].getDebugName(2)
    enclosed, ts, again = {}, {}, {}

    def place(p, kind, scale, centred=False, shift=0):
        """Content `p` of `kind`, shrunk by `scale`, where it stands: on the
        middle of its box, `centred`, not between it and its ink's, and
        `shift` right."""
        # Placed as emboldened, which is not quite even all around
        x0, y0, x1, y1 = p.bounds
        if kind == "raised":  # its top at the top of ™
            low = tm.bounds[3] - scale * y1
        else:
            low = cy - scale * (y0 + y1) / 2
        ink = StatisticsPen()
        p.draw(ink)
        # Without an enclosure to look centred in (🆐), centred on its middle
        weight = INK if kind not in ("none", "raised") and not centred else 0
        middle = (x0 + x1) / 2 * (1 - weight) + ink.meanX * weight
        p = p.transform(scale, 0, 0, scale, cx - scale * middle + shift, low)
        if kind == "crossed":  # white diagonals behind the content, corner to corner
            a = radius * SQUARE
            cross = pathops.Path()
            for x, y in ((a, a), (a, -a)):
                line = pathops.Path()
                line.moveTo(cx - x, cy - y)
                line.lineTo(cx + x, cy + y)
                line.stroke(stroke, pathops.LineCap.BUTT_CAP, pathops.LineJoin.MITER_JOIN, 4)
                cross = pathops.op(cross, line, pathops.PathOp.UNION)
            p = pathops.op(p, cross, pathops.PathOp.UNION)
        return p

    for kind, contents, each, slanted in ENCLOSURES:
        frame, inner = _enclosure(kind, cx, cy, radius, stroke)
        # Raised (🅪): as ™, of the style's own letters
        source = smooth if kind == "raised" else sources[slanted]
        own = stem(path(source, "n"))
        thick = stem(tm) if kind == "raised" else target
        texts = {cp: content(source, shapers[id(source)], text) for cp, text in contents.items()}
        most = 1 if kind == "none" else height  # square words as big as fits
        fits = {cp: fit(text, source, most, inner, slanted) for cp, text in contents.items()}
        scales = {}
        for cp, p in texts.items():
            x0, y0, x1, y1 = p.bounds
            if kind == "raised":  # as tall as ™
                scales[cp] = _fit(p, (tm.bounds[3] - tm.bounds[1]) / (y1 - y0), cx)  # in the em
            else:
                scales[cp] = fits[cp] if each else min(fits.values())
        # The size upright styles draw it, as typed in Bold
        shared = dict(scales)
        if kind != "raised" and not slanted:
            bold = {
                cp: _fit(content(wide, shapers[id(wide)], t), most, inner)
                for cp, t in contents.items()
            }
            shared = {cp: bold[cp] if each else min(bold.values()) for cp in contents}
        font = italic if slanted else smooth
        heavy = [cp for cp in texts if blended and blends(contents[cp]) and cp not in emboldened]
        plans, drawn = {}, {}

        # Smaller than digits (🆩), not heavier than them, raised too: strokes
        # would merge
        args, label = (font, digits, target, slanted), notes and f"{notes} {style}"
        for cp in heavy:
            ts[cp] = 0
            text, scale = contents[cp], scales[cp]
            plans[cp], drawn[cp] = _heavier(
                *args, text, scale, shared[cp], cp, label, grid, style=style
            )
        # Heavier, wider than typed, past ROOM: shrunk, made heavier again
        # there, a set all together. Nearer its enclosure than CLEAR of its
        # stroke (⓾ ran into its inner ring, Italic's ⑳ touched its own), it
        # alone: centred on its box, its figures nearer (TIGHT), narrowed
        # (ACROSS), and only then shrunk. Its set keeps its size: shrunk with
        # ⓾, ⓵–⓽ lost a cell on 70.
        room = {cp: _fit(drawn[cp], scales[cp], inner, ROOM) for cp in heavy}
        if room and not each:
            room = dict.fromkeys(texts, min(room.values()))
        shaped = {}  # {code point: (how near its figures, how narrow)}, centred
        if kind in ENCLOSING:
            # On a grid, a cell and a half off at least, as it snaps: ⓾ fused
            # with its ring on 35, 50
            apart = max(stroke * CLEAR, 1.5 * (grid or 0))
            near, fits = _near(kind, frame, cx, cy, radius, apart, place, grid)
            for cp in heavy:
                at = room[cp]
                if not near(drawn[cp], at):
                    continue
                pair = contents[cp].isdigit() and len(contents[cp]) > 1
                # Centred as the rest, within SLACK on a grid: in the smooth
                # font, and ⓾ on a grid; the rest there on its box, anywhere
                # across, as approved
                centring = not grid or kind == "double"
                box = "\n" in contents[cp] if centring else True
                found = None
                for tight in TIGHT if pair else (1,):
                    q = (
                        drawn[cp]
                        if tight == 1
                        else heavier(font, contents[cp], plans[cp], tight, style)
                    )
                    for across in ACROSS:
                        if fits(q.transform(across, 0, 0, 1, 0, 0), at, box, centring):
                            found = tight, across
                            break
                    if found:
                        break
                shaped[cp] = found or (TIGHT[-1] if pair else 1, ACROSS[-1])
                tight, across = shaped[cp]
                if tight != 1:
                    drawn[cp] = heavier(font, contents[cp], plans[cp], tight, style)
                q = drawn[cp].transform(across, 0, 0, 1, 0, 0)
                if found is None:  # then shrunk
                    lo, hi = at * 0.7, at
                    while hi - lo > 0.001:
                        mid = (lo + hi) / 2
                        lo, hi = (mid, hi) if fits(q, mid, box, centring) else (lo, mid)
                    room[cp] = lo
                # Centred as the rest, or the nearest it is off its
                # enclosure: on its box, ⓾'s 1 stood near its ring, its 0 far;
                # in the middle of where it is off it, its 0 stood near. Not
                # centring, in the middle of where it is off it
                if centring:
                    clear = [d for d in _around(80) if not near(q, room[cp], box, d)]
                    shift = min(clear, key=abs) if clear else 0
                else:
                    clear = [d for d in range(-80, 81, 4) if not near(q, room[cp], True, d)]
                    shift = (min(clear) + max(clear)) / 2 if clear else 0
                shaped[cp] = tight, across, shift, box
                if notes:
                    log(f"{notes} {style} {chr(cp)}: {tight:.1f} as near, {across:.2f} as wide")
        for cp, less in room.items() if kind != "raised" else ():
            if less < scales[cp]:
                scales[cp] = less
                if cp in drawn:
                    tight = shaped.get(cp, (1,))[0]
                    plans[cp], drawn[cp] = _heavier(
                        *args, contents[cp], less, shared[cp], cp, label, grid, tight, style
                    )
                if notes:
                    log(f"{notes} {style} {chr(cp)}: shrunk to {less:.3f}, heavier wider")
        # Emboldened (EMBOLDENED), as big as before group 4: as fits typed,
        # its set as big as its smallest typed, not shrunk with what is
        # thickened (Italic's ㉏ ㎨ 🆧 came out smaller, and read otherwise)
        typed = min(_fit(q, most, inner) for q in texts.values())
        for cp, p in texts.items():
            scale = scales[cp]
            if cp in emboldened and kind != "raised":
                scale = _fit(p, most, inner) if each else typed
            if cp in drawn:
                p = drawn[cp]
            else:
                # Smaller than digits (🆩, ㎑), not heavier than them: strokes would merge
                p = embolden(p, max(-THIN, (thick / max(scale, height) - own) / 2))
            # Lines (Hi-/Res) on their box: on their ink, H and R drew them right
            tight, across, shift, box = shaped.get(cp, (1, 1, 0, "\n" in contents[cp]))
            p = p.transform(across, 0, 0, 1, 0, 0)
            enclosed[cp] = kind, frame, place(p, kind, scale, box, shift)
            if cp in drawn:
                # Emboldened on a grid (_ease) up to the stems of n at its size
                now = plans[cp][2]
                bolder = max(0, (thick / max(scale, height) - now) / 2)
                # Or thinned (_ease) as light as before it was WEIGHT heavier
                lighter = now * (1 - 1 / WEIGHT) / 2
                shape = shaped.get(cp)
                again[cp] = font, contents[cp], kind, scale, shape, plans[cp], bolder, lighter

    redrawn = {}

    def redraw(cp, t):
        """Content of `cp` emboldened `t` of the way from as made heavier to
        the stems of n at the size it is drawn, as on 100, or, below 0,
        thinned as much of the way to as light as before WEIGHT."""
        font, text, kind, scale, shape, plan, bolder, lighter = again[cp]
        tight, across, shift, box = shape or (1, 1, 0, "\n" in text)
        if cp not in redrawn:
            redrawn[cp] = heavier(font, text, plan, tight, style)
        p = embolden(redrawn[cp], t * (bolder if t > 0 else lighter))
        p = p.transform(across, 0, 0, 1, 0, 0)
        return place(p, kind, scale, box, shift)

    return enclosed, ts, redraw


def _heavier(font, floor, n, slanted, text, scale, shared, cp, notes, grid, tight=1, style=None):
    """How `text` of `font` is made heavier at `scale` (_plan), and it so
    (heavier) in an enclosure of `style`, logged where its carving caps its
    thickening, in the smooth font."""
    plan, want = _plan(font, text, scale, shared, floor, n, slanted)
    if notes and not grid:
        chars = [c for c in text if c != "\n" and path(font, c).bounds[2]]
        routes = {c: _heavy(font, c, plan, _of(text), style)[1] for c in chars}
        thick = "".join(c for c in chars if routes[c] == "thickened")
        if thick and plan[1] < want:
            log(f"{notes} {chr(cp)} {thick}: thickened {plan[1]:.1f}, capped from {want:.1f}")
        hand = "".join(c for c in chars if routes[c] == "drawn")
        if hand:
            log(f"{notes} {chr(cp)} {hand}: drawn")
    return plan, heavier(font, text, plan, tight, style)


def _near(kind, frame, cx, cy, radius, apart, place, grid=None):
    """Whether content (a path) of `kind` placed at a scale (`place`) comes
    nearer its enclosure `frame` than `apart`, and whether it fits: off it
    centred as placed, or on a grid, as it is phased, within half a cell
    of it (SLACK)."""
    outside = frame
    if kind in NEGATIVE:  # cut out of it: what is outside it
        big = 2 * radius
        outside = pathops.op(
            rect(cx - big, cy - big, cx + big, cy + big), frame, pathops.PathOp.DIFFERENCE
        )
    grown = embolden(outside, apart)

    def near(p, scale, centred=False, shift=0):
        placed = place(p, kind, scale, centred, shift)
        return abs(pathops.op(grown, placed, pathops.PathOp.INTERSECTION).area) > 1

    slack = SLACK * (grid or 0)

    def fits(p, scale, centred=False, centring=True):
        """Whether `p`, centred as placed, is off it, or, not `centring`,
        off it anywhere across: so, ⓾ stood on its right, its weight off
        centre."""
        shifts = _around(slack) if centring else range(-80, 81, 8)
        return any(not near(p, scale, centred, d) for d in shifts)

    return near, fits


def _around(far, step=4):
    """Shifts from 0 out to `far` either way, by `step`."""
    return [0, *(d * k for d in range(step, int(far) + 1, step) for k in (-1, 1))]


def _put(kind, frame, p):
    """Content `p` in its enclosure `frame`, or cut out of it (discs and
    blocks)."""
    negative = kind in NEGATIVE
    return pathops.op(frame, p, pathops.PathOp.DIFFERENCE if negative else pathops.PathOp.UNION)


def _single(text):
    """Whether `text` is a number or a letter, not a word."""
    return text.isdigit() or len(text) == 1


def _pixelated(font, enclosed, glyphs, grid, eased=None, emboldened=()):
    """Enclosed glyphs {name: glyph} pixelated on the grid. Thickened
    content (blends) on PHASED apart from its enclosure, where in a cell it
    falls best (shapes.phased), off it, strokes as thick as n's; then cut
    out of it or put in it, pixels on pixels. Others whole, and
    `emboldened`.

    On EASED, with `eased` (the content thickened, a function to draw it
    again emboldened by a t, and what to log as), content whose pixels
    lose a piece or a counter (_ease) is emboldened, by EASE at a time, up
    to the stems of n, and placed again: the first that holds is kept;
    where none does, it stays as thickened."""
    texts = {cp: text for _, contents, _, _ in ENCLOSURES for cp, text in contents.items()}
    cps = {CODEPOINTS[cp]: cp for cp in texts}
    apart = {
        CODEPOINTS[cp]: drawn
        for cp, drawn in enclosed.items()
        if grid in PHASED
        and blends(texts[cp])
        and _single(texts[cp])
        and drawn[0] != "crossed"
        and cp not in emboldened
    }
    out = pixelate_glyphs({n: g for n, g in glyphs.items() if n not in apart}, grid)
    kinds = {kind: frame for kind, frame, _ in apart.values()}
    frames = pixelate_glyphs({kind: glyph(frame) for kind, frame in kinds.items()}, grid)
    n = font["glyf"][font.getBestCmap()[ord("n")]]
    away = {}
    for kind, g in frames.items():
        on, (left, top), _ = cells(g, grid)
        ink = {(left + c, top - r - 1) for r, c in zip(*np.nonzero(on))}
        if kind in ("disc", "block"):  # cut out: off the air around
            xs, ys = [x for x, _ in ink], [y for _, y in ink]
            box = range(min(xs) - 1, max(xs) + 2), range(min(ys) - 1, max(ys) + 2)
            ink = {(x, y) for x in box[0] for y in box[1]} - ink
        away[kind] = ink
    contents = phased(
        {name: glyph(p) for name, (_, _, p) in apart.items()},
        grid,
        None,
        [n],
        away={name: away[kind] for name, (kind, _, _) in apart.items()},
        heavy=True,
    )
    if eased and grid in EASED:
        contents.update(_ease(apart, contents, grid, [n], away, eased))
    if eased and grid in LIKENED:
        lower = {name: drawn for name, drawn in apart.items() if texts[cps[name]].islower()}
        contents.update(_liken(lower, grid, [n], away, eased))
    for name, (kind, _, _) in apart.items():
        pen = pathops.PathPen
        frame, p = pathops.Path(), pathops.Path()
        frames[kind].draw(pen(frame), None)
        contents[name].draw(pen(p), None)
        out[name] = glyph(_put(kind, frame, p))
    return {name: out[name] for name in glyphs}


def _liken(apart, grid, like, away, eased):
    """_pixelated: {name: pixel content} of `apart` (lowercase) on LIKENED,
    as thickened, then emboldened up to the stems of n by EASE, as _ease
    (a stroke of Italic's r, v, x thinner than a cell drops out), and
    placed at each spot phased tries: the pixels off the enclosure, then
    that lose fewest pieces and counters, then with fewest counters more
    (_lost), then most like the smooth font's drawing, by the cells half
    covered by it, at that spot, the most they share of all they cover
    (_covered)."""
    ts, redraw, label = eased
    cps = {CODEPOINTS[cp]: cp for cp in ts}
    theirs = [widths(cells(g, grid)[0]) for g in like]
    theirs = [sum(w) / len(w) for w in zip(*theirs)]
    tried, smooth, counted = {}, {}, {}
    for name, (_, _, p) in apart.items():
        cp = cps[name]
        for k in range(round(1 / EASE) + 1):
            tried[name, k] = k * EASE, redraw(cp, k * EASE)
        smooth[name] = p
        counted[name] = _counted(p)
    placed = _placed(
        {key: glyph(p) for key, (_, p) in tried.items()},
        grid,
        None,
        theirs,
        False,
        {key: away[apart[key[0]][0]] for key in tried},
        True,
    )
    out, covered = {}, {}
    for name in apart:
        best = None
        for key, (u, _) in tried.items():
            if key[0] != name:
                continue
            for _, rank, pixels, _, (i, j) in placed[key]:
                if (name, i, j) not in covered:
                    there = smooth[name].transform(1, 0, 0, 1, i * grid / SHIFTS, j * grid / SHIFTS)
                    covered[name, i, j] = _covered(there, grid)
                on, (left, top), _ = cells(pixels, grid)
                ink = {(left + c, top - r - 1) for r, c in zip(*np.nonzero(on))}
                theirs_ = covered[name, i, j]
                alike = len(ink & theirs_) / max(1, len(ink | theirs_))
                score = (rank[0], *_lost(counted[name], pixels, grid, True), -alike)
                if best is None or score < best[0]:
                    best = score, pixels, u
        out[name] = best[1]
        log(f"{label} {chr(cps[name])}: likest at {best[2]:.2f}, {-best[0][3]:.2f} alike")
    return out


def _covered(p, grid):
    """The cells, by their corner, over the grid, half covered by `p` or more."""
    x0, y0, x1, y1 = p.bounds
    out = set()
    for x in range(math.floor(x0 / grid), math.ceil(x1 / grid)):
        for y in range(math.floor(y0 / grid), math.ceil(y1 / grid)):
            cell = rect(x * grid, y * grid, (x + 1) * grid, (y + 1) * grid)
            if abs(pathops.op(p, cell, pathops.PathOp.INTERSECTION).area) >= grid * grid / 2:
                out.add((x, y))
    return out


def _counted(drawn):
    """How many pieces and counters `drawn`, a path, has. Its carving stays
    open: closed, figures set close would be one (⑪), and the tail of Q
    would close a counter on its bowl."""
    contours = list(drawn.contours)
    outer = max(contours, key=lambda c: abs(c.area)).clockwise
    holes = sum(c.clockwise != outer for c in contours)
    return len(contours) - holes, holes


def _lost(counted, g, grid, broken=False):
    """How many pieces and counters pixel glyph `g` has fewer than `counted`
    (_counted), or, `broken`, pieces more (a stroke thinner than a cell,
    dropped out), and how many counters more: pixels joined at a corner
    are one, counters closed by every pixel (shapes.cells)."""
    _, _, (pieces, counters, _) = cells(g, grid)
    lost = max(0, counted[0] - pieces) + max(0, counted[1] - len(counters[0]))
    if broken:
        lost += max(0, pieces - counted[0])
    return lost, max(0, len(counters[0]) - counted[1])


def _ease(apart, contents, grid, like, away, eased):
    """_pixelated: {name: pixel content} of the content of `apart` whose
    pixels in `contents` lose a piece or a counter (_lost), or break (a
    stroke thinner than a cell dropped out), emboldened by EASE at a time
    of the way to the stems of n, till they lose none: a piece of it as
    Redaction sets it (figures set close are one, ⑪), a counter of its
    drawing, and no more counters than it had. Where none holds, thinned
    so, no lighter than before WEIGHT: heavier, Bold's ⑩ ➉ closed
    their 0 on 70. Where none holds either, it stays as made heavier."""
    ts, redraw, label = eased
    cps = {CODEPOINTS[cp]: cp for cp in ts}
    n = round(1 / EASE)
    steps = [k * EASE for k in range(1, n + 1)] + [-k * EASE for k in range(1, n + 1)]
    at = dict.fromkeys(apart, -1)
    t = dict.fromkeys(apart, 0)
    counted = {name: _counted(p) for name, (_, _, p) in apart.items()}

    def left(name):
        return at[name] < len(steps) - 1

    was = {name: _lost(counted[name], contents[name], grid, True) for name in apart}
    failing = [name for name in apart if was[name][0]]
    out = {}
    while failing:
        drawn = {}
        for name in failing:
            at[name] += 1
            t[name] = steps[at[name]]
            drawn[name] = redraw(cps[name], t[name])
        placed = phased(
            {name: glyph(p) for name, p in drawn.items()},
            grid,
            None,
            like,
            away={name: away[apart[name][0]] for name in drawn},
            heavy=True,
        )
        for name in failing:
            cp = cps[name]
            lost, extra = _lost(counted[name], placed[name], grid, True)
            if not lost and extra <= was[name][1]:  # and no counter more
                out[name] = placed[name]
                way = "emboldened" if t[name] > 0 else "thinned"
                log(f"{label} {chr(cp)}: {way} to {abs(t[name]):.2f}")
            elif not left(name):
                log(f"{label} {chr(cp)}: kept, none holds")
        failing = [n for n in failing if n not in out and left(n)]
    return out


def _layout(smooth, grid):
    """The advance of enclosed glyphs, the radius and stroke of their
    enclosures, and where they are centred up."""
    em = pixel.snap_advance(1000, grid or 1)
    # On a grid, a cell of white on each side, or enclosures in a row touch.
    radius = min(RADIUS, em / 2 - (grid or 0))
    minus = smooth["glyf"][smooth.getBestCmap()[ord("−")]]
    minus.recalcBounds(smooth["glyf"])
    stroke = max(minus.yMax - minus.yMin, grid or 0)  # at least a cell
    # On a grid, centred on the corner of a cell both ways, as em / 2 is, so
    # enclosures pixelate the same on all sides.
    return em, radius, stroke, pixel.snap(CENTRE, grid or 1)


def enclosure(smooth, grid, kind):
    """The enclosure of `kind` alone, as drawn around content, a path:
    score.py tells content from it."""
    em, radius, stroke, cy = _layout(smooth, grid)
    return _enclosure(kind, em / 2, cy, radius, stroke)[0]


@functools.cache
def by_cells():
    """{(grid, style, character): rows} of the enclosed glyphs drawn by hand
    on a grid (CELLS, shapes.drawn_cells), each its cells, top row first,
    "#" ink, "." air."""
    return drawn_cells(CELLS)


def _cells(kind, frame, rows, grid):
    """A glyph of `rows` (by_cells), placed on its enclosure `frame` (a path)
    pixelated on the grid: the block spans it, whose cells it keeps (or
    those it is cut out of, a disc or a block). Put in it as _pixelated
    puts content, so cells as before make the glyph as before. A word
    without an enclosure (㎏) stands where its rows say (`at`), traced as
    pixelating traces it."""
    if rows.at is not None:
        left, bottom = rows.at
        on = np.array([[v == "#" for v in line] for line in rows])
        pen = TTGlyphPen(None)
        for contour in pixel._trace(on):
            pen.moveTo(((left + contour[0][0]) * grid, (bottom + len(rows) + contour[0][1]) * grid))
            for x, y in contour[1:]:
                pen.lineTo(((left + x) * grid, (bottom + len(rows) + y) * grid))
            pen.closePath()
        return pen.glyph()
    g = pixelate_glyphs({kind: glyph(frame)}, grid)[kind]
    on, (left, top), _ = cells(g, grid)
    if on.shape != (len(rows), len(rows[0])) or any(len(r) != len(rows[0]) for r in rows):
        raise ValueError(f"{kind} drawn by hand on {grid} is not as big as its enclosure")
    ink = np.array([[v == "#" for v in line] for line in rows])
    if not ((ink <= on) if kind in NEGATIVE else (on <= ink)).all():
        raise ValueError(f"{kind} drawn by hand on {grid} is not its enclosure as built")
    content, ring = pathops.Path(), pathops.Path()
    g.draw(pathops.PathPen(ring), None)
    pen = pathops.PathPen(content)
    for contour in pixel._trace(on ^ ink):
        pen.moveTo(((left + contour[0][0]) * grid, (top + contour[0][1]) * grid))
        for x, y in contour[1:]:
            pen.lineTo(((left + x) * grid, (top + y) * grid))
        pen.closePath()
    return glyph(_put(kind, ring, content))


def add_glyphs(font, smooth, grid=None):
    em, radius, stroke, cy = _layout(smooth, grid)
    blended = not grid or grid <= COARSEST
    style = smooth["name"].getDebugName(2)
    emboldened = {ord(c) for c in EMBOLDENED.get(grid, {}).get(style, "")}
    enclosed, ts, redraw = _enclosed(
        smooth, em, radius, stroke, cy, blended, grid or "smooth", emboldened=emboldened, grid=grid
    )
    glyphs = {CODEPOINTS[cp]: glyph(_put(*drawn)) for cp, drawn in enclosed.items()}
    if grid:
        # Drawn as before, pixelated as before: with its enclosure
        emboldened |= {cp for cp in enclosed if cp not in ts}
        eased = (ts, redraw, f"{grid} {style}") if blended and grid in EASED else None
        glyphs = _pixelated(font, enclosed, glyphs, grid, eased, emboldened)
        # Or drawn by hand, cell by cell, on this grid
        for cp, (kind, frame, _) in enclosed.items():
            rows = by_cells().get((grid, style, chr(cp)))
            if rows:
                glyphs[CODEPOINTS[cp]] = _cells(kind, frame, rows, grid)
    add(
        font, {name: (g, em) for name, g in glyphs.items()}, {cp: CODEPOINTS[cp] for cp in enclosed}
    )

    s = shaper(font)
    glyphs = {CODEPOINTS[cp]: typed(font, s, text, grid) for cp, text in TYPED.items()}
    # 🄯: © turned over, in place
    copyright = font.getBestCmap()[ord("©")]
    g = font["glyf"][copyright]
    g.recalcBounds(font["glyf"])
    pen = TTGlyphPen(font["glyf"])
    pen.addComponent(copyright, (-1, 0, 0, 1, g.xMin + g.xMax, 0))
    glyphs[CODEPOINTS[COPYLEFT]] = (pen.glyph(), font["hmtx"][copyright][0])
    add(font, glyphs, CODEPOINTS)
