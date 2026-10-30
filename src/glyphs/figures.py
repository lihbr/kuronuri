"""Figures drawn from Redaction's own: superscript and subscript digits,
numerators and denominators, and vulgar fractions: ⁰ ⁴ ⁹, ₀ ₂, ⅓ ⅔ ⅛ ⅒
↉ ⅟ ℀ ℅, and the features for them.

Redaction has ¹ ² ³, and ¼ ½ ¾ ⅗ made of them, its fraction slash, and the
same digits on the baseline: 2, and 4 and 5, which are raised for ⁴ ⁵. The
others (0, 6 to 9) are drawn to match: Redaction's digits made heavier as
its Bold is of its Regular (shapes.blend), so their stems match those of ¹
shrunk to its height, on its baseline, hairlines and carving as MCKL's
own. Fractions are made of them (components), as
Redaction's are: the numerator as far left of the slash, and the denominator
as far right of it, as in ½, each at its own height along the slash.

Subscripts are superscripts (components) below the baseline, a third of
their height down, and denominators on it, as in ½. Superscript letters, for
℀ ℅ and the ordinals (ordinals.py), are Redaction's shrunk as the digits,
their x-height at the top of ¹: in Regular, Bold's thinned; in Italic and
Bold, made heavier as Bold is of Regular where their outlines match, else
grown across only, their carving cut again.

Redaction's `frac` turns 1/2 into ½ (font-variant-numeric:
diagonal-fractions): it does every fraction there is a glyph for, and `sups`
and `numr` give the digits Redaction lacks. `subs` and `sinf` turn digits
into subscripts (font-variant-position: sub), and `dnom` into
denominators.
"""

import functools

from fontTools.otlLib import builder as otl
from fontTools.ttLib.tables import otTables as ot

import layout
import pixel

from .shapes import (
    add,
    blend,
    composite,
    embolden,
    glyph,
    masters,
    path,
    phased,
    pixelate_glyphs,
    runs,
    shrunk,
    sideways,
    slope,
    stem,
    union,
)

# Glyphs of superscript digits, Redaction's first, as numerators too
SUPERIORS = {
    "0": "uni2070",
    "1": "onesuperior",
    "2": "twosuperior",
    "3": "threesuperior",
    **{str(d): f"uni{0x2070 + d:04X}" for d in range(4, 10)},
}
DRAWN = {d: name for d, name in SUPERIORS.items() if name.startswith("uni")}
# code point: (numerator, denominator); Redaction has ¼ ½ ¾ ⅗
FRACTIONS = {
    0x2150: ("1", "7"),
    0x2151: ("1", "9"),
    0x2152: ("1", "10"),
    0x2153: ("1", "3"),
    0x2154: ("2", "3"),
    0x2155: ("1", "5"),
    0x2156: ("2", "5"),
    0x2158: ("4", "5"),
    0x2159: ("1", "6"),
    0x215A: ("5", "6"),
    0x215B: ("1", "8"),
    0x215C: ("3", "8"),
    0x215D: ("5", "8"),
    0x215E: ("7", "8"),
    0x215F: ("1", ""),
    0x2189: ("0", "3"),
    0x2100: ("a", "c"),  # account of
    0x2105: ("c", "o"),  # care of
}
REDACTION = {0xBC: ("1", "4"), 0xBD: ("1", "2"), 0xBE: ("3", "4"), 0x2157: ("3", "5")}
INFERIORS = {str(d): f"uni{0x2080 + d:04X}" for d in range(10)}
DROP = 1 / 3  # of the height of subscripts, below the baseline
# Digits Redaction has small, as denominators: in which fraction
OWN = {"4": "¼", "5": "⅗"}
DENOMINATORS = {d: f"{name}.dnom" for d, name in SUPERIORS.items()}
# Superscript letters of ℀ and ℅, those of ordinals.py, drawn first
LETTERS = {"a": "ordfeminine", "c": "c.superior", "o": "ordmasculine"}
CODEPOINTS = (
    {0x2070 + int(d): name for d, name in DRAWN.items()}
    | {0x2080 + int(d): name for d, name in INFERIORS.items()}
    | {cp: f"uni{cp:04X}" for cp in FRACTIONS}
)
PHASED = (35, 50, 70)  # grids figures are placed on so: finer, they keep the drawing's
CARVED = (10, 20)  # grids letters are placed on where their carving comes out
ALTERNATES = []
SAMPLES = [
    "x⁰ x¹ x² x³ x⁴ x⁵ x⁶ x⁷ x⁸ x⁹",
    "H₂O CO₂ x₀ x₁ x₉ C₆H₁₂O₆",
    "¼ ½ ¾ ⅐ ⅑ ⅒ ⅓ ⅔ ⅕ ⅖ ⅗ ⅘ ⅙ ⅚ ⅛ ⅜ ⅝ ⅞ ⅟ ↉",
    "1/2 cup, 3/4 inch, 1/10 mile, 2/3 (frac)",
]


