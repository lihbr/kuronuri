"""Fullwidth forms of Redaction's letters, digits and signs: ＡＢＣ ０１２ ！？,
and 〒, the Japanese postal mark, from its T.

Japanese text sets Latin letters and digits fullwidth (２０２６年), one em
each. Each is Redaction's own glyph (a component) centred in the em, so in
the numbered variants it keeps MCKL's pixels. So is the punctuation that
does not turn in vertical text (！ ？ ； ＂).

， ． ： ＝ and － are Redaction's too, where Noto Serif JP's sit (， at
the bottom left of the em), and so are their vertical forms, as Noto Serif
JP's: ， and ． moved to the top right, ： and ＝ turned a quarter, which
`vert` and `vrt2` swap in. The other punctuation that turns in vertical text
stays Noto Serif JP's (（ becomes ︵), as do ～ and ＿.

〒 is drawn by hand from T (shapes.drawn): its top again above it, the
bars as far apart as Noto Serif JP's, their beaks cut short of the gap so
they read as a pair. It stands upright in Italic too, as Japanese does:
Italic's T unslanted, its stem as thick as its slanted one. On 10 to 70 it
is pixelated where in a cell it falls best, its bars whole cells apart so
they come out alike; on 100 it is cut from MCKL's pixel T, whose bar row is
carved there, its lower bar laid straight as the top one.

`fwid`, `hwid` and `pwid` swap characters for their width forms. Noto Serif
JP's lose what the build replaces: its ASCII by Redaction's, its fullwidth
forms by these, each substitution going with either side of it (fwid kept
29 of 253, and ABC stayed ABC), and it never had halfwidth katakana in
`hwid`. They are made again on the merged font, from what Unicode decomposes
to what (width_forms): `fwid` turns ABC123 into ＡＢＣ１２３ and ｱｲｳ ｶﾞ into アイウ ガ;
`hwid` turns ＡＢＣ into Redaction's ABC, there being no halfwidth Latin, and
アイウ ガ into ｱｲｳ ｶﾞ (voiced kana into two); `pwid` turns ＡＢＣ into ABC,
which are proportional. Noto Serif JP's that are left stay first: its
proportional and halfwidth punctuation. `ruby` is Noto Serif JP's: of five
substitutions, for Bopomofo tone marks, the two whose glyphs are left.
"""

import unicodedata

import numpy as np
import pathops
from fontTools.otlLib import builder as otl
from fontTools.pens.ttGlyphPen import TTGlyphPen

import layout
import pixel

from .shapes import (
    _placed,
    _regions,
    add,
    cells,
    composite,
    drawn,
    glyph,
    path,
    rect,
    runs,
    slope,
    union_paths,
    widths,
)

