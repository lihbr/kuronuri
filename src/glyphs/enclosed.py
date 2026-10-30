"""Enclosed numbers and letters drawn from Redaction's own: ① Ⓐ ❶ ⓵ 🄰 🅰 🆒,
and ⑴ ⒈ 🄁 🄯.

The enclosures are rings (①), two rings (⓵), discs (❶), squares (🄰) and
blocks (🅰), as thin as Redaction's minus, as its other signs are thin. They
sit where Noto Serif JP's ring does: across the em (but a cell from its
sides on a grid), centred on the ideographic em box, as Japanese text
expects. Their content is Redaction's glyphs as typed, made heavier first so
their stems match those of n once shrunk, the same size across a family:
as tall as the x-height for digits, or less if the widest would not fit
(⑳), and centred between their middle and the middle of their ink, so ④,
heavier on the right, looks centred. Words (🆒 COOL) are each as big as
fits. Discs and blocks are cut out by their content. Japanese stays upright
in italic, and so do enclosures, around italic content.

Content is made heavier as Redaction's Bold is of its Regular
(shapes.blend), till the stems of n, I or 1 (_of: I with a capital, n
with lowercase alone, else 1) are those of n at the size it is drawn,
or, smaller than circled numbers, as heavy as those, and no further than
T_MAX past its own style (Bold's T_BOLD): further, its forms swell. It
is shrunk back as tall as its own, its glyphs all one height and one
weight, as the superscript letters, so it keeps MCKL's hairlines and
carving. A glyph that folds blends as far as it goes. A glyph whose
outlines do not match Redaction's Regular and Bold as they are (Italic's
lowercase, W Q), or that blends less than HALF as far, is drawn as
before, alone, its word blended: grown sideways, a quarter as much up and
down, as much as its own n, I or 1 takes to be as heavy as blended
(superscripts less), its serifs and hairlines nearly as thin, as tall as
it would blend, its dots scaled, not grown, Redaction's carving swept out
to its new edge where it cuts cleanly (_before, _bold, _whites, _moved);
where it does not, emboldened all round and uncarved (UNIFORM). Grown all
round, W's crotches and Q's tail closed; sideways only, its tops flat;
matched loosely, its carving was cut where it is not; by its stems
alone, ragged. Glyphs are spaced as near as typed where their ink comes
nearest, any way (_nearest); figures as far apart as they look on
average, all alike (_optically). Content is as big as it fits typed in
Redaction's Bold, upright, in every style, or smaller where a style's
own is wider (Italic's M): words take the room their blending adds, up
to ROOM, sets too, all together; a glyph nearer its enclosure than CLEAR
of its stroke is fitted alone: its figures nearer, narrowed, then
shrunk, in the middle of where it is off it (⓾). Lines (Hi-/Res) are set
one under the other. On a grid (PHASED), a number or a letter is
pixelated apart from its enclosure, where in a cell it falls best, its
stems filling cells first (shapes.phased); words are pixelated with it,
which keeps more of their counters and their letters off it. On 70,
lowercase is blended and placed as like its smooth drawing as its pixels
come (_liken), but for a few that read as other letters so; on 35 to 70,
a few that blended read as other glyphs are drawn as before
(EMBOLDENED). Content all drawn as before is pixelated as before, with
its enclosure. On 100 (COARSEST), all content is emboldened: from Bold
thinned in an upright Regular, which keeps its carving.

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
    SPECK,
    STEP,
    THIN,
    _centroid,
    _hull,
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
    grooves,
    masters,
    path,
    phased,
    pixelate_glyphs,
    rect,
    runs,
    shaper,
    shrunk,
    sideways,
    stem,
    typed,
    union,
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
T_MAX = 1.0  # farthest content is blended past its own style, Bold's of Regular: further, it swells
T_BOLD = 1.2  # and Bold's, the owner's call: 1.0 left it as heavy as Regular's
# least area of a hole content drawn as before keeps: its carving, closing, leaves less
SLIVER = 400
# what a glyph drawn as before is no heavier than, blended
SIBLINGS = {"Q": "O"}
# Letters drawn as before that do not grow and carve cleanly: emboldened all
# round and uncarved, as 29c0292 drew them, and smoothed as it did
# (UNIFORM_SHORT). Italic's Q came out with a lumpy loop and a loose blob in it
# (🅀 🆀), its y with its arm split from its ball (ⓨ); Bold's s faceted, its
# top cut gone. The fifth audit's: carved, Italic's a u d kept a thorn at
# their foot, its v w a drip over their notch, its W a horn in each crotch,
# its R a spur by its traps, Bold's Q a barb in its tail gap; Bold's W, grown
# on its own, its crotches filled (the owner keeps round 4's). Swept out
# (_moved), Italic's n r kept a thorn and a ledge at their branch, m its second
# wedge a nick, e a knob by its bar's cut, f a slit in its ball, z a thorn at
# its top cut, h k s x ledges, lumps and facets by theirs. For a release; the
# owner's follow-up
UNIFORM = {"Italic": "QyaudvwWRefhkmnrsxz", "Bold": "sQW"}
# most of the white between its strokes a W drawn as before fills, all round
OPEN = 0.5
UNIFORM_SHORT = 12
# Fallback glyphs grown less, as ¹'s stem is of 1's: superscripts
SMALL = "¹²³"
# of what a glyph drawn as before grows sideways: how much its inner joins
# are rounded by, and how thin what grew may be, twice (W's spurs)
CLOSE = 0.5
# how much a glyph drawn as before grows up and down, of how much sideways
FLAT = 0.25
SPUR = 0.5
# how near figures come, and how narrow, for content to fit its enclosure alone (⓾)
TIGHT = (1, 0.8, 0.6)
# how near figures come, of their nearest ink typed, spaced as they look
NEAREST = 0.7
# shortest segment content drawn as before keeps where it runs on through it
# (_smoothed): 6 drawn about a third as big (㎮); and how far it turns there
SHORT = 18
BEND = math.radians(60)
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
# its enclosure: blended, it reads as other glyphs, where so it did not. On
# 70, lowercase as like the smooth font's as it comes (_liken): Italic's e
# as p, h as A, f without its bar; Bold's z as x. The round-2 audit: Italic
# ㉊ as 50, ⓴ as 30, 🅹 in two, 🆁 as ñ on 50, ⓿ 🄌 as S, 🆀 as U, ㎁ ㎃ ㎄
# ㎫ broken or fused, 🄼 fused to its square on 70; Bold ⑪ as U on 50, ➌ ⓭
# as 5, ㎡ a bar on 70; Regular 🅸 as ) on 70, ㎢ as km³ on 35; ㏇'s full
# stop a comma on 35, and Italic ㏞'s V and slash broken; Italic ㎮ off
# centre on 35 and 50, its thin strokes lost. Blended to 1.2, Bold's m counters
# close in ㎚ ㎞ ㎣ ㎦ ㎷ on 50, ⑧ reads A and ⑨ 8 on 70; Italic ⓴'s 0 breaks
# its disc on 70. The round-4 audit: Regular ㉊ as 50, 🅊 as KV, 🅦 as \\\ on
# 50, Ⓗ as X and Ⓜ as x on 70; Italic 🆀 as () and 🆧 as KDR on 35, ⓾ as M,
# ㉏ as 30, Ⓗ as N, ㎨ off centre on 50; Bold 🆧 as HDX on 35, 🆂 ⓢ as 8, ㏛ as Br, 🄷 as i,
# ㊵–㊾'s 4 broken on 50, ➐ as T, ➒ as D, ⑩ ➉ a block, Ⓜ as Ж, ⓿ 🄌 as □,
# ⑥ ➅ as 8, 🅸 as ], 🅾 as -□- on 70. The fifth: Regular ㉈ as J0, ㉉ ㉋ ㉌
# misread on 50.
EMBOLDENED = {
    35: {"Regular": "㎢㏇", "Italic": "㏇㏞㎮🆀🆧", "Bold": "㏇🆧"},
    50: {
        "Regular": "㉈㉉㉊㉋㉌🅊🅦",
        "Italic": "㉊⓴🅹🆁㎮⓾㉏Ⓗ㎨",
        "Bold": "⑪㎚㎞㎣㎦㎷🆂ⓢ㏛🄷㊵㊶㊷㊸㊹㊺㊻㊼㊽㊾",
    },
    70: {
        "Regular": "🅸ⒽⓂ",
        "Italic": "ⓔⓗⓕ⓿🄌🄼🆀㎁㎃㎄㎫⓴",
        "Bold": "ⓩ➌⓭㎡⑧⑨➇➈➐➒⑩➉Ⓜ⓿🄌⑥➅🅸🅾",
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


def heavier(font, text, stems=None, notes=None, t=None, source=None, fell=None, tight=1):
    """`text` in `font` (smooth) made heavier as Redaction's Bold is of its
    Regular (shapes.blend), by `t`, or as far as it takes for the stems of
    its n, I or 1 (_of) to be `stems` (solve), no farther than T_MAX past
    `font`: further, its forms swell and fold. Each glyph is blended
    (_blended), and shrunk back as tall as `font`'s (solve): its letters
    all one height and one weight. A glyph that does not match Redaction's
    Regular and Bold, or blends less than HALF as far, is drawn as before
    from `source` (_before), alone: its word blended. Spaced as typed,
    around their own ink (_spaced), its lines (Hi-/Res) one under the
    other, as content() sets them, each centred on x = 0. Glyphs blended
    less than `t` or only loosely are noted in `notes`, a list, as (char,
    t, t blended to, matched loosely); those drawn as before in `fell`."""
    of = _of(text)
    if t is None:
        t = solve(font, text, stems)
    out = pathops.Path()
    for i, line in enumerate(text.split("\n")):
        reached = []
        p = _spaced(font, line, t, reached, source or font, of, fell, tight)
        if notes is not None:
            notes += [(c, t, *rest) for c, *rest in reached if rest[1] or rest[0] != t]
        down = i * font["OS/2"].sCapHeight * LINES
        out.addPath(p.transform(1, 0, 0, 1, -(p.bounds[0] + p.bounds[2]) / 2, -down))
    k = _height(font, of) / _height(font, of, t)  # back as tall as `font`'s
    out = out.transform(k, 0, 0, k, 0, 0)
    return pathops.op(out, pathops.Path(), pathops.PathOp.UNION)


def _spaced(font, line, t, notes, source, of, fell=None, tight=1):
    """`line` of `font`, each glyph blended by `t` (_blended), or drawn as
    before from `source` (_before), its ink as near the last's as typed
    (_nearest): blended, glyphs grow wider than their advances (Bold's
    "less" ran together, ㉔ and ㉕ apart unlike), and toward each other
    where they come nearest, not where their boxes do (Bold's 4 ran into
    ㊷'s 2, a 1's foot into ⓫'s other 1). Notes (char, t blended to,
    matched loosely) in `notes`, glyphs drawn as before in `fell`."""
    out, last = pathops.Path(), None
    for (char, (_, x, y)), was in zip(
        zip(line, _set(font, _shaper(font), line)[0]), _typed(font, line)
    ):
        if path(font, char).bounds == (0, 0, 0, 0):  # a space
            continue
        blended = _blended(font, char, t)
        if blended is None or abs(blended[1]) < abs(t) * HALF:  # no match, or paler than the rest
            p = _before(font, source, char, t, of)
            if fell is not None:
                fell.append(char)
        else:
            p, done, loosely = blended
            notes.append((char, done, loosely))
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
    Redaction's Regular and Bold as they are: matched loosely, its carving
    is not where theirs is (W, Q). Where it folds or its carving closes
    before `t`, as far as it blends, by a STEP of `t`, and no further: grown
    another way, its carving is cut again where it was not (Italic's k, y
    in Bold). (path, t blended to, False), or None if it does not match."""
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
        return (p, u, False) if p is not None else None
    return path(font, char), 0, False