def _letters(smooth):
    """What superscript letters are shrunk from, by how much they are made
    heavier (shapes.shrunk), how much they are shrunk, and how tall and
    where they stand: their x-height at the top of ¹, as tall as
    emboldened, their baseline below."""
    one, sup = path(smooth, "1"), path(smooth, "¹")
    scale = (sup.bounds[3] - sup.bounds[1]) / (one.bounds[3] - one.bounds[1])
    source, amount = shrunk(smooth, scale, target=stem(sup))
    height = (source["OS/2"].sxHeight + 2 * amount) * scale
    return source, amount, scale, height, sup.bounds[3] - height


@functools.cache
def _ink(char):
    """How much ink Redaction's Bold adds to its Regular's `char`, over how
    much growing it across by a unit adds (shapes.sideways)."""
    regular, bold = masters()
    a, b = path(regular, char), path(bold, char)
    return (abs(b.area) - abs(a.area)) / (abs(sideways(a, 1, pointed=False).area) - abs(a.area))


def _heavier(source, char, amount, scale, height):
    """`char` of `source` made heavier, its stems as those of n emboldened
    by `amount` shrunk by `scale`, its x-height `height`: as Bold is of
    Regular (shapes.blend) where their outlines match it and it grows
    clean, its own carving MCKL's; else grown across only (shapes.sideways),
    its carving cut again, as much as n, or, where it matches but would run
    into itself (Bold's s), adding as much ink as blending would (_ink).
    Either, its x-height grows less than emboldened: it is shrunk less, and
    made that less heavier."""
    regular, bold = masters()
    x, s = source["OS/2"].sxHeight, stem(path(source, "n"))
    dx = bold["OS/2"].sxHeight - regular["OS/2"].sxHeight
    ds = stem(path(bold, "n")) - stem(path(regular, "n"))
    h, target = height / scale, s + 2 * amount  # what n emboldened would be
    # (s + t ds) / (x + t dx) = target / h
    t = (target * x - s * h) / (ds * h - dx * target)
    ink = 1
    try:
        p = blend(source, regular, bold, char, t)
    except ValueError:
        p, ink = None, _ink(char) / _ink("n")
    if p is not None:
        k = height / (x + t * dx)
        return p.transform(k, 0, 0, k, 0, 0)
    k = height / x
    p = sideways(path(source, char), (target * scale / k - s) / 2 * ink, carve=True, thick=s)
    return p.transform(k, 0, 0, k, 0, 0)


