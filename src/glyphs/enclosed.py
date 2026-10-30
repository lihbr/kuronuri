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

Bold's and Italic's content is Redaction's own as drawn, only scaled and
placed: lighter than their n, but MCKL's carving, tips and terminals
(Bold's 🄫 🄬, Italic's C R as drawn). Regular's is made heavier as
Redaction's Bold is of its Regular (shapes.blend), till the stems of n, I
or 1 (_of: I with a capital, n with lowercase alone, else 1) are those of
n at the size it is drawn, or, smaller than circled numbers, as heavy as
those, and no further than T_MAX (Bold): further, its forms swell. It is
shrunk back as tall as its own, its glyphs all one height and one weight,
as the superscript letters, so it keeps MCKL's hairlines and carving. A
glyph that folds blends as far as it goes. A glyph whose outlines do not
match Redaction's Regular and Bold as they are (Q W w y, the R of 🄬),
or that blends less than HALF as far, is drawn as before, alone, its word
blended (_before): Bold's Q W w y as they are, Italic's R emboldened all
round. Glyphs are spaced as near as typed where their ink comes nearest,
any way (_nearest); figures as far apart as they look on average, all
alike (_optically). Content is as big as it fits typed in Redaction's
Bold, upright, in every style, or smaller where a style's own is wider
(Italic's M): words take the room their blending adds, up to ROOM, sets
too, all together; a glyph nearer its enclosure than CLEAR of its stroke
is fitted alone, centred as the rest (⓾): its figures nearer, narrowed,
then shrunk. Lines (Hi-/Res) are set one under the other, centred on
their box. On a grid (PHASED), a number or a letter is pixelated apart
from its enclosure, where in a cell it falls best, its stems filling
cells first (shapes.phased); words are pixelated with it, which keeps
more of their counters and their letters off it. On 35 to 70 (EASED),
where its pixels lose a piece or a counter, Regular's is blended less,
Bold's and Italic's, a stroke thinner than a cell dropped out, emboldened
a little (_ease). On 70, lowercase is placed, and blended or emboldened,
as like its smooth drawing as its pixels come (_liken); on 35 to 70, a
few that read as other glyphs are drawn as before group 4 (EMBOLDENED).
Content all drawn as before is pixelated as before, with its enclosure.
On 100 (COARSEST), all content is emboldened: from Bold thinned in an
upright Regular, which keeps its carving.

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
from family import log, redaction

from .shapes import (
    SHIFTS,
    STEP,
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
    embolden,
    glyph,
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

RADIUS = 462  # of the ring, as in Noto Serif JP
CENTRE = 380  # of the ideographic em box (-120..880)
SQUARE = 0.86  # half the side of squares, over the radius of rings: they look as big
FIT = 0.8  # of the width inside the enclosure, that content may take
# of it, that content blended wider may take: as far as emboldened words
# came before (🆜, ㏑)
ROOM = 0.9
# Enclosures blended content is kept half a stroke from, and those it is cut out of
ENCLOSING = ("ring", "double", "disc", "square", "block", "boxring")
NEGATIVE = ("disc", "block", "crossed")
LINES = 1.25  # cap heights between the lines of content (Hi-/Res), as content() sets them
T_MAX = 1.0  # farthest content is blended past Regular, Bold's of Regular: further, it swells
# least area of a hole content drawn as before keeps: its carving, closing, leaves less
SLIVER = 400
# shortest segment a glyph drawn as before keeps, wherever it turns, as
# 29c0292 smoothed it (_smoothed)
SHORT = 12
# Fallback glyphs grown less, as ¹'s stem is of 1's: superscripts
SMALL = "¹²³"
# how near figures come, and how narrow, for content to fit its enclosure alone (⓾)
TIGHT = (1, 0.8, 0.6)
# how near figures come, of their nearest ink typed, spaced as they look
NEAREST = 0.7
# nearest two points of content as placed keep where it runs on through them,
# turning less than CLEAN_BEND (_cleaned), and any way: under 2, a word's W
# crotches and curves still left segments a few units long (🆕 ㎯); turning
# more, a serif's corner, kept
NEAR = 6
CLOSEST = 2
CLEAN_BEND = math.radians(80)
ACROSS = (1, 0.98, 0.96, 0.94, 0.92)
# least of its stroke content keeps off its enclosure (⓾ at half stood crowded)
CLEAR = 0.75
SPACED = 300  # farthest glyphs are spaced by their nearest ink, not their boxes
# Of a cell, how far off centre content may stand on a grid to fit off its
# enclosure, as phasing it moves it anyway
SLACK = 0.5
HALF = 0.5  # least of its t a glyph blends to for its content to be blended, not drawn as before
INK = 0.5  # how far content is centred on the middle of its ink, from 0 to 1
# Coarsest grid digits and capitals are blended on: on 100, abstract, their
# hairlines are under half a cell and drop out, letters with them (㍳)
COARSEST = 70
# Grids blended numbers and letters are placed on apart, where in a cell
# they fall best
PHASED = (10, 20, 35, 50, 70)
# Grids blended numbers and letters are blended less on where their pixels
# lose a piece or a counter (_pixelated), by EASE of t at a time
EASED = (35, 50, 70)
EASE = 0.1
# Grids lowercase is blended and placed on as like the smooth font's as its
# pixels come (_liken)
LIKENED = (70,)
# Content drawn on a grid as before group 4, emboldened and pixelated with
# its enclosure: blended, or as drawn, it reads as other glyphs, where so it
# did not. On 70, lowercase as like the smooth font's as it comes (_liken).
# Regular's, the audits of rounds 2 to 5: 🅸 as ) on 70, ㎢ as km³ on 35;
# ㏇'s full stop a comma on 35; Ⓗ as X and Ⓜ as x on 70, ㉊ as 50, 🅊 as KV,
# 🅦 as \\\ on 50, ㉈ as J0, ㉉ ㉋ ㉌ misread on 50. Bold's and Italic's,
# as drawn (round 6, the rest of theirs reading as well without): Italic's
# ㏞ V/m in two, ㎮'s slash lost, ㎧ ㎨ their slash's foot, on 35 and 50; on
# 50, ㉊ as JO, ㎨ broken, ⓛ ⓣ as !; on 70, its e as ρ, h as λ, f without
# its bar, 🄼 and the letters of ㎁ ㎃ ㎄ ㎫ broken; Bold's Ⓜ as Ж, ⓗ a
# wedge on 70; the words of 🆋–🆏, cut out thinner than a cell, gone on 50
# (Italic's) and 70.
EMBOLDENED = {
    35: {"Regular": "㎢㏇", "Italic": "㏞㎮㎧㎨"},
    50: {"Regular": "㉈㉉㉊㉋㉌🅊🅦", "Italic": "㉊㎮㎨ⓛⓣ🆋🆌🆍🆎🆏"},
    70: {
        "Regular": "🅸ⒽⓂ",
        "Italic": "ⓔⓗⓕ🄼㎁㎃㎄㎫🆋🆌🆍🆎🆏",
        "Bold": "Ⓜⓗ🆋🆌🆍🆎🆏",
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
    """Whether `text` is drawn blended (heavier): all content is, letters,
    figures and their punctuation."""
    return any(c.isalnum() for c in text)


def heavier(font, text, t, notes=None, source=None, fell=None, tight=1):
    """`text` in `font` (smooth) made heavier as Redaction's Bold is of its
    Regular (shapes.blend), by `t` (solve), or as drawn where it is 0
    (Bold's and Italic's: Redaction's own). Each glyph is blended
    (_blended), and shrunk back as tall as `font`'s (solve): its letters
    all one height and one weight. A glyph that does not match Redaction's
    Regular and Bold, or blends less than HALF as far, is drawn as before
    from `source` (_before), alone: its word blended. Spaced as typed,
    around their own ink (_spaced), its lines (Hi-/Res) one under the
    other, as content() sets them, each centred on x = 0. Glyphs blended
    less than `t` are noted in `notes`, a list, as (char, t, t blended
    to, False); those drawn as before in `fell`."""
    of = _of(text)
    out = pathops.Path()
    for i, line in enumerate(text.split("\n")):
        reached = []
        p = _spaced(font, line, t, reached, source or font, of, fell, tight)
        if notes is not None:
            notes += [(c, t, done) for c, done in reached if done != t]
        down = i * font["OS/2"].sCapHeight * LINES
        out.addPath(p.transform(1, 0, 0, 1, -(p.bounds[0] + p.bounds[2]) / 2, -down))
    k = _height(font, of) / _height(font, of, t)  # back as tall as `font`'s
    out = out.transform(k, 0, 0, k, 0, 0)
    return pathops.op(out, pathops.Path(), pathops.PathOp.UNION)


def _spaced(font, line, t, notes, source, of, fell=None, tight=1):
    """`line` of `font`, each glyph as drawn (`t` 0), blended by `t`
    (_blended), or drawn as before from `source` (_before), its ink as near
    the last's as typed
    (_nearest): blended, glyphs grow wider than their advances (Bold's
    "less" ran together, ㉔ and ㉕ apart unlike), and toward each other
    where they come nearest, not where their boxes do (Bold's 4 ran into
    ㊷'s 2, a 1's foot into ⓫'s other 1). Notes (char, t blended to) in
    `notes`, glyphs drawn as before in `fell`."""
    out, last = pathops.Path(), None
    for (char, (_, x, y)), was in zip(
        zip(line, _set(font, _shaper(font), line)[0]), _typed(font, line)
    ):
        if path(font, char).bounds == (0, 0, 0, 0):  # a space
            continue
        blended = (path(font, char), 0) if not t else _blended(font, char, t)
        if blended is None or abs(blended[1]) < abs(t) * HALF:  # no match, or paler than the rest
            p = _before(font, source, char, t, of)
            if fell is not None:
                fell.append(char)
        else:
            p, done = blended
            notes.append((char, done))
        p = p.transform(1, 0, 0, 1, x, y)
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


def _blended(font, char, t):
    """`char` of `font` blended by `t` (shapes.blend), its outline matched to
    Redaction's Regular and Bold as they are. Where it folds or its carving
    closes before `t`, as far as it blends, by a STEP of `t`, and no
    further. (path, t blended to), or None if it does not match (W, Q)."""
    regular, bold = masters()
    for k in range(round(1 / STEP), -1, -1):
        u = t * k * STEP
        try:
            p = blend(font, regular, bold, char, u)
        except ValueError:
            # Folds, or its carving closes: or slivers, which skia-pathops
            # leaves where edges nearly meet, are taken for carving (Bold's H)
            try:
                p = blend(font, regular, bold, char, u, sliver=True)
            except (ValueError, pathops.PathOpsError):
                continue
        except pathops.PathOpsError:
            continue
        return (p, u) if p is not None else None
    return path(font, char), 0


def _of(text):
    """The glyph whose stems `text` is made heavier by: I if it has a
    capital (℡), so that none of its glyphs is blended further than alone:
    solved on n, its capitals would be past ℡'s, where Bold's S folds; else
    n if it has a lowercase letter, else 1."""
    if any(c.isupper() for c in text):
        return "I"
    return "n" if any(c.islower() for c in text) else "1"


def solve(font, text, stems):
    """How far `text` of `font` is blended for the stems of its n, I or 1
    (_of) to be `stems` once shrunk back as tall as `font`'s (heavier), as
    the superscript letters are, no farther than T_MAX."""
    of, (regular, bold) = _of(text), masters()
    s, x = stem(path(font, of)), _height(font, of)
    ds = stem(path(bold, of)) - stem(path(regular, of))
    dx = _height(bold, of) - _height(regular, of)
    # (s + t ds) / (x + t dx) = stems / x
    return min(T_MAX, x * (stems - s) / (ds * x - stems * dx))


@functools.cache
def _before(font, source, char, t, of):
    """`char` drawn as before: `source`'s, emboldened all round as much as
    its own n, I or 1 of `font` blended by `t` takes to be as heavy, as its
    word's blended letters are (Italic's R, in Regular's 🄬), or as it is
    where that is lighter (Regular's Q W w y, from Bold): thinned, Q's tail
    and W's notches came out cut. As tall as it would blend. No heavier
    than its pieces and counters stay; holes under SLIVER filled.
    Smoothed as 29c0292 did (_smoothed)."""
    p = path(source, char)
    own = _of(char) if char.isalnum() else of
    # Superscripts as ¹ is of 1: ³ came out heavy
    ratio = stem(path(source, "¹")) / stem(path(source, "1")) if char in SMALL else 1
    amount = max(0, _amount(font, source, own, t, own) * ratio)
    pieces = _pieces(p)
    q = embolden(p, amount if amount >= 0.5 else 0)
    while amount > 0.5 and _pieces(q) != pieces:
        amount *= 0.8
        q = embolden(p, amount)
    if amount > 0.5:
        contours = list(q.contours)
        outer = max(contours, key=lambda c: abs(c.area)).clockwise
        kept = pathops.Path()
        for c in contours:
            if c.clockwise == outer or abs(c.area) >= SLIVER:
                kept.addPath(c)
        q = pathops.op(kept, pathops.Path(), pathops.PathOp.UNION)
    # As tall as it would blend, its top where it would: scaled about its
    # foot, W stood low in 🆕; by its n, I or 1, J R W tall, grown down too
    k = _height(font, char, t) / (q.bounds[3] - q.bounds[1])
    dy = _top(font, char, t) - q.bounds[3] * k
    q = _smoothed(q.transform(k, 0, 0, k, 0, dy))
    # Rounded, as the font will be: skia-pathops fails on it, spacing it
    rounded = pathops.Path()
    glyph(q).draw(pathops.PathPen(rounded), None)
    return rounded


def _smoothed(p):
    """`p` without its segments shorter than SHORT, but where it turns right
    back, or a third as short any way, which emboldening leaves along its
    curves and round its tips: the next goes on from the last, no further
    off than they are long."""
    out = pathops.Path()
    pen, start, at, heading = out.getPen(), None, None, None
    for verb, pts in p.segments:
        if verb == "moveTo":
            start = at = pts[0]
            heading = None
            pen.moveTo(at)
        elif verb in ("closePath", "endPath"):
            pen.closePath()
        else:
            end = pts[-1]
            way = math.atan2(end[1] - at[1], end[0] - at[0])
            off = 0 if heading is None else way - heading
            turn = abs((off + math.pi) % (2 * math.pi) - math.pi)
            run = math.dist(at, end)
            if end != start and (run < SHORT / 3 or run < SHORT and turn < math.pi):
                continue  # dropped: the next starts where this one did
            getattr(pen, verb)(*pts)
            last = pts[-2] if len(pts) > 1 and pts[-2] != end else at
            heading = math.atan2(end[1] - last[1], end[0] - last[0])
            at = end
    return pathops.op(out, pathops.Path(), pathops.PathOp.UNION)


def _cleaned(p):
    """`p` as placed, rounded as the font will be, without its points nearer
    the last than NEAR where it runs on through them, turning less than
    CLEAN_BEND, or than CLOSEST any way, and its lines on in a line merged:
    joined and shrunk, a word's letters drawn as before left segments a few
    units long along their curves and round their tips (🆕, ㎯). Its
    corners kept: dropped, its traps came out slopes, its stems leaning
    (🆓, 🆖)."""
    out = pathops.Path()
    for contour in p.contours:
        points = []  # [(verb, points)], rounded
        for verb, pts in contour.segments:
            pts = tuple((round(x), round(y)) for x, y in pts)
            if verb == "moveTo":
                points = [(verb, pts)]
            elif verb in ("lineTo", "qCurveTo", "curveTo"):
                at = points[-1][1][-1]
                run = math.dist(at, pts[-1])
                last = points[-1][1]
                if len(last) > 1:
                    before = last[-2]
                else:
                    before = points[-2][1][-1] if len(points) > 1 else at
                way = math.atan2(pts[-1][1] - at[1], pts[-1][0] - at[0])
                heading = math.atan2(at[1] - before[1], at[0] - before[0])
                turn = abs((way - heading + math.pi) % (2 * math.pi) - math.pi)
                if run < CLOSEST or run < NEAR and before != at and turn < CLEAN_BEND:
                    continue  # dropped: the next goes on from the last
                if verb == "lineTo" and points[-1][0] == "lineTo" and len(points) > 1:
                    a, b, c = points[-2][1][-1], points[-1][1][-1], pts[-1]
                    cross = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
                    if abs(cross) <= math.dist(a, c) / 2:  # b within half a unit of a–c
                        points[-1] = (verb, pts)
                        continue
                points.append((verb, pts))
        if len(points) < 3:
            continue
        pen = out.getPen()
        for verb, pts in points:
            getattr(pen, verb)(*pts)
        pen.closePath()
    return pathops.op(out, pathops.Path(), pathops.PathOp.UNION)


@functools.cache
def _amount(font, source, char, t, of):
    """How much `char` of `source` is emboldened all round (thinned below 0)
    for the stems of its `of` to be those of `font` blended by `t`, once as
    tall as `font`'s `char` would blend."""
    regular, bold = masters()
    stems = stem(path(font, of)) + t * (stem(path(bold, of)) - stem(path(regular, of)))
    tall = _height(font, char, t)
    h = path(source, char).bounds
    h = h[3] - h[1]
    s = stem(path(source, of))
    # (s + 2a) tall / (h + 2a) = stems
    return (stems * h - s * tall) / (2 * (tall - stems))


def _top(font, char, t):
    """Where the top of `char` of `font` blended by `t` is."""
    regular, bold = masters()
    return path(font, char).bounds[3] + t * (
        path(bold, char).bounds[3] - path(regular, char).bounds[3]
    )


def _height(font, of, t=0):
    """How tall `of` of `font` is, blended by `t` as Redaction's Bold is of
    its Regular."""
    regular, bold = masters()
    h = path(font, of).bounds
    hr, hb = path(regular, of).bounds, path(bold, of).bounds
    return (h[3] - h[1]) + t * ((hb[3] - hb[1]) - (hr[3] - hr[1]))


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


def _enclosed(
    smooth,
    em,
    radius,
    stroke,
    cy,
    blended=True,
    notes=None,
    solved=False,
    emboldened=(),
    grid=None,
):
    """{code point: (kind, enclosure, content)} of the enclosed glyphs,
    paths, centred on an advance of `em` and on `cy`, in enclosures of
    `radius` and `stroke`. Digits and capitals blended (blends), unless not
    `blended`, their stems those of n at the size they are drawn, or, drawn
    smaller than digits (NUMBERS), as heavy as those. It logs those that do
    not blend so far (heavier), with `notes`, the
    variant drawn: each grid draws its own, as big as its enclosures.
    Also how far each blended glyph is ({code point: t}), and a function to
    draw its content again, blended by another t, where it stands. If
    `solved`, only how far, as first solved: the size of words aside.
    Content of `emboldened` (code points) is emboldened, as on 100."""
    cx = em / 2
    # Content as tall as the x-height for digits, its stems as thick as those
    # of n once shrunk (shapes.shrunk)
    zero = path(smooth, "0")
    height = smooth["OS/2"].sxHeight / (zero.bounds[3] - zero.bounds[1])
    italic = redaction(None, "Italic")
    sources = {False: shrunk(smooth, height)[0], True: italic}
    # Upright content is as big as it fits typed in Redaction's Bold, the
    # widest of the family, as Regular's always was (shrunk): the same size
    # in every style, but smaller where a style's own is wider (Italic's M)
    wide = redaction(None, "Bold")
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
    regular = style == "Regular"  # blended; Bold's and Italic's content as drawn
    enclosed, ts, again = {}, {}, {}

    def place(p, kind, scale, centred=False, shift=0, clean=False):
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
        if clean:  # drawn: as the font will be (_cleaned)
            p = _cleaned(p)
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
        # At the size drawn, as ™ raised; smaller than digits (🆩), not
        # heavier than them: strokes would merge
        floor = 0 if kind == "raised" else digits
        font = italic if slanted else smooth
        heavy = [cp for cp in texts if blended and blends(contents[cp]) and cp not in emboldened]
        drawn = {}
        for cp in heavy:
            # Bold's and Italic's as drawn (t 0): Redaction's own, scaled
            ts[cp] = solve(font, contents[cp], thick / max(scales[cp], floor)) if regular else 0
            if not solved:
                drawn[cp] = _drawn(font, contents[cp], ts[cp], source)
        if solved:
            continue
        # Blended, wider than typed, past ROOM: shrunk, its stems solved
        # again there, a set all together. Nearer its enclosure than CLEAR of
        # its stroke (⓾ ran into its inner ring, Italic's ⑳ touched its own),
        # it alone: centred on its box, its figures nearer (TIGHT), narrowed
        # (ACROSS), and only then shrunk. Its set keeps its size: shrunk
        # with ⓾, ⓵–⓽ lost a cell on 70.
        room = {cp: _fit(drawn[cp][0], scales[cp], inner, ROOM) for cp in heavy}
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
                if not near(drawn[cp][0], at):
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
                        drawn[cp][0]
                        if tight == 1
                        else heavier(font, contents[cp], ts[cp], source=source, tight=tight)
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
                    drawn[cp] = _drawn(font, contents[cp], ts[cp], source, tight)
                q = drawn[cp][0].transform(across, 0, 0, 1, 0, 0)
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
                if cp in drawn and regular:
                    ts[cp] = solve(font, contents[cp], thick / max(less, floor))
                    drawn[cp] = _drawn(font, contents[cp], ts[cp], source, shaped.get(cp, (1,))[0])
                if notes:
                    log(f"{notes} {style} {chr(cp)}: shrunk to {less:.3f}, blended wider")
        # All of it drawn as before (Italic's ㎏): pixelated as before
        before = {cp for cp in drawn if drawn[cp][3]}
        for cp in before:
            ts.pop(cp)
        # Emboldened (EMBOLDENED), as big as before group 4: as fits typed,
        # its set as big as its smallest typed, not shrunk with what blends
        # (Italic's ㉏ ㎨ 🆧 came out smaller than approved, and read otherwise)
        typed = min(_fit(q, most, inner) for q in texts.values())
        for cp, p in texts.items():
            scale = scales[cp]
            if cp in emboldened and kind != "raised":
                scale = _fit(p, most, inner) if each else typed
            if cp in drawn:
                p, noted, fell, _ = drawn[cp]
                for char, t, done in noted if notes else []:
                    log(f"{notes} {style} {chr(cp)} {char}: t {t:.2f}, blended to {done:.2f}")
                if fell and notes:
                    log(f"{notes} {style} {chr(cp)} {''.join(fell)}: drawn as before")
            else:
                # Smaller than digits (🆩, ㎑), not heavier than them: strokes would merge
                p = embolden(p, max(-THIN, (thick / max(scale, height) - own) / 2))
            # Lines (Hi-/Res) on their box: on their ink, H and R drew them right
            tight, across, shift, box = shaped.get(cp, (1, 1, 0, "\n" in contents[cp]))
            p = p.transform(across, 0, 0, 1, 0, 0)
            # Cleaned where it has letters drawn as before, in the smooth font
            clean = not grid and cp in drawn and bool(drawn[cp][2])
            enclosed[cp] = kind, frame, place(p, kind, scale, box, shift, clean)
            if cp in drawn and cp not in before:
                bolder = max(-THIN, (thick / max(scale, height) - own) / 2)
                again[cp] = font, contents[cp], kind, scale, source, shaped.get(cp), bolder
    if solved:
        return ts

    drawn_as_is = {}

    def redraw(cp, t):
        """Content of `cp` blended by `t` (Regular's), or, as drawn (Bold's
        and Italic's), emboldened `t` of the way to the stems of n at the size
        it is drawn, as on 100."""
        font, text, kind, scale, source, shape, bolder = again[cp]
        tight, across, shift, box = shape or (1, 1, 0, "\n" in text)
        if regular:
            p = heavier(font, text, t=t, source=source, tight=tight)
        else:
            if cp not in drawn_as_is:
                drawn_as_is[cp] = heavier(font, text, 0, source=source, tight=tight)
            p = embolden(drawn_as_is[cp], t * bolder)
        p = p.transform(across, 0, 0, 1, 0, 0)
        return place(p, kind, scale, box, shift)

    return enclosed, ts, redraw


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


def _drawn(font, text, t, source, tight=1):
    """`text` of `font` made heavier by `t` (heavier), what of it is noted,
    what of it is drawn as before from `source`, and whether all of it is."""
    noted, fell = [], []
    p = heavier(font, text, notes=noted, t=t, source=source, fell=fell, tight=tight)
    ink = [c for c in text if c != "\n" and path(font, c).bounds != (0, 0, 0, 0)]
    return p, noted, fell, len(fell) == len(ink)


def _put(kind, frame, p):
    """Content `p` in its enclosure `frame`, or cut out of it (discs and
    blocks)."""
    negative = kind in NEGATIVE
    return pathops.op(frame, p, pathops.PathOp.DIFFERENCE if negative else pathops.PathOp.UNION)


def _single(text):
    """Whether `text` is a number or a letter, not a word."""
    return text.isdigit() or len(text) == 1


def _pixelated(font, enclosed, glyphs, grid, eased=None, emboldened=()):
    """Enclosed glyphs {name: glyph} pixelated on the grid. Blended content
    (blends) on PHASED apart from its enclosure, where in a cell it falls
    best (shapes.phased), off it, strokes as thick as n's; then cut out of
    it or put in it, pixels on pixels. Others whole, and `emboldened`.

    On EASED, with `eased` (how far each is blended, a function to draw it
    again blended by another t, how far the smooth font blends it, and what
    to log as), content whose pixels lose a piece or a counter (_ease) is
    blended less, by EASE at a time, down to how far the smooth font blends
    it, and placed again: the first that holds is kept; where none does, it
    stays as blended.
    Drawn smaller than in the smooth font, as its enclosures are a cell in,
    it is blended further, and its counters, smaller than a cell, close
    (Bold's ④ ⑥ on 70)."""
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
    blended by how far the smooth font blends it to as far as here, by
    EASE, and placed at each spot phased tries: the pixels off the
    enclosure, then that lose fewest pieces and counters, then with fewest
    counters more (_lost), then most
    like the smooth font's drawing, by the cells half covered by it, at that
    spot, the most they share of all they cover (_covered). Bold's v blended
    so far reads as ▼, Italic's e as p. Bold's and Italic's, drawn as
    they are, emboldened from there by EASE, as _ease: a stroke of Italic's
    r, v, x thinner than a cell drops out."""
    ts, redraw, lightest, label, far = eased
    up = far is not lightest
    cps = {CODEPOINTS[cp]: cp for cp in ts}
    theirs = [widths(cells(g, grid)[0]) for g in like]
    theirs = [sum(w) / len(w) for w in zip(*theirs)]
    tried, smooth, counted = {}, {}, {}
    for name, (_, _, p) in apart.items():
        cp, t, light = cps[name], ts[cps[name]], lightest[cps[name]]
        if up:
            span = far[cp] - t
            steps = [t + k * EASE for k in range(round(span / EASE) + 1)]
        else:
            steps = [light + k * EASE for k in range(int((t - light) / EASE) + 1)]
        for k, u in enumerate(sorted({*steps, t}) if up or t > light else [t]):
            tried[name, k] = u, redraw(cp, u)
        smooth[name] = redraw(cp, light) if t > light else p
        holes = max(_counted(p)[1], _counted(smooth[name])[1])
        counted[name] = _counted(redraw(cp, 0))[0], holes
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
                score = (rank[0], *_lost(counted[name], pixels, grid, up), -alike)
                if best is None or score < best[0]:
                    best = score, pixels, u
        out[name] = best[1]
        t = ts[cps[name]]
        log(f"{label} {chr(cps[name])}: t {t:.2f} likest at {best[2]:.2f}, {-best[0][3]:.2f} alike")
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
    pixels in `contents` lose a piece or a counter (_lost), blended less
    (Regular's) or emboldened (Bold's and Italic's, as drawn), by EASE at a
    time, till they lose none: a piece of it as Redaction sets it (blended,
    figures set close are one, ⑪), a counter of its drawing blended as far
    as here or as in the smooth font, and no more counters than it had.
    Where none holds, it stays as it was: blended lighter, it would only be
    paler than the rest, and no better; emboldened, heavier."""
    ts, redraw, lightest, label, far = eased
    up = far is not lightest
    cps = {CODEPOINTS[cp]: cp for cp in ts}
    t = {name: ts[cps[name]] for name in apart}
    light = {name: lightest[cps[name]] for name in apart}
    end = {name: far[cps[name]] for name in apart}
    counted = {}
    for name, (_, _, p) in apart.items():
        lighter = p if t[name] <= light[name] else redraw(cps[name], light[name])
        holes = max(_counted(p)[1], _counted(lighter)[1])
        counted[name] = _counted(redraw(cps[name], 0))[0], holes

    def left(name):
        return t[name] < end[name] if up else t[name] > end[name]

    was = {name: _lost(counted[name], contents[name], grid, up) for name in apart}
    failing = [name for name in apart if left(name) and was[name][0]]
    out = {}
    while failing:
        drawn = {}
        for name in failing:
            t[name] = min(t[name] + EASE, end[name]) if up else max(t[name] - EASE, end[name])
            drawn[name] = redraw(cps[name], t[name])
        placed = phased(
            {name: glyph(p) for name, p in drawn.items()},
            grid,
            None,
            like,
            away={name: away[apart[name][0]] for name in drawn},
            heavy=True,
        )
        how = "emboldened" if up else "eased"
        for name in failing:
            cp = cps[name]
            lost, extra = _lost(counted[name], placed[name], grid, up)
            if not lost and extra <= was[name][1]:  # and no counter more
                out[name] = placed[name]
                log(f"{label} {chr(cp)}: t {ts[cp]:.2f} {how} to {t[name]:.2f}")
            elif not left(name):
                log(f"{label} {chr(cp)}: t {ts[cp]:.2f} kept, none holds to {t[name]:.2f}")
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
        eased = None
        if blended and grid in EASED:  # down to how far the smooth font blends
            lightest = _enclosed(smooth, *_layout(smooth, None), solved=True)
            # Bold's and Italic's, as drawn, up to the stems of n
            far = lightest if style == "Regular" else dict.fromkeys(ts, 1)
            eased = ts, redraw, lightest, f"{grid} {style}", far
        glyphs = _pixelated(font, enclosed, glyphs, grid, eased, emboldened)
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
