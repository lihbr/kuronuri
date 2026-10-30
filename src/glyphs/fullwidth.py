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

〒 is T with a bar as long and thick as its own above it, the stem
shortened to stand on the baseline still: Redaction's own pieces, so in the
numbered variants it keeps MCKL's pixels.
"""

import pathops
from fontTools.otlLib import builder as otl
from fontTools.pens.ttGlyphPen import TTGlyphPen

import layout
import pixel

from .shapes import add, composite, glyph, path, rect, runs, slope, union_paths

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
GAP = 0.18  # between the bars of 〒, over its height
CODEPOINTS = {cp: f"uni{cp:04X}" for cp in [*SOURCES, *HALFWIDTH, *PUNCTUATION, POSTAL]}
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
    """Add the vertical forms to `vert` and `vrt2`, of the merged font."""
    table = font["GSUB"].table
    for tag in ("vert", "vrt2"):
        layout.extend_feature(table, tag, otl.buildLookup([otl.buildSingleSubstSubtable(VERTICAL)]))


def _postal(font, smooth, grid, em):
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

    # The bar again: straight, as long as T's, as thick (cut out of T, its
    # ends would bring a little of the beaks along)
    a, b = runs(t, y=y1 - thick / 2)[0][0], runs(t, y=y1 - thick / 2)[-1][1]
    p = union_paths(
        [
            rect(a, y1 - thick, b, y1),
            clip(cut, y1).transform(1, 0, 0, 1, shift, -drop),
            clip(y0 - 1, cut - drop),
        ]
    )
    left, _, right, _ = p.bounds
    return glyph(p.transform(1, 0, 0, 1, pixel.snap((em - right - left) / 2, g), 0))
