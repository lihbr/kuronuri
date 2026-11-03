"""Letters Redaction lacks, for maths and units, drawn by hand from its own
(shapes.drawn): Σ Π, the Greek capitals, are ∑ ∏ of maths.py as tall as
capitals; μ (and µ, the micro sign) is u, its left stem carried down to p's
descender; ℏ is Italic's ħ, in every style, Bold's emboldened as ∫ is. Each
is set between the side bearings of the letter it is drawn from, MCKL's
pixel letter's on a grid. There, they are pixelated where in a cell they
fall best, their strokes as thick as those of that letter.

Ω ℧ ℵ ℊ ℓ ℮ have no letter of Redaction to be drawn from: they stay Noto
Serif JP's, as the rest of Greek does. Units (squared.py) set ℓ and Ω
among Redaction's letters: for them alone (add_noto), they are Noto Serif
JP's scaled as tall as Redaction's l and O.
"""

import pixel

from .shapes import add, drawn, glyph, path, phased, slope

# {code point: (glyph name, the letter it is drawn from, of Italic)}
LETTERS = {
    0x03A3: ("uni03A3", "Z", False),
    0x03A0: ("uni03A0", "H", False),
    0x03BC: ("uni03BC", "u", False),
    0x00B5: ("uni03BC", "u", False),
    0x210F: ("uni210F", "ħ", True),
}
CODEPOINTS = {cp: name for cp, (name, _, _) in LETTERS.items()}
# Noto Serif JP's, for units: {code point: Redaction's letter it is as tall as}
NOTO = {0x2113: "l", 0x03A9: "O"}
ALTERNATES = []
SAMPLES = [
    "ΣΠμℏ",
    "ZΣX HΠT uμp ħℏh",
    "5 µm, 3 μF, ℏω = E",
    "Σ ΣΠ Π ∑∏",
]


def add_glyphs(font, smooth, grid=None):
    """Add the letters to `font`: a Redaction style, or one of Redaction 10 to
    100 on `grid`, as drawn for the style of `smooth`, the same style
    without a grid."""
    from family import redaction

    style = smooth["name"].getDebugName(2)
    hand = drawn(style)
    italic = redaction(None, "Italic")
    cmap, glyf = font.getBestCmap(), font["glyf"]
    g = grid or 1
    out = {}
    for cp, (name, letter, of_italic) in LETTERS.items():
        if name in out:
            continue
        shape = glyph(hand[chr(cp)][0])
        if grid:
            source = glyf[cmap[ord(letter)]]
            source.recalcBounds(glyf)
            shape = phased({name: shape}, grid, None, [source], carved=True)[name]
        # Between the side bearings of its letter, MCKL's own on a grid
        if grid:
            spacing = redaction(grid, "Italic") if of_italic else font
        else:
            spacing = italic if of_italic else smooth
        sg = spacing["glyf"][spacing.getBestCmap()[ord(letter)]]
        sg.recalcBounds(spacing["glyf"])
        lsb = pixel.snap(sg.xMin, g)
        rsb = pixel.snap(spacing["hmtx"][spacing.getBestCmap()[ord(letter)]][0] - sg.xMax, g)
        shape.recalcBounds(None)
        shape.coordinates.translate((lsb - shape.xMin, 0))
        out[name] = shape, pixel.snap(shape.xMax - shape.xMin + lsb + rsb, g)
    add(font, out, CODEPOINTS)


def add_noto(font):
    """Add Noto Serif JP's ℓ and Ω (NOTO), at the weight Kuronuri pairs with
    the style of `font`, a smooth Redaction style, as tall as its l and O,
    slanted in Italic: for units alone."""
    from family import NOTO_WEIGHT, noto_glyphs

    weight = NOTO_WEIGHT[700 if font["OS/2"].usWeightClass >= 700 else 400]
    noto = noto_glyphs(weight, "".join(chr(cp) + letter for cp, letter in NOTO.items()))
    s = slope(font)
    out, codepoints = {}, {}
    for cp, letter in NOTO.items():
        theirs, ours = path(noto, letter).bounds, path(font, letter).bounds
        k = (ours[3] - ours[1]) / (theirs[3] - theirs[1])
        name = f"uni{cp:04X}"
        p = path(noto, chr(cp)).transform(k, 0, s * k, k, 0, 0)
        advance = round(noto["hmtx"][noto.getBestCmap()[cp]][0] * k)
        out[name], codepoints[cp] = (glyph(p), advance), name
    add(font, out, codepoints)