def _of(text):
    """The glyph whose stems `text` is made heavier by: I if it has a
    capital (℡), so that none of its glyphs is blended further than alone:
    solved on n, its capitals would be past ℡'s, where Bold's S folds; else
    n if it has a lowercase letter, else 1."""
    if any(c.isupper() for c in text):
        return "I"
    return "n" if any(c.islower() for c in text) else "1"


def solve(font, text, stems, past=0):
    """How far `text` of `font` is blended for the stems of its n, I or 1
    (_of) to be `stems` once shrunk back as tall as `font`'s (heavier), as
    the superscript letters are, no farther than T_MAX past its style:
    `past`, 1 where it is Bold's (🄫, Italic's, in Bold)."""
    of, (regular, bold) = _of(text), masters()
    s, x = stem(path(font, of)), _height(font, of)
    ds = stem(path(bold, of)) - stem(path(regular, of))
    dx = _height(bold, of) - _height(regular, of)
    # (s + t ds) / (x + t dx) = stems / x
    return min(past + T_MAX, x * (stems - s) / (ds * x - stems * dx))


@functools.cache
def _before(font, source, char, t, of):
    """`char` drawn as before: `source`'s (as approved), emboldened as much
    as its own n, I or 1 of `font` blended by `t` takes to be as heavy, as
    its word's blended letters are, its inner joins rounded and the narrow
    whites emboldening closes kept (_bold): solved on the word's capital,
    Italic's lowercase came out as heavy as it. Q no heavier than O's bowl
    (SIBLINGS). No further than its pieces and counters stay. Holes under
    SLIVER filled."""
    p = path(source, char)
    own = _of(char) if char.isalnum() else of
    uniform = char in UNIFORM.get(font["name"].getDebugName(2), "")
    flat = 1 if uniform else FLAT
    # Superscripts as ¹ is of 1: ³ came out heavy
    ratio = stem(path(source, "¹")) / stem(path(source, "1")) if char in SMALL else 1
    amount = max(-THIN, _amount(font, source, own, t, own, flat=flat) * ratio)
    if char in SIBLINGS:  # no heavier than its sibling's blended
        sibling = SIBLINGS[char]
        amount = min(amount, _amount(font, source, sibling, t, sibling, True, flat))
    pieces, gaps = _pieces(p), len(grooves(p)) if uniform and char in SIBLINGS else 0
    # Uniform, W's middle no more than OPEN filled, as round 4 drew it
    s = stem(path(source, own))
    air = (
        [c for c in _air(p).contours if abs(c.area) >= (1.5 * s) ** 2]
        if uniform and char in "Ww"
        else []
    )

    def closes(q):
        """Whether its pieces or counters change; uniform, Q's tail fuses to
        its bowl, or W's middle fills more than OPEN."""
        if _pieces(q) != pieces or (gaps and len(grooves(q)) < gaps):
            return True
        left = _air(q) if air else None
        return any(
            abs(pathops.op(c, left, pathops.PathOp.INTERSECTION).area) < (1 - OPEN) * abs(c.area)
            for c in air
        )

    q = _bold(p, amount, uniform)
    while amount > 0.5 and closes(q):
        amount *= 0.8
        q = _bold(p, amount, uniform)
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
    # Rounded, as the font will be: skia-pathops fails on it, spacing it
    rounded = pathops.Path()
    # Thinned or uniform, as 29c0292 smoothed it: Regular's W serifs slanted
    smooth = {} if amount > 0.5 and not uniform else {"short": UNIFORM_SHORT, "bend": math.pi}
    glyph(_smoothed(q.transform(k, 0, 0, k, 0, dy), **smooth)).draw(pathops.PathPen(rounded), None)
    return rounded


