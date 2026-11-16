"""The soft, Unicode and non-breaking hyphens, U+00AD, U+2010 and U+2011,
and the figure dash, U+2012: Redaction's hyphen.

Redaction has none of them, so Noto Serif JP's came in with the merge:
U+2010 its fullwidth Japanese hyphen, U+00AD and U+2011 its own hyphen,
narrower and lower than Redaction's. Browsers set the hyphen of a broken
word (`&shy;`, `hyphens: auto`) with U+2010 when the font has it, so
"dis-comfort" broke as "dis  -". U+00AD and U+2011 are the hyphen; U+2010
is a glyph made of it, kerned as it is, so that `fwid` turns it, and not
U+002D (which turns into －), into the hyphen centred in the em.

The figure dash is the hyphen, as thick and as high, its right end moved
out to the advance of the tabular figures, so it lines up with them.
"""

import copy

from fontTools.otlLib import builder as otl

import layout
import pixel

from .greek import _kern
from .shapes import add, composite

CODEPOINTS = {0xAD: "hyphen", 0x2010: "uni2010", 0x2011: "hyphen", 0x2012: "uni2012"}
FULLWIDTH = {"uni2010": "uni2010.fwid"}
ALTERNATES = list(FULLWIDTH.values())
SAMPLES = [
    "dis­comfort dis‐comfort dis‑comfort dis-comfort",
    "e‑mail 2026‐11‐16 T‐V T-V",
    "0123 ‒ 4567 ‒ 89 (tnum)",
    "- ‐ ‑ ‒ – —",
]
FEATURES = ["tnum"]


def add_glyphs(font, smooth, grid=None):
    glyf, hmtx = font["glyf"], font["hmtx"]
    advance = hmtx["hyphen"][0]
    # added first, U+2010 is the last glyph of the font, as _kern needs
    add(font, {"uni2010": (composite(font, [("hyphen", 0, 0)], grid), advance)}, {})
    _kern(font, {"uni2010": ("hyphen", "hyphen")})
    em = pixel.snap_advance(1000, grid or 1)
    dx = em / 2 - (glyf["hyphen"].xMin + glyf["hyphen"].xMax) / 2
    add(font, {"uni2010.fwid": (composite(font, [("hyphen", dx, 0)], grid), em)}, {})
    # Italic 10 and 20 draw the hyphen's ends as steps: moving its right
    # half keeps them
    width = pixel.snap(max(hmtx[d][0] for d in layout.DIGITS), grid or 10)
    dash = copy.deepcopy(glyf["hyphen"])
    middle = (dash.xMin + dash.xMax) / 2
    for i, (x, y) in enumerate(dash.coordinates):
        if x > middle:
            dash.coordinates[i] = (x + width - advance, y)
    add(font, {"uni2012": (dash, width)}, CODEPOINTS)


def add_features(font):
    lookup = otl.buildLookup([otl.buildSingleSubstSubtable(FULLWIDTH)])
    layout.extend_feature(font["GSUB"].table, "fwid", lookup)
