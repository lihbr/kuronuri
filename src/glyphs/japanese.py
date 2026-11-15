"""Japanese signs of figures and kanji: ㋀ (January) to ㋋, ㏠ (the 1st) to
㏾, and ㍘ (0 o'clock) to ㍰.

Their figures are Redaction's, as typed, and their kanji (月 日 点) Noto
Serif JP's, at the weight of the kanji Kuronuri sets with the style on the
grid (family.noto_weight): lighter on the coarse grids. As in Noto Serif
JP, both are as tall as its signs are, side by side in the em, condensed
when they would not fit, their vertical stems a little thinner than before
(the figures' than those of n), as much as Noto Serif JP's: emboldened
mostly sideways, in a space stretched upright, so horizontal strokes stay
thin. Japanese stays
upright in italic; the figures are italic. Pixelated on a grid.
"""

import pathops

import pixel
from family import noto_glyphs, noto_weight

from .shapes import add, content, embolden, glyph, path, pixelate_glyphs, runs, shaper, stem

# code point: (figures, kanji)
SIGNS = (
    {0x32C0 + i: (str(i + 1), "月") for i in range(12)}
    | {0x33E0 + i: (str(i + 1), "日") for i in range(31)}
    | {0x3358 + i: (str(i), "点") for i in range(25)}
)
CODEPOINTS = {cp: f"uni{cp:04X}" for cp in SIGNS}
ALTERNATES = []
SAMPLES = ["㋀㋁㋂㋉㋊㋋", "㏠㏡㏩㏾", "㍘㍙㍢㍰", "期限は㋃㏮まで"]
BOX = (40, -44, 960, 795)  # where Noto Serif JP's signs stand in the em, over 1000
GAP = 20  # between the figures and the kanji, over 1000
THINNER = 0.3  # condensed by s, vertical stems are s ** THINNER as thick, as in Noto Serif JP


def _verticals(p):
    """The mean width of the vertical strokes of `p` a third of the way up:
    halfway, 日 has a bar across."""
    spans = runs(p, y=p.bounds[1] + (p.bounds[3] - p.bounds[1]) / 3)
    return sum(b - a for a, b in spans) / len(spans)


def _condensed(p, squeeze, thick, own):
    """`p` condensed sideways by `squeeze`, its vertical strokes, `own`
    thick, made `thick`: emboldened stretched upright as much as condensed,
    then put back, horizontal strokes thicken `squeeze` times as much."""
    p = p.transform(squeeze, 0, 0, 1 / squeeze, 0, 0)
    p = embolden(p, (thick - own * squeeze) / 2)
    return p.transform(1, 0, 0, squeeze, 0, 0)


def add_glyphs(font, smooth, grid=None):
    em = pixel.snap_advance(1000, grid or 1)
    x0, y0, x1, y1 = (v * em / 1000 for v in BOX)
    weight = noto_weight(700 if smooth["OS/2"].usWeightClass >= 700 else 400, grid)
    noto = noto_glyphs(weight, "".join(sorted({k for _, k in SIGNS.values()})))
    target = stem(path(smooth, "n"))
    s = shaper(smooth)
    glyphs = {}
    for cp, (figures, kanji) in SIGNS.items():
        digits, sign = content(smooth, s, figures), path(noto, kanji)
        # As tall as the box, side by side, condensed to fit in it
        dy = (y1 - y0) / (digits.bounds[3] - digits.bounds[1])
        ky = (y1 - y0) / (sign.bounds[3] - sign.bounds[1])
        dw = (digits.bounds[2] - digits.bounds[0]) * dy
        kw = (sign.bounds[2] - sign.bounds[0]) * ky
        room = x1 - x0 - GAP * em / 1000
        squeeze = min(1, room / (dw + kw))
        own = _verticals(path(noto, "日"))
        for _ in range(3):  # emboldened, they widen: condensed again to fit
            thinner = squeeze**THINNER
            d = _condensed(digits, squeeze, target * thinner / dy, stem(path(smooth, "1")))
            k = _condensed(sign, squeeze, own * thinner, own)
            width = (d.bounds[2] - d.bounds[0]) * dy + (k.bounds[2] - k.bounds[0]) * ky
            if width <= room + 1:
                break
            squeeze *= room / width
        digits, sign = d, k
        d0, e0, _, _ = digits.bounds
        _, f0, k1, _ = sign.bounds
        digits = digits.transform(dy, 0, 0, dy, x0 - d0 * dy, y0 - e0 * dy)
        sign = sign.transform(ky, 0, 0, ky, x1 - k1 * ky, y0 - f0 * ky)
        glyphs[CODEPOINTS[cp]] = glyph(pathops.op(digits, sign, pathops.PathOp.UNION))
    if grid:
        glyphs = pixelate_glyphs(glyphs, grid)
    add(font, {name: (g, em) for name, g in glyphs.items()}, CODEPOINTS)