def _smoothed(p, short=SHORT, bend=BEND):
    """`p` without its segments shorter than `short` where it runs on
    through them, turning less than BEND, or a third as short, which
    growing leaves along its curves and round its tips: the next goes on
    from the last, no further off than they are long. Where it turns more
    (a serif's end), kept: dropped, W's serifs came out slanted."""
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
            if end != start and (run < short / 3 or run < short and turn < bend):
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
def _amount(font, source, char, t, of, blended=False, flat=FLAT):
    """How much `char` of `source` is emboldened for the stems of its `of` to
    be those of `font` blended by `t`, once as tall as `font`'s `char` would
    blend; or, `blended`, those of `char` blended itself (O, for Q). Grown
    `flat` as much up and down as sideways (1: all round)."""
    regular, bold = masters()
    if blended:
        stems = stem(_blended(font, char, t)[0])
    else:
        stems = stem(path(font, of)) + t * (stem(path(bold, of)) - stem(path(regular, of)))
    tall = _height(font, char, t)
    h = path(source, char).bounds
    h = h[3] - h[1]
    s = stem(path(source, of))
    # Grown sideways, flat as much up and down: (s + 2a) tall / (h + 2 flat a) = stems
    grown = (stems * h - s * tall) / (2 * (tall - flat * stems))
    if grown >= 0:
        return grown
    # Thinned all round: (s + 2a) tall / (h + 2a) = stems
    return (stems * h - s * tall) / (2 * (tall - stems))