def _superior(smooth, char, own=True):
    """`char` of `smooth` as a superscript, on the baseline of ¹: 4 and 5 are
    those of Redaction's ¼ and ⅗, raised (unless not `own`, for score.py to
    draw them as the others); other digits are its own, made heavier as
    Bold is of Regular (shapes.blend: Bold's past Bold) till the stem of its
    1 shrunk as tall as ¹ is that of ¹, set as that 1 would be on ¹; it
    raises if Regular's, Bold's and its own do not match. Letters are
    shrunk as much, their x-height at its top, their stems as those of ¹
    (shapes.shrunk): an upright Regular's are Bold's thinned, which keeps
    their carving; others are made heavier (_heavier), keeping theirs."""
    one, sup = path(smooth, "1"), path(smooth, "¹")
    scale = (sup.bounds[3] - sup.bounds[1]) / (one.bounds[3] - one.bounds[1])
    if char.isalpha():
        source, amount, scale, height, base = _letters(smooth)
        if amount < 0:  # Bold thinned, which keeps its carving
            p = embolden(path(source, char), amount)
            return glyph(p.transform(scale, 0, 0, scale, 0, base + amount * scale))
        p = _heavier(source, char, amount, scale, height)
        return glyph(p.transform(1, 0, 0, 1, 0, base))
    up = sup.bounds[1] - one.bounds[1] * scale
    if own and char in OWN:  # the denominator of a fraction of Redaction's: not slash nor ¹ ³
        pieces = sorted(path(smooth, OWN[char]).contours, key=lambda c: c.bounds[3] - c.bounds[1])
        pieces.pop()  # the slash, the tallest
        denominator = union([])
        for c in pieces:
            if c.bounds[1] < sup.bounds[1] / 2:
                denominator.addPath(c)
        return glyph(denominator.transform(1, 0, 0, 1, 0, up))
    regular, bold = masters()
    t = (stem(sup) / scale - stem(one)) / (stem(path(bold, "1")) - stem(path(regular, "1")))
    heavier = blend(smooth, regular, bold, "1", t), blend(smooth, regular, bold, char, t)
    if not all(heavier):  # drawn another way, it would stand out of the set
        raise ValueError(f"{char} of Redaction's Regular, Bold and this style do not match")
    one, p = heavier
    scale = (sup.bounds[3] - sup.bounds[1]) / (one.bounds[3] - one.bounds[1])
    # On the grid as ¹ is, pixelated: the side bearings come after
    dx, dy = sup.bounds[0] - one.bounds[0] * scale, sup.bounds[1] - one.bounds[1] * scale
    return glyph(p.transform(scale, 0, 0, scale, dx, dy))


def pixelated(font, glyphs, grid, rows=None):
    """Drawn figures {name: glyph} pixelated on the grid of `font`, on 35 to
    70 (PHASED) each where in a cell it falls best (shapes.phased): its
    hairlines are about half a cell, which a cell fills or not as they
    fall. On the rows of ¹, strokes as thick as MCKL's ² ³ on the grid.
    Letters, on their own `rows`, so too, and on 10 and 20 (CARVED) where
    their carving comes out first, and none as another."""
    letters = rows is not None
    if grid not in PHASED and not (letters and grid in CARVED):
        return pixelate_glyphs(glyphs, grid)
    glyf = font["glyf"]
    for name in ("onesuperior", "twosuperior", "threesuperior"):
        glyf[name].recalcBounds(glyf)
    rows = rows or (glyf["onesuperior"].yMin, glyf["onesuperior"].yMax)
    like = [glyf["twosuperior"], glyf["threesuperior"]]
    return phased(glyphs, grid, rows, like, letters and grid in CARVED, distinct=letters)


def _bearings(font, char):
    """The left and right side bearings of `char` in `font`, and its height."""
    name = font.getBestCmap()[ord(char)]
    g = font["glyf"][name]
    g.recalcBounds(font["glyf"])
    return g.xMin, font["hmtx"][name][0] - g.xMax, g.yMax - g.yMin


@functools.cache
def _spacing(smooth):
    """How much farther from their neighbours MCKL sets ¹ ² ³ than 1 2 3
    shrunk as tall: on both sides alike, and to the right of the left
    (in italic, along the slant, as they are raised)."""
    track = shift = 0
    for d, s in zip("123", "¹²³"):
        (l0, r0, h0), (l1, r1, h1) = _bearings(smooth, d), _bearings(smooth, s)
        dl, dr = l1 - l0 * h1 / h0, r1 - r0 * h1 / h0
        track, shift = track + (dl + dr) / 6, shift + (dl - dr) / 6
    return track, shift