ASCII = "!\"#$%&'*+/0123456789;<>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ\\^`abcdefghijklmnopqrstuvwxyz"
# fullwidth code point: the character it is the fullwidth form of
SOURCES = {0xFF01 + ord(c) - 0x21: c for c in ASCII} | {
    0xFFE0: "¢",
    0xFFE1: "£",
    0xFFE5: "¥",
    0xFFE6: "₩",
}
HALFWIDTH = {0xFFE8: "|"}  # in half an em
# Punctuation that turns in vertical text: (source, the middle of its ink in
# the em, as Noto Serif JP's, or None for the middle of the em, its vertical
# form: moved by (x, y), or turned a quarter)
PUNCTUATION = {
    0xFF0C: (",", 150, (666, 674)),
    0xFF0E: (".", 151, (670, 670)),
    0xFF1A: (":", None, "turned"),
    0xFF1D: ("=", None, "turned"),
    0xFF0D: ("−", None, None),
}
VERTICAL = {f"uni{cp:04X}": f"uni{cp:04X}.vert" for cp, (*_, v) in PUNCTUATION.items() if v}
TURN_AROUND = (500, 380)  # middle of the ideographic em box, which turned forms turn about
POSTAL = 0x3012
GAP = 0.18  # between the bars of 〒 cut from T, over its height
STEM = 0.3  # of the height of 〒 and T, where their stems are measured on a grid
CUT = (100,)  # grids 〒 is cut from MCKL's pixel T on, not pixelated from its drawing
CODEPOINTS = {cp: f"uni{cp:04X}" for cp in [*SOURCES, *HALFWIDTH, *PUNCTUATION, POSTAL]}
# Halfwidth sound marks: the spacing ones they are the halfwidth forms of,
# which Unicode decomposes to the combining ones
MARKS = {0xFF9E: 0x309B, 0xFF9F: 0x309C}
# What Noto Serif JP's width features map besides Unicode's width forms
# that both characters are left of after the build, by feature, {from: to}:
# ￨ is | in half an em. Where they differ from Unicode's, Unicode's are kept
# (/ to ／, not ∕), and its spaces are left out: it makes the space an en
# space and an en space an em one, so spaces would change width to whatever
# the font's en and em spaces are, which are not Noto's; `fwid` makes the
# space the ideographic one instead, Unicode's mapping
NOTO = {
    "fwid": {0xB7: 0x30FB, 0x2014: 0x2015},
    "hwid": {0x7C: 0xFFE8},
    "pwid": {0x2015: 0x2014, 0x301C: 0x7E, 0x2215: 0x2F, 0x2035: 0x60, 0xFFE8: 0x7C},
}
ALTERNATES = []
SAMPLES = [
    "２０２６年１０月２２日",
    "ＮＨＫとＪＲ東日本",
    "ＡＢＣ ABC ０１２ 012",
    "￥１,０００",
    "＃１ ＠ｌｉｈｂｒ",
    "本当！？ ええ；「ＯＫ」",
    "〒100-0001 東京都",
    "はい、そうです。１，０００円：＝－",
    "ABC abc 123 !? ¥ ｱｲｳ ｶﾞﾊﾟｳﾞ (fwid)",
    "ＡＢＣ ａｂｃ １２３ アイウ ガパヴ。「ー」 (hwid, pwid)",
]


def add_glyphs(font, smooth, grid=None):
    glyf, hmtx, cmap = font["glyf"], font["hmtx"], font.getBestCmap()
    em = pixel.snap_advance(1000, grid or 1)
    half = pixel.snap(em / 2, grid or 1)
    glyphs = {}
    for sources, width in ((SOURCES, em), (HALFWIDTH, half)):
        for cp, c in sources.items():
            src = cmap[ord(c)]
            dx = (width - hmtx[src][0]) / 2
            glyphs[CODEPOINTS[cp]] = (composite(font, [(src, dx, 0)], grid), width)
    for cp, (c, middle, _) in PUNCTUATION.items():
        src = cmap[ord(c)]
        glyf[src].recalcBounds(glyf)
        ink = (glyf[src].xMin + glyf[src].xMax) / 2
        dx = (middle if middle is not None else em / 2) - ink
        glyphs[CODEPOINTS[cp]] = (composite(font, [(src, dx, 0)], grid), em)
    glyphs[CODEPOINTS[POSTAL]] = (_postal(font, smooth, grid, em), em)
    add(font, glyphs, CODEPOINTS)

    # Vertical forms: moved, or turned a quarter clockwise about the middle of
    # the em box, from the middle of their ink, as components
    vertical = {}
    for cp, (_, _, form) in PUNCTUATION.items():
        name = CODEPOINTS[cp]
        if not form:
            continue
        pen = TTGlyphPen(glyf)
        if form == "turned":
            glyf[name].recalcBounds(glyf)
            x, y = (glyf[name].xMin + glyf[name].xMax) / 2, (glyf[name].yMin + glyf[name].yMax) / 2
            cx, cy = (pixel.snap(v, grid or 1) for v in TURN_AROUND)
            dx, dy = pixel.snap(cx - y, grid or 1), pixel.snap(cy + x, grid or 1)
            pen.addComponent(name, (0, -1, 1, 0, dx, dy))
        else:
            pen.addComponent(name, (1, 0, 0, 1, *(pixel.snap(v, grid or 1) for v in form)))
        vertical[VERTICAL[name]] = (pen.glyph(), em)
    add(font, vertical, {})