def _top(font, char, t):
    """Where the top of `char` of `font` blended by `t` is."""
    regular, bold = masters()
    return path(font, char).bounds[3] + t * (
        path(bold, char).bounds[3] - path(regular, char).bounds[3]
    )


def _bold(p, amount, uniform=False):
    """`p` grown by `amount` sideways and a quarter as much up and down
    (_oval): its stems grow, its serifs and level hairlines hardly, as
    Redaction's Bold is of its Regular; grown all round, W's crotches and
    the gaps between its serifs closed, Q's bowl and s's counters filled,
    its hairlines heavy. Its carving filled before, its inner joins rounded
    by half as much after (CLOSE; emboldened, Italic's exit hooks pinched to
    corners), what grew thinner than as much taken off (SPUR, _spurless),
    and the whites growing closes kept (_whites):
    Redaction's carving, the gaps between W's serifs. Its pieces under a
    quarter of the largest (i's dot, a full stop) scaled about their middle
    by half as much, not grown, and kept as far from it: grown, Italic's i
    dot came out flat; scaled as far, too big and near its stem. Less than
    half a unit, as it is: skia-pathops drops outlines stroked so thin
    (Regular's W, from Bold's). Thinned, as it is thinned."""
    if abs(amount) < 0.5:
        return p
    if amount < 0 or uniform:
        q = embolden(p, amount)
    else:
        # Its carving filled first, cut back after: grown, its notches stood
        # out as teeth
        q = _oval(union_paths([p, *(gap for gap, _ in grooves(p))]), amount)
        q = _spurless(p, _closed(q, amount * CLOSE), amount * SPUR)
        q = _whites(p, q, amount)
    contours = list(pathops.op(p, pathops.Path(), pathops.PathOp.UNION).contours)
    largest = max(contours, key=lambda c: abs(c.area))
    for c in contours:
        if c.clockwise != largest.clockwise or abs(c.area) >= abs(largest.area) / 4:
            continue
        x0, y0, x1, y1 = c.bounds
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        f = 1 + amount / max(x1 - x0, y1 - y0)
        # Above it (a dot), its foot where it was, or where its top grows,
        # all round; else (a full stop) its top, or its foot
        rise = amount if uniform else 0
        dy = (rise + (f - 1) * (y1 - y0) / 2) * (1 if y0 >= largest.bounds[3] - 1 else -1)
        q = pathops.op(q, embolden(c, abs(amount) + 1), pathops.PathOp.DIFFERENCE)
        scaled = c.transform(f, 0, 0, f, cx - f * cx, cy - f * cy + dy)
        q = pathops.op(q, scaled, pathops.PathOp.UNION)
    return q