def superiors(font, smooth, grid, chars):
    """{glyph name: (glyph, advance)} of `chars` ({character: glyph name})
    as superscripts: digits with the side bearings of ¹, italic ones
    overhanging on the right; letters with their own, shrunk as they are,
    set as MCKL sets ¹ ² ³ against 1 2 3 (_spacing)."""
    g = grid or 1
    glyf, hmtx = font["glyf"], font["hmtx"]
    glyf["onesuperior"].recalcBounds(glyf)
    left = hmtx["onesuperior"][1]
    right = hmtx["onesuperior"][0] - glyf["onesuperior"].xMax
    track, shift = _spacing(smooth)
    size = _letters(smooth)[3] / smooth["OS/2"].sxHeight

    def bearings(c):
        if c.isdigit():
            return left, right
        lsb, rsb, _ = _bearings(smooth, c)
        return lsb * size + track + shift, rsb * size + track - shift

    drawn = {name: _superior(smooth, c) for c, name in chars.items()}
    if grid:  # in the order of `chars`, for the same glyph order every build
        digits = {n: drawn[n] for c, n in chars.items() if c.isdigit()}
        letters = {n: drawn[n] for c, n in chars.items() if not c.isdigit()}
        done = pixelated(font, digits, grid) if digits else {}
        if letters:  # on their baseline and x-height
            *_, height, base = _letters(smooth)
            rows = pixel.snap(base, grid), pixel.snap(base + height, grid)
            done |= pixelated(font, letters, grid, rows)
        drawn = {n: done[n] for n in drawn}
    out = {}
    for c, name in chars.items():
        gl, (lsb, rsb) = drawn[name], bearings(c)
        gl.coordinates.translate((pixel.snap(lsb, g) - gl.coordinates.calcIntBounds()[0], 0))
        gl.recalcBounds(None)
        out[name] = gl, pixel.snap(gl.xMax + rsb, g)
    return out