def add_features(font):
    """Add the vertical forms to `vert` and `vrt2`, and the width forms to
    `fwid`, `hwid` and `pwid` (width_forms), of the merged font."""
    table = font["GSUB"].table
    for tag in ("vert", "vrt2"):
        layout.extend_feature(table, tag, otl.buildLookup([otl.buildSingleSubstSubtable(VERTICAL)]))
    cmap = font.getBestCmap()
    for tag, (ligatures, single, multiple) in width_forms(set(cmap)).items():
        covered = _covered(table, tag)
        ligatures = {
            tuple(cmap[c] for c in seq): cmap[cp]
            for seq, cp in ligatures.items()
            if cmap[seq[0]] not in covered
        }
        single = {cmap[a]: cmap[b] for a, b in single.items() if cmap[a] not in covered}
        multiple = {
            cmap[a]: [cmap[c] for c in b] for a, b in multiple.items() if cmap[a] not in covered
        }
        # ﾊﾟ to パ before ﾊ to ハ
        for built in (
            ligatures and otl.buildLigatureSubstSubtable(ligatures),
            single and otl.buildSingleSubstSubtable(single),
            multiple and otl.buildMultipleSubstSubtable(multiple),
        ):
            if built:
                layout.extend_feature(table, tag, otl.buildLookup([built]))


def width_forms(cps):
    """The width forms among the code points `cps`, by feature: ({sequence:
    code point}, {code point: code point}, {code point: sequence}), to
    ligate, swap and split. `fwid` turns characters into their fullwidth
    form (A to Ａ, the space to the ideographic one) and halfwidth ones into
    theirs (ｱ to ア, ﾊﾟ to パ); `hwid` the other way, voiced kana into two
    (パ to ﾊﾟ), and fullwidth Latin into Redaction's, there being no
    halfwidth Latin; `pwid` fullwidth Latin into Redaction's, which is
    proportional. Each as Unicode decomposes them (<wide>, <narrow>), and
    as Noto Serif JP's did before the build replaced either side (NOTO)."""
    out = {tag: ({}, {}, {}) for tag in ("fwid", "hwid", "pwid")}
    fwid, hwid, pwid = (out[tag][1] for tag in ("fwid", "hwid", "pwid"))
    narrow = {}  # full: half
    for cp in sorted(cps):
        kind, *of = unicodedata.decomposition(chr(cp)).split() or [""]
        if kind in ("<wide>", "<narrow>") and len(of) == 1:
            of = MARKS.get(cp, int(of[0], 16))
            if of not in cps:
                continue
            if kind == "<wide>":
                fwid.setdefault(of, cp)
                hwid.setdefault(cp, of)
                pwid.setdefault(cp, of)
            else:
                narrow.setdefault(of, cp)
                fwid.setdefault(cp, of)
    for half in MARKS:  # the combining sound marks become halfwidth too
        narrow[int(unicodedata.decomposition(chr(half)).split()[1], 16)] = half
    for full, half in narrow.items():
        if full in cps and half in cps:
            hwid.setdefault(full, half)
    for cp in sorted(cps):  # ガ: カ and the voiced sound mark, canonically
        decomposed = unicodedata.decomposition(chr(cp)).split()
        halves = [narrow.get(int(c, 16)) for c in decomposed if c[0] != "<"]
        if len(halves) == 2 and decomposed[0][0] != "<" and all(h in cps for h in halves):
            out["hwid"][2][cp] = halves
            out["fwid"][0][tuple(halves)] = cp
    for tag, pairs in NOTO.items():
        for a, b in pairs.items():
            if a in cps and b in cps:
                out[tag][1].setdefault(a, b)
    return out


def _covered(table, tag):
    """The glyphs the lookups of the features `tag` of `table` substitute
    already: Noto Serif JP's, those of its glyphs the build kept."""
    covered = set()
    for rec in table.FeatureList.FeatureRecord:
        if rec.FeatureTag != tag:
            continue
        for i in rec.Feature.LookupListIndex:
            for st in table.LookupList.Lookup[i].SubTable:
                st = getattr(st, "ExtSubTable", st)
                for attr in ("mapping", "ligatures", "alternates"):
                    covered |= set(getattr(st, attr, {}))
    return covered