def _oval(p, amount):
    """`p` grown by `amount` sideways and FLAT as much up and down: round
    about an oval as wide as twice `amount`, so its stems grow, its serifs
    and level hairlines a little, and its tops and balls stay round. Swept
    sideways only, they came out flat (the owner's flat tops, square balls).
    Where skia-pathops fails, a little further, else swept."""
    tall = p.transform(1, 0, 0, 1 / FLAT, 0, 0)
    for k in (1, 1.01, 0.99, 1.02):
        try:
            return embolden(tall, amount * k).transform(1, 0, 0, FLAT, 0, 0)
        except pathops.PathOpsError:
            continue
    return sideways(p, amount, pointed=False)


def _spurless(p, q, o):
    """`q`, `p` grown, without what grew thinner than twice `o`: sideways,
    a notch of Redaction's (where W's hairline meets its stem) ran out
    into a shelf as long as it grew."""
    for rounded in (False, True):
        try:
            opened = embolden(embolden(q, -o, round=rounded), o, round=rounded)
            return union_paths([p, opened])
        except pathops.PathOpsError:
            continue
    return q


def _closed(p, r):
    """`p` grown by `r`, round, and thinned back: its concave joins and its
    whites narrower than twice `r` filled. Where skia-pathops fails, with
    sharp corners, or a little further."""
    for k, rounded in ((1, True), (1, False), (1.01, True), (0.99, True)):
        try:
            return embolden(embolden(p, r * k, round=rounded), -r * k, round=rounded)
        except pathops.PathOpsError:
            continue
    return p