def add_glyphs(font, smooth, grid=None):
    g = grid or 1
    glyf, hmtx, cmap = font["glyf"], font["hmtx"], font.getBestCmap()
    add(
        font,
        superiors(font, smooth, grid, DRAWN),
        {0x2070 + int(d): name for d, name in DRAWN.items()},
    )
    left = hmtx["onesuperior"][1]
    right = hmtx["onesuperior"][0] - glyf["onesuperior"].xMax

    # Subscripts: superscripts, their top as far below the baseline as DROP of
    # them, back along the slant in italic, but not past their side bearing
    sup = path(font, "¹")
    height = sup.bounds[3] - sup.bounds[1]
    down = pixel.snap(-height * DROP - sup.bounds[1], g)
    inferiors = {}
    for d, name in INFERIORS.items():
        superior = glyf[SUPERIORS[d]]
        superior.recalcBounds(glyf)
        back = pixel.snap(max(down * slope(smooth), -superior.xMin), g)
        advance = max(hmtx[SUPERIORS[d]][0], pixel.snap(superior.xMax + back + right, g))
        inferiors[name] = (composite(font, [(SUPERIORS[d], back, down)], grid), advance)
    add(font, inferiors, {0x2080 + int(d): name for d, name in INFERIORS.items()})

    # Where Redaction's ½ sets its numerator and denominator, along its slash:
    # measured smooth, the pieces of a pixel ½ can be one
    half, one = path(smooth, "½"), path(smooth, "¹")
    pieces = sorted(half.contours, key=lambda c: c.bounds[3] - c.bounds[1])
    slash = pieces.pop()  # the tallest
    numerator = max(pieces, key=lambda c: c.bounds[1])
    denominator = min(pieces, key=lambda c: c.bounds[1])
    den_shift = denominator.bounds[1] - numerator.bounds[1]  # down to the baseline

    def along(y):
        """The left and right edges of the slash at height `y`."""
        edges = runs(slash, y=y)
        return edges[0][0], edges[-1][1]

    num_mid = (one.bounds[1] + one.bounds[3]) / 2
    den_mid = num_mid + den_shift
    num_gap = along(num_mid)[0] - numerator.bounds[2]
    den_gap = denominator.bounds[0] - along(den_mid)[1]
    right = smooth["hmtx"][smooth.getBestCmap()[0xBD]][0] - denominator.bounds[2]
    # Letters on the baseline too: they stand higher than digits
    source, amount, scale, _, base = _letters(smooth)
    letter_drop = -pixel.snap(base + min(amount, 0) * scale, g)

    def digits(text):
        """Superscript digits of `text` side by side: [(name, x)] from 0, and
        the width of their ink."""
        x, out = 0, []
        for d in text:
            name = (SUPERIORS | LETTERS)[d]
            glyf[name].recalcBounds(glyf)
            out.append((name, x - glyf[name].xMin))
            x += glyf[name].xMax - glyf[name].xMin + left + right
        return out, x - left - right

    # Denominators: superscripts on the baseline, as in ½
    add(
        font,
        {
            name: (composite(font, [(SUPERIORS[d], 0, den_shift)], grid), hmtx[SUPERIORS[d]][0])
            for d, name in DENOMINATORS.items()
        },
        {},
    )

    glyphs = {}
    for cp, (num, den) in FRACTIONS.items():
        n, n_width = digits(num)
        d, d_width = digits(den)
        nx = along(num_mid)[0] - num_gap - n_width  # left of the numerator
        dx = along(den_mid)[1] + den_gap  # left of the denominator
        shift = left - nx  # the numerator on the side bearing
        parts = [(name, x + nx + shift, 0) for name, x in n]
        parts.append((cmap[ord("⁄")], shift, 0))
        parts += [
            (name, x + dx + shift, letter_drop if name in LETTERS.values() else den_shift)
            for name, x in d
        ]
        end = dx + d_width + right if den else hmtx[cmap[ord("⁄")]][0]
        glyphs[CODEPOINTS[cp]] = (composite(font, parts, grid), pixel.snap(end + shift, g))
    add(font, glyphs, CODEPOINTS)

    # sups and numr give the digits Redaction lacks, and frac its fractions
    gsub = font["GSUB"].table
    lookups = {
        tag: {
            i
            for r in gsub.FeatureList.FeatureRecord
            if r.FeatureTag == tag
            for i in r.Feature.LookupListIndex
        }
        for tag in ("sups", "numr", "frac")
    }
    for i in lookups["sups"] | lookups["numr"]:
        for st in gsub.LookupList.Lookup[i].SubTable:
            st.mapping.update({cmap[ord(d)]: name for d, name in DRAWN.items()})
    for i in lookups["frac"]:
        for st in gsub.LookupList.Lookup[i].SubTable:
            for cp, (num, den) in FRACTIONS.items():
                if not den:
                    continue
                first, *rest = (cmap[ord(c)] for c in f"{num}/{den}")
                ligature = ot.Ligature()
                ligature.LigGlyph, ligature.Component = CODEPOINTS[cp], rest
                st.ligatures.setdefault(first, []).append(ligature)
            for ligatures in st.ligatures.values():  # longer first: 1/10 before 1/1
                ligatures.sort(key=lambda lig: len(lig.Component), reverse=True)
    # subs, sinf and dnom, which Redaction does not have
    for tag, forms in (("subs", INFERIORS), ("sinf", INFERIORS), ("dnom", DENOMINATORS)):
        mapping = {cmap[ord(d)]: name for d, name in forms.items()}
        layout.add_feature(gsub, tag, otl.buildLookup([otl.buildSingleSubstSubtable(mapping)]))