def _postal(font, smooth, grid, em):
    """〒 of `font`, centred in `em`: drawn by hand from its T (shapes.drawn),
    on a grid pixelated where in a cell it falls best, of the spots where
    its stem is as many cells across as MCKL's T (across its slant), its
    pixels join along edges (_square) and its beaks come out even (_even);
    on CUT, or without a drawing, cut from T (_cut)."""
    hand = drawn(smooth["name"].getDebugName(2)).get(chr(POSTAL))
    if hand is None or grid in CUT:
        return _cut(font, smooth, grid, em)
    g = grid or 1
    p = hand[0]
    if grid:
        # The bars as far apart as whole cells, so they fall in them alike
        top, lower = sorted(p.contours, key=lambda c: -c.bounds[1])
        drop = top.bounds[3] - lower.bounds[3]
        p = union_paths([top.transform(1, 0, 0, 1, 0, pixel.snap(drop, g) - drop), lower])
    left, _, right, _ = p.bounds
    out = glyph(p.transform(1, 0, 0, 1, pixel.snap((em - right - left) / 2, g), 0))
    if grid:
        t = font["glyf"][font.getBestCmap()[ord("T")]]
        t.recalcBounds(font["glyf"])
        rows, theirs = (t.yMin, t.yMax), widths(cells(t, grid)[0])
        placed = [o[2] for o in _placed({"〒": out}, grid, rows, theirs, False, None, True)["〒"]]
        y = (t.yMax - t.yMin) * STEM
        # as thick as T's measured across its slant, as 〒 stands upright
        stem = [pixel.snap(w / (1 + slope(smooth) ** 2) ** 0.5, g) for w in _across(t, y)]
        out = min(
            placed,
            key=lambda o: (_across(o, y) != stem, not _square(o, grid), not _even(o, grid)),
        )
        out.recalcBounds(None)
        out.coordinates.translate((pixel.snap((em - out.xMax - out.xMin) / 2, g), 0))
    return out


def _across(g, y):
    """How wide the stroke of pixel glyph `g` is at height `y`: its stem."""
    p = pathops.Path()
    g.draw(pathops.PathPen(p), None)
    return [b - a for a, b in runs(p, y=y)]


def _even(g, grid):
    """Whether the top bar of pixel glyph `g`, its rows down to the gap,
    comes out as even as drawn: its beaks as wide as each other, under it."""
    on = cells(g, grid)[0]
    bar = on[: np.argmin(on.any(axis=1))]
    (cols,) = np.nonzero(bar[0])
    inside = bar[:, cols[0] : cols[-1] + 1]
    return inside.sum() == bar.sum() and (inside == inside[:, ::-1]).all()


def _square(g, grid):
    """Whether the pixels of `g` that touch join along an edge, not only at a
    corner: a beak cell beside its bar, not off its end."""
    on, _, (pieces, _, _) = cells(g, grid)
    return len(_regions(np.pad(on, 1), True, ((0, 1), (1, 0), (0, -1), (-1, 0)))) == pieces


def _cut(font, smooth, grid, em):
    """〒 from the T of `font`: its bar again above it, as far apart as in
    Noto Serif JP's (a little less than a fifth of its height), the stem cut
    as much shorter, along the slant, centred in `em`."""
    g = grid or 1
    t = path(font, "T")
    x0, y0, x1, y1 = t.bounds
    # The bar, where the T has nothing else: a quarter of the way along it
    bar = max(runs(t, x=x0 + (x1 - x0) / 4), key=lambda run: run[1])
    thick = bar[1] - bar[0]
    drop = thick + pixel.snap((y1 - y0) * GAP, g)
    cut = pixel.snap(y0 + (y1 - y0) * 0.4, g)  # in the stem, between beaks and foot
    shift = pixel.snap(-drop * slope(smooth), g)

    def clip(bottom, top):
        return pathops.op(t, rect(x0 - 1, bottom, x1 + 1, top), pathops.PathOp.INTERSECTION)

    # Both bars straight, as long as T's, as thick: cut out of T, the top's
    # ends would bring a little of the beaks along, and on 100, where MCKL
    # carves T's bar row by the stem, the lower one would come in pieces
    a, b = runs(t, y=y1 - thick / 2)[0][0], runs(t, y=y1 - thick / 2)[-1][1]
    p = union_paths(
        [
            rect(a, y1 - thick, b, y1),
            clip(cut, y1).transform(1, 0, 0, 1, shift, -drop),
            clip(y0 - 1, cut - drop),
            rect(a + shift, y1 - thick - drop, b + shift, y1 - drop),
        ]
    )
    left, _, right, _ = p.bounds
    return glyph(p.transform(1, 0, 0, 1, pixel.snap((em - right - left) / 2, g), 0))