def _whites(p, q, amount):
    """`q`, `p` grown by `amount`, with the whites of `p` growing closes
    kept as Redaction draws them, each cut back out of what grew: its
    carving (shapes.grooves), moved out to the new edges it opens to
    (_moved), as deep and as pointed (Italic's n h d came out with
    square-ended slots), and its gaps open at both ends (between W's
    serifs), carried on out at each. Not where it would leave a piece or a
    counter of its own: cut so, it floats (Italic's z, W). Whites closed a
    part only are not: kept, they left horns of what grew beside them."""
    reach = amount * (1 + CLOSE)
    narrow = pathops.op(_closed(p, reach), p, pathops.PathOp.DIFFERENCE)
    traps = union_paths([gap for gap, _ in grooves(p)])
    holes = max(_pieces(q)[1], _pieces(p)[1])
    o = reach / 4.5  # a third of what it grew
    for white in narrow.contours:
        if abs(white.area) < SLIVER:
            continue
        mouths = _mouths(p, white)
        trap = abs(pathops.op(white, traps, pathops.PathOp.INTERSECTION).area) > SPECK
        points = _hull(list(white.points))
        if trap and mouths:  # a wedge: moved out to the new edges (Q's tail gap, at each)
            cut = union_paths([_moved(white, mouth, q, amount) for mouth in mouths])
        elif len(mouths) > 1:  # open at both ends (W's serifs): on out at each
            ends = []
            for ux, uy in mouths:
                ends += [(x + ux * 1.5 * reach, y + uy * 1.5 * reach) for x, y in points]
            cut = union([_hull(points + ends)])
        else:
            continue
        cut = pathops.op(cut, p, pathops.PathOp.DIFFERENCE)  # only what grew
        trial = _dehorned(_crumbs(pathops.op(q, cut, pathops.PathOp.DIFFERENCE)), q, cut, o)
        if (
            _pieces(trial)[0] == _pieces(q)[0]
            and _pieces(trial)[1] <= holes
            and _spikes(trial, o) <= _spikes(q, o) + SLIVER
        ):
            q = trial
    return q


def _moved(white, mouth, q, amount):
    """Redaction's wedge `white`, moved out along its `mouth` till its mouth
    is in the white of `q` (grown), as long, a little longer to open: cut
    so, it is as deep and as pointed as Redaction's from the new edge.
    Scaled about its tip out to it, it came out longer, and where it ended
    inside a narrow white (W's crotches), what grew past it stood as a
    tooth."""
    ux, uy = mouth
    points = _hull(list(white.points))
    along = [x * ux + y * uy for x, y in points]
    length = max(max(along) - min(along), 1)
    tx, ty = points[along.index(min(along))]
    # Its last fifth, the mouth: a band across it
    nx, ny = -uy, ux
    far = max(abs((x - tx) * nx + (y - ty) * ny) for x, y in points) + 1
    a, b = min(along) + 0.8 * length, max(along) + 1
    corners = ((a, -far), (b, -far), (b, far), (a, far))
    band = union([[(ux * u + nx * v, uy * u + ny * v) for u, v in corners]])
    mouth = pathops.op(white, band, pathops.PathOp.INTERSECTION)
    d = 0
    while d < 3 * amount:
        moved = mouth.transform(1, 0, 0, 1, ux * d, uy * d)
        inked = abs(pathops.op(moved, q, pathops.PathOp.INTERSECTION).area)
        if inked <= 0.02 * abs(moved.area):
            break
        d += 2
    f = 1 + 0.1 * amount / length
    wedge = white.transform(f, 0, 0, f, tx - f * tx, ty - f * ty)
    if d < 1:
        return wedge
    # All it sweeps moving out, where it was to where it is: moved alone, the
    # edge it left stood beside it, as horns (Italic's W), thorns (a's foot)
    along = wedge.transform(ux, -uy, uy, ux, d / 2, 0)  # its mouth's way along x
    swept = sideways(along, d / 2, pointed=False)
    return swept.transform(ux, uy, -uy, ux, 0, 0)


def _dehorned(p, q, cut, o):
    """`p`, `q` with `cut` out, without the horns the cut leaves: what of it
    thinner than twice `o` touches the cut and was not so in `q` (the grown
    serif beside W's crotches, Q's tail gap)."""
    try:
        opened = embolden(embolden(p, -o, round=True), o, round=True)
    except pathops.PathOpsError:
        return p
    horns = pathops.op(p, opened, pathops.PathOp.DIFFERENCE)
    near = embolden(cut, o)
    out = pathops.Path()
    for h in horns.contours:
        if abs(pathops.op(h, near, pathops.PathOp.INTERSECTION).area) > SPECK:
            out.addPath(h)
    if not list(out.contours):
        return p
    return _crumbs(pathops.op(p, out, pathops.PathOp.DIFFERENCE))


def _spikes(p, o):
    """How much of `p` is thinner than twice `o`: what opening it by `o`
    takes off. A cut that leaves more stands Redaction's own thin teeth, or
    what grew beside it, as spikes (Italic's k, z)."""
    try:
        opened = embolden(embolden(p, -o, round=True), o, round=True)
    except pathops.PathOpsError:
        return 0
    return abs(pathops.op(p, opened, pathops.PathOp.DIFFERENCE).area)


