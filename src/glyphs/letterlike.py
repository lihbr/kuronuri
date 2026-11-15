"""Letters Redaction lacks, for maths and units, drawn by hand from its own
(shapes.drawn): Σ Π, the Greek capitals, are ∑ ∏ of maths.py as tall as
capitals; μ (and µ, the micro sign) is u, its left stem carried down to p's
descender and cut there, plain, its right one cut at the baseline, as wide
as it runs, under the carved join of its bowl: Greek lowercase has no feet
(greek.py); Italic's ends as its u does, in the stroke it leaves by, which
is no foot. ℏ is Italic's ħ, in every style, Bold's emboldened as ∫ is.
Each is set between the side bearings of the letter it is drawn from, MCKL's
pixel letter's on a grid, as far from them as its outline says (SIDES):
Italic's μ is u where u is, its descender under the letter before it, as
p's is; Regular's and Bold's μ is as wide as u, its right side bearing the
wider by the reach of the foot it lost (83 units, Bold's 84). There, they
are pixelated where in a cell they fall best, their strokes as thick as
those of that letter.

℧ ℵ ℊ ℓ ℮ have no letter of Redaction to be drawn from: they stay Noto
Serif JP's (the Greek letters, Ω too, are greek.py's). Units (squared.py)
set ℓ and Ω
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
SIDES = "com.lihbr.kuronuri.sides"  # in an outline's lib: its side bearings
# On a grid, units off those side bearings: {(code point, style, grid): (left,
# right)}. μ's right foot came off in its outline, its side bearing the wider
# by its reach, but its cells lost less than that (a cell of the foot on
# Regular's and Bold's 50), none (Regular's 100, pixelated without it), or
# stand a column to the left (Bold's 20, its left stem where u's and η's
# are), and a side bearing rounds to a cell more or less than they lost: μ
# is as wide as it was with its foot, its right stem on the same columns
REFITTED = {(0x03BC, "Regular", 50): (0, -50), (0x03BC, "Regular", 100): (0, -100)}
REFITTED |= {(0x03BC, "Bold", 20): (0, 20), (0x03BC, "Bold", 50): (0, -50)}
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
        # Between the side bearings of its letter, MCKL's own on a grid, each
        # as far from that letter's as its outline says (μ), and REFITTED
        of = italic if of_italic else smooth
        spacing = (redaction(grid, "Italic") if of_italic else font) if grid else of
        og = of["glyf"][of.getBestCmap()[ord(letter)]]
        og.recalcBounds(of["glyf"])
        sg = spacing["glyf"][spacing.getBestCmap()[ord(letter)]]
        sg.recalcBounds(spacing["glyf"])
        sides, more = hand[chr(cp)][1][SIDES], REFITTED.get((cp, style, grid), (0, 0))
        theirs, own = (
            f["hmtx"][f.getBestCmap()[ord(letter)]][0] - x.xMax
            for f, x in ((spacing, sg), (of, og))
        )
        lsb = pixel.snap(sg.xMin + sides[0] - og.xMin, g) + more[0]
        rsb = pixel.snap(theirs + sides[1] - own, g) + more[1]
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
