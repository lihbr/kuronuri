"""Split fonts into unicode-range slices for the web.

Google Fonts serves Japanese families (IBM Plex Sans JP, Noto Serif JP...) as
about 120 WOFF2 slices, each listed in the CSS with a `unicode-range`, so a
browser only downloads the slices a page uses. The slices group characters
by frequency: slice 119 holds kana, punctuation and the most common kanji,
slice 0 the rarest. We reuse Google's slices (data/google-jp-slices.json,
taken from the CSS of IBM Plex Sans JP).

As in Google's, each slice keeps the variation sequences of its characters
(葛 and U+E0100), with the variants they ask for, and its `unicode-range`
lists the characters alone: browsers pick the slice by the character, and
set the selector after it with the same font.
"""

import json
from pathlib import Path

from fontTools import subset
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.unicodedata import mirrored

from family import SELECTORS
from glyphs.arrows import ARROWS

SLICES = json.loads(
    (Path(__file__).resolve().parent / "data" / "google-jp-slices.json").read_text()
)["slices"]
# Features left out of the slices: they pull hundreds of rarely used glyphs
# into them (dlig turns katakana words into squared ligatures like ㌔). The
# desktop fonts keep them.
DROP_FEATURES = {"aalt", "nlck", "hist", "dlig"}


def plan(cmap):
    """Give each character of the font to exactly one slice, as a list of
    (slice name, sorted code points) in Google's order.

    Some characters are in two of Google's slices; Latin slices win, then
    Japanese slices from most to least frequent. Characters in none of
    them (Roman numerals) go to an extra "misc" slice. Kuronuri's arrows
    are part of its Latin design: they go in the latin slice. Mirrored
    pairs like ＜＞ stay together: right-to-left text swaps one for the
    other within the same font (and the subsetter adds the mirror anyway)."""
    owner = {}
    for sl in reversed(SLICES):  # latin, latin-ext, cyrillic, 119 ... 0
        for a, b in sl["ranges"]:
            for c in range(a, b + 1):
                if c in cmap:
                    owner.setdefault(c, sl["name"])
    for c in ARROWS:
        if c in cmap:
            owner[c] = "latin"
    for c in sorted(cmap):
        m = mirrored(c)
        if m is not None and m > c and m in cmap:
            owner[m] = owner.get(c, "misc")
    groups = {}
    for c in sorted(cmap):
        groups.setdefault(owner.get(c, "misc"), []).append(c)
    order = [sl["name"] for sl in SLICES] + ["misc"]
    return [(name, groups[name]) for name in order if name in groups]


def unicode_range(cps):
    """CSS unicode-range for sorted code points: U+20-7e, U+a0, ..."""
    parts, start = [], cps[0]
    for prev, c in zip(cps, cps[1:] + [None]):
        if c == prev + 1:
            continue
        parts.append(f"U+{start:x}" if start == prev else f"U+{start:x}-{prev:x}")
        start = c
    return ", ".join(parts)


def write_slice(task):
    ttf, out, cps = task
    font = TTFont(ttf)
    tags = {
        r.FeatureTag
        for t in ("GSUB", "GPOS")
        if t in font
        for r in font[t].table.FeatureList.FeatureRecord
    }
    opts = subset.Options()
    opts.layout_features = sorted(tags - DROP_FEATURES)
    opts.name_IDs = ["*"]
    opts.name_languages = ["*"]
    s = subset.Subsetter(opts)
    s.populate(unicodes=set(cps) | SELECTORS)
    s.subset(font)
    font.flavor = "woff2"
    font.save(out)


def font_face(family, style, weight, url, cps):
    # ?no-inline: Vite would inline slices under 4 KB into the CSS, so they
    # would load with it, used or not
    return (
        f"@font-face {{\n"
        f'  font-family: "{family}";\n'
        f"  font-style: {style};\n"
        f"  font-weight: {weight};\n"
        f"  font-display: swap;\n"
        f'  src: url("{url}?no-inline") format("woff2");\n'
        f"  unicode-range: {unicode_range(cps)};\n"
        f"}}\n"
    )


def outline(ttf, text):
    """`text` set in a font, as an SVG of one path in font units, in the
    colour of the text around it: as wide as its advances and as tall as
    the font's line before line-height (hhea ascent to descent), its
    baseline at the ascent. For the site's title to paint without the
    font."""
    font = TTFont(ttf)
    glyphs, cmap, hmtx = font.getGlyphSet(), font.getBestCmap(), font["hmtx"]
    hhea = font["hhea"]
    pen = SVGPathPen(glyphs, ntos=lambda n: f"{round(n, 1):g}")
    x = 0
    for c in text:
        name = cmap[ord(c)]
        glyphs[name].draw(TransformPen(pen, (1, 0, 0, -1, x, hhea.ascent)))
        x += hmtx[name][0]
    height = hhea.ascent - hhea.descent
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {x} {height}">'
        f'<path fill="currentColor" d="{pen.getCommands()}"/></svg>\n'
    )