def _crumbs(p):
    """`p` without its pieces and holes under SLIVER: crumbs of what grew a
    cut leaves by its edge, and pinholes."""
    contours = list(p.contours)
    if not contours:
        return p
    kept = pathops.Path()
    for c in contours:
        if abs(c.area) >= SLIVER:
            kept.addPath(c)
    return pathops.op(kept, pathops.Path(), pathops.PathOp.UNION)


def _mouths(p, white):
    """Which ways a white of `p` opens to the rest of its white: unit
    directions from its middle to where it touches it."""
    points = _hull(list(white.points))
    cx, cy = _centroid(points)
    air = pathops.op(embolden(white, 2), union_paths([p, white]), pathops.PathOp.DIFFERENCE)
    out = []
    for mouth in air.contours:
        if abs(mouth.area) < 2:
            continue
        mx, my = _centroid(list(mouth.points))
        d = math.hypot(mx - cx, my - cy) or 1
        out.append(((mx - cx) / d, (my - cy) / d))
    return out


def _air(p):
    """The white of `p` within its convex hull, but its counters: between
    its strokes (W's middle)."""
    outer = max(p.contours, key=lambda c: abs(c.area)).clockwise
    filled = pathops.Path()
    for c in p.contours:
        if c.clockwise == outer:
            filled.addPath(c)
    p = pathops.op(filled, pathops.Path(), pathops.PathOp.UNION)
    # Its hull on its outline, not its control points, which growing moves
    on, last = [], (0, 0)
    for verb, pts in p.segments:
        if verb in ("curveTo", "qCurveTo") and len(pts) == 3:
            (x0, y0), (x1, y1), (x2, y2), (x3, y3) = last, *pts
            for t in (0.25, 0.5, 0.75):
                u = 1 - t
                on.append(
                    (
                        u**3 * x0 + 3 * u * u * t * x1 + 3 * u * t * t * x2 + t**3 * x3,
                        u**3 * y0 + 3 * u * u * t * y1 + 3 * u * t * t * y2 + t**3 * y3,
                    )
                )
        if pts:
            last = pts[-1]
            on.append(last)
    hull = _hull(on)
    h = pathops.Path()
    h.moveTo(*hull[0])
    for pt in hull[1:]:
        h.lineTo(*pt)
    h.close()
    return pathops.op(h, p, pathops.PathOp.DIFFERENCE)


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
    not blend so far or match only loosely (heavier), with `notes`, the
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
        # Bold's to T_BOLD; Italic's, in Bold (🄫), as far past Bold as Bold's own
        bold = smooth["OS/2"].usWeightClass >= 700
        past = (1 if slanted else 0) + T_BOLD - T_MAX if bold else 0
        drawn = {}
        for cp in heavy:
            ts[cp] = solve(font, contents[cp], thick / max(scales[cp], floor), past)
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
            near, fits = _near(kind, frame, cx, cy, radius, apart, place)
            for cp in heavy:
                at = room[cp]
                if not near(drawn[cp][0], at):
                    continue
                pair = contents[cp].isdigit() and len(contents[cp]) > 1
                found = None
                for tight in TIGHT if pair else (1,):
                    q = (
                        drawn[cp][0]
                        if tight == 1
                        else heavier(font, contents[cp], t=ts[cp], source=source, tight=tight)
                    )
                    for across in ACROSS:
                        if fits(q.transform(across, 0, 0, 1, 0, 0), at):
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
                        lo, hi = (mid, hi) if fits(q, mid) else (lo, mid)
                    room[cp] = lo
                # In the middle of where it is off its enclosure, across: on
                # its box, ⓾'s 1 stood near its ring, its 0 far
                clear = [d for d in range(-80, 81, 4) if not near(q, room[cp], True, d)]
                shaped[cp] = tight, across, (min(clear) + max(clear)) / 2 if clear else 0
                if notes:
                    log(f"{notes} {style} {chr(cp)}: {tight:.1f} as near, {across:.2f} as wide")
        for cp, less in room.items() if kind != "raised" else ():
            if less < scales[cp]:
                scales[cp] = less
                if cp in drawn:
                    ts[cp] = solve(font, contents[cp], thick / max(less, floor), past)
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
                for char, t, done, loosely in noted if notes else []:
                    how = ", matched loosely" if loosely else ""
                    log(f"{notes} {style} {chr(cp)} {char}: t {t:.2f}, blended to {done:.2f}{how}")
                if fell and notes:
                    log(f"{notes} {style} {chr(cp)} {''.join(fell)}: drawn as before")
            else:
                # Smaller than digits (🆩, ㎑), not heavier than them: strokes would merge
                p = embolden(p, max(-THIN, (thick / max(scale, height) - own) / 2))
            tight, across, shift = shaped.get(cp, (1, 1, 0))
            p = p.transform(across, 0, 0, 1, 0, 0)
            # Cleaned where it has letters drawn as before, in the smooth font
            clean = not grid and cp in drawn and bool(drawn[cp][2])
            enclosed[cp] = kind, frame, place(p, kind, scale, cp in shaped, shift, clean)
            if cp in drawn and cp not in before:
                again[cp] = font, contents[cp], kind, scale, source, shaped.get(cp)
    if solved:
        return ts

    def redraw(cp, t):
        font, text, kind, scale, source, shape = again[cp]
        tight, across, shift = shape or (1, 1, 0)
        p = heavier(font, text, t=t, source=source, tight=tight)
        p = p.transform(across, 0, 0, 1, 0, 0)
        return place(p, kind, scale, shape is not None, shift)

    return enclosed, ts, redraw


def _near(kind, frame, cx, cy, radius, apart, place):
    """Whether content (a path) of `kind` placed at a scale (`place`) comes
    nearer its enclosure `frame` than `apart`, and whether it fits."""
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

    def fits(p, scale):
        """Whether `p`, centred on its box, is off it somewhere across."""
        return any(not near(p, scale, True, d) for d in range(-80, 81, 8))

    return near, fits


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
    so far reads as ▼, Italic's e as p."""
    ts, redraw, lightest, label = eased
    cps = {CODEPOINTS[cp]: cp for cp in ts}
    theirs = [widths(cells(g, grid)[0]) for g in like]
    theirs = [sum(w) / len(w) for w in zip(*theirs)]
    tried, smooth, counted = {}, {}, {}
    for name, (_, _, p) in apart.items():
        cp, t, light = cps[name], ts[cps[name]], lightest[cps[name]]
        steps = [light + k * EASE for k in range(int((t - light) / EASE) + 1)]
        for k, u in enumerate(sorted({*steps, t}) if t > light else [t]):
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
                score = (rank[0], *_lost(counted[name], pixels, grid), -alike)
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


def _lost(counted, g, grid):
    """How many pieces and counters pixel glyph `g` has fewer than `counted`
    (_counted), and how many counters more: pixels joined at a corner are
    one, counters closed by every pixel (shapes.cells)."""
    _, _, (pieces, counters, _) = cells(g, grid)
    lost = max(0, counted[0] - pieces) + max(0, counted[1] - len(counters[0]))
    return lost, max(0, len(counters[0]) - counted[1])


def _ease(apart, contents, grid, like, away, eased):
    """_pixelated: {name: pixel content} of the content of `apart` whose
    pixels in `contents` lose a piece or a counter (_lost), blended less
    till they lose none: a piece of it as Redaction sets it (blended,
    figures set close are one, ⑪), a counter of its drawing blended as far
    as here or as in the smooth font, and no more counters than it had.
    Where none holds, it stays as blended: lighter, it would only be paler
    than the rest, and no better."""
    ts, redraw, lightest, label = eased
    cps = {CODEPOINTS[cp]: cp for cp in ts}
    t = {name: ts[cps[name]] for name in apart}
    light = {name: lightest[cps[name]] for name in apart}
    counted = {}
    for name, (_, _, p) in apart.items():
        lighter = p if t[name] <= light[name] else redraw(cps[name], light[name])
        holes = max(_counted(p)[1], _counted(lighter)[1])
        counted[name] = _counted(redraw(cps[name], 0))[0], holes
    was = {name: _lost(counted[name], contents[name], grid) for name in apart}
    failing = [name for name in apart if t[name] > light[name] and was[name][0]]
    out = {}
    while failing:
        drawn = {}
        for name in failing:
            t[name] = max(t[name] - EASE, light[name])
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
            lost, extra = _lost(counted[name], placed[name], grid)
            if not lost and extra <= was[name][1]:  # and no counter more
                out[name] = placed[name]
                log(f"{label} {chr(cp)}: t {ts[cp]:.2f} eased to {t[name]:.2f}")
            elif t[name] <= light[name]:
                log(f"{label} {chr(cp)}: t {ts[cp]:.2f} kept, none holds down to {t[name]:.2f}")
        failing = [n for n in failing if n not in out and t[n] > light[n]]
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
            eased = ts, redraw, lightest, f"{grid} {style}"
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
