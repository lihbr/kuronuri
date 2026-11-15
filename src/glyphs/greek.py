"""Greek letters, which Redaction lacks, and Japanese text sets as symbols
(α版, πr², Δt, 5Ω): each cut from Redaction's own letters, of the same style,
or drawn from their measures where none has its shape (α π τ φ ω), so its
stems, hairlines, serifs and carving are MCKL's. Noto Serif JP's Greek
stays out (build.py): its design does not match. Σ Π μ are
letterlike.py's.

Capitals that are Latin ones are Redaction's (SAME, components): Α Β Ε Ζ Η
Ι Κ Μ Ν Ο Ρ Τ Υ Χ, and ο is o. Λ is V turned upside down (TURNED), in every
font, so MCKL's pixels on a grid: A's strokes, with V's notch at its apex,
between A's side bearings.

The others are drawn by hand from Redaction's points (shapes.drawn), a
source note in each outline. Where a hairline meets a stem, Redaction cuts
a ledge into the stem, on the side of the counter (under E's arm, H's bar,
A's bar): the letters drawn get that ledge, as wide and as deep. Where a
hairline crosses a stem (Φ Ψ φ ψ), on alternate sides, as T has it under
its bar on the right only: one under the hairline on the right, one over
it on the left, so the stem is never cut from both sides at one height.
- Γ: F without its middle arm.
- Δ: ∆ (maths.py's glyph, outline and pixels, when it is the letter drawn
  from A and Z, else a copy of its outline here): one design. A's side
  bearings and a little more (APART): its base is solid from end to end,
  and between A's own it joins a neighbour's base or serif on a grid.
  There, a cell of air where its base ends, and no more: on 100, where a
  cell is a stroke, on its right only; Italic's, a cell more than MCKL's A
  on each side where two of its A meet, and A's own where they do not.
- Θ: O, with H's bar across it and H's ledges under it, in the bowl.
- Ξ: the three arms of E, each mirrored, without its stem.
- Φ: I, and the two halves of o on each side of its stem, joined across
  it, a slice of their middle out so the bowl clears I's serifs, its
  halves meeting again in a line; D's ledge, at the upper right corner of
  its counters and the lower left.
- Ψ: the thin arm of U, twice, shorter (not scaled), I through it, its
  serifs clear of theirs; H's ledge under the cup on the right, and in it
  on the left.
- Ω: O open at the foot, standing on E's middle arm, twice: its bar, and
  the half of its serif above it, as far out as it clears the bowl. The
  ohm sign (U+2126) is the same glyph.
- α: the script form, drawn: a bowl as o's left side, whose stroke goes on
  from its top down to the right, thick, to a's tail, and from its bottom
  up to the right, thin, to a ball as c's, joined to it by r's step: across
  from the stroke, then down to the ball's side. They cross as x's strokes do,
  straight through, x's notch cut into the thick one above and below. In
  Italic, one stroke that crosses itself: a's bowl, as full, its top
  stroke turning down, thick, close by the bowl, into a stem that leans
  back a little and ends in a's tail; its bottom stroke going up, thin,
  through that stem, and on, steeper, to a small ball at the x-height, as
  x's arm ends: the stroke goes over the ball's top, and its lower edge
  ends in x's step, down to the ball's side, the ball round under it. Two
  short strokes right of the bowl, x's notches where they cross. The ball
  stands over the side bearing, as x's does, by less: the tail under it
  is as far from the letter after it as x's.
- β: ß without its bar and ball, its waist and its lower bowl each closed
  into the stem by B's bar, B's ledge by each: two counters. Its stem
  carried down to p's descender, plain (Italic's ß descends already).
- η: n, its right stem carried down to p's descender; no feet, as Greek
  lowercase has none (the cursive convention of Greek text faces: κ λ μ φ
  χ ψ neither; the flag a stem starts with stays, and the curl t's stem
  ends in, on π and τ): its left stem cut at the baseline, its right one
  as ρ's and β's are cut.
- θ: the zero, with e's bar across it and H's ledges under it.
- ι: the right stem of u, its flag and spur; in Italic, ı without the
  stroke it enters by.
- κ: k, its stem cut for the top of ı, without its feet: its stem and its
  leg cut at the baseline (Italic's k has none, its leg ends in a curl).
- λ: v turned upside down, as Λ is V, its thick stroke carried up to the
  cap height, without its feet: its legs cut at the baseline; in Italic,
  x, without its upper right arm, its thick stroke
  carried up to the ascender, turning steeper above where its strokes
  cross: straight on, it leans back as far as Italic leans forward, its
  top under the letter before it. Below, it is x: its join, its terminals.
- ν: Italic's v, which is the Greek letter's shape, upright (Bold's made
  heavier, its notch cut again); Italic's own is its v without its serifs.
- π: drawn: a bar as thick as Π's, z's beak at its left end, over two legs
  of t's stem, nearer than n's stems by 15 in 100 of their spacing (under
  a flat bar, open below, a counter as wide as n's reads wider than n's
  under its arch), the left one cut at the baseline, the right one with
  t's curl; t's ledge under the bar, right of each leg.
- ρ: o, and p's stem under its left side, plain; in Italic, o's left side
  goes on down as p's stem, at p's slant, in one stroke: its edge leaves
  the bowl where the bowl leans as it does, and the counter runs along it
  as p's. Where the bowl comes back to the stem, d's notch, mirrored: as
  wide, as deep. Italic's stem, which goes on from the bowl's side, would
  stand nearer the letter before it than p's: its side bearing is p's
  stem's, less what keeps the bowl by its stem.
- σ: o, its top carried on to the right as a bar.
- τ: π's bar and beak over t's stem and curl, t's ledge under the bar.
- υ: the lower half of o under u's stem and flag, the upper right side of
  the zero as its right arm, each joined where both run the same way:
  narrower than u. Regular's o is wider than that: it takes Italic's,
  upright, as ν takes its v.
- φ: the loop form, drawn: o's left side as an arc open at the top, its
  end carried over and cut as ω's arms are, and o's right side as a bowl
  that arches over into p's stem, cut at its descender, plain; a ledge in
  the stem under the arch on the right, one over the foot of the bowl on
  the left.
- χ: the Greek construction, drawn: a stroke as thick as x's, straight
  from the x-height on the right to p's descender on the left, cut level
  at both ends, and one as thin as x's through it, from the upper left to
  the lower right, a's tail at its foot and the same turned half round at
  its head; x's notch in the crotch above the crossing and in the one
  below, cut along the thin stroke into the thick one. Not x set low,
  whose thick stroke runs the other way. Italic's is the same, leaning.
- ψ: υ, its halves apart under p's stem, which goes through it under l's
  top and is cut at its descender, plain, each counter as wide as the stem
  or so; a ledge in the stem in the left counter's corner, and one under
  the bowl on the right.
- ω: o twice, the left of one and the right of the other, as near as
  their counters meet in a point under half the x-height, each arm
  carried over the top and back to a cut that hangs: its bowls do not
  gape.

Each stands between the side bearings its outline says (lib), those of the
Latin letter of the same structure on that side, to the same part of the
shape; on a grid, as far from those of MCKL's pixel letter of that side
(SIDED) as drawn (fitted). No room is added for another script: a browser
sets Greek, Latin and Japanese in a run each and kerns no pair across two,
and there Greek is held to what Redaction's own letters do, which lean
over a kanji in Italic and touch their neighbours on a grid. But for a
comma, a period or a figure (CLEARED), which no letter is to be over
without kerning: a side that would be gets the least that clears them
(_cleared), kerned back within Greek.

On a grid, they are pixelated where in a cell they fall
best (shapes.phased's placements), of those where each straight stem is as
many cells thick as that stem of MCKL's pixel letter (STEMS): a stem a
cell thicker reads as bold in a line. Where no placement does (the two
arms of Ψ fall apart in their cells, Italic's slanted stems come out a
cell over MCKL's), the cells over are taken off the stem's left edge, row
by row, as far as it runs as thick, not where a serif or another stroke
joins it, and only if the letter keeps its pieces and counters (_held);
and η φ χ ψ end on the row p does (DEEP). Those that then read as another
letter, or close a counter the letter does not have, are drawn by hand,
cell by cell (drawn/greek.txt).

Within a run (within: Greek, and the figures, marks, brackets and
superscripts a shaper sets with it), they are kerned as Redaction's
letters of the same sides (KERNED): each joins the kerning classes and
pairs of the letter its right side is, when it comes first, and of the
one its left side is, when it comes second, MCKL's values. χ is not: its
legs reach under its neighbours, as no letter of Redaction's does; the
letters and marks that reach down to them are set apart by hand (PAIRS).
Then (finish, _fitted, once every module has drawn its glyphs, and
add_features, for the characters of a run Noto Serif JP brings to the
merge: ′ ″ ¤ ¦ ¬ ‒ ※...) no pair is left one over the other: it is opened
by the least that clears it and AIR units, on a grid by whole cells.
There, no two share an edge either, cells side by side or one above the
other, unless the pair of Redaction's
letters they stand as (edged) shares one: Τ and λ, two Ψ, ψ and ω. Cells
that meet at a corner only are left: slanted letters of pixels do
everywhere. Beside a Latin letter, which a browser sets in another run but
some shapers do not, a pair is kept no nearer than that of Redaction's
letter of that side. μ and χ have a descender, a hook and a leg where u
and x have nothing (ROWED): a pair may share an edge at its baseline, as
u and x do, and theirs hang on to the letter before them by the hook, or
under it by the descender. They share an edge with a neighbour, of their
run or Latin, only on the rows where the letter they stand as would meet
it in their place.

γ δ ε ζ ξ ς are left out: nothing of Redaction's draws them well.
"""

import copy
import unicodedata

import numpy as np
import pathops
from fontTools.pens.basePen import BasePen
from fontTools.ttLib.tables import otTables
from fontTools.ttLib.tables.otBase import ValueRecord
from fontTools.unicodedata import script

import pixel

from . import maths
from .shapes import (
    _pieces,
    _placed,
    add,
    cells,
    composite,
    drawn,
    drawn_cells,
    glyph,
    path,
    rect,
    union_paths,
    widths,
)

# Redaction's own: {code point: its letter}
SAME = dict(zip([0x0391, 0x0392, 0x0395, 0x0396, 0x0397, 0x0399, 0x039A], "ABEZHIK"))
SAME |= dict(zip([0x039C, 0x039D, 0x039F, 0x03A1, 0x03A4, 0x03A5, 0x03A7, 0x03BF], "MNOPTYXo"))
# Turned upside down: {code point: (its letter, the letter it is set as)}
TURNED = {0x039B: ("V", "A")}
# Drawn by hand: {code point: the letter its strokes are as thick as, on a grid}
DRAWN = dict(zip([0x0393, 0x0394, 0x0398, 0x039E, 0x03A6, 0x03A8, 0x03A9], "FAOEOUO"))
DRAWN |= dict(zip([0x03B1, 0x03B2, 0x03B7, 0x03B8, 0x03B9, 0x03BA, 0x03BB], "opn0ukv"))
DRAWN |= dict(zip([0x03BD, 0x03C0, 0x03C1, 0x03C3, 0x03C4, 0x03C5, 0x03C6], "vnpotuo"))
DRAWN |= dict(zip([0x03C7, 0x03C8, 0x03C9], "xuo"))
# The letters each stands as, on its left and on its right, where not that one
SIDED = {0x03B1: "oa", 0x03B2: "pß", 0x03B7: "nq", 0x03C0: "nt", 0x03C1: "oo", 0x03C3: "ot"}
SIDED |= {0x03C5: "uo", 0x03C7: "yx", 0x03C8: "uo"}
ITALIC_SIDED = {0x03B1: "ox", 0x03B2: "ßß", 0x03B9: "ıı", 0x03BB: "xx", 0x03C7: "xx"}
# On a grid, the right arm of υ ψ is a column of cells, as u's stem is: o's
# side meets a neighbour along one cell, and would let the arm lie against
# the letter after it from top to bottom. For the edges a pair may share
# (edged), they stand as u on that side
EDGED = {0x03C5: "u", 0x03C8: "u"}
# Pairs that share no edge on a grid whatever Redaction's letters do: η's right
# stem and β's fused in one bar twice as thick, a dozen cells long, where q and
# p share one
UNFUSED = {(0x03B7, 0x03B2)}
# Those that share an edge on a grid only on the rows where the letter they
# stand as (like) would meet that neighbour in their place: μ's descender,
# χ's hook, tail and leg are where u and x have nothing, and an edge u or x
# shares at the baseline would let them hang on to a neighbour there
ROWED = {0x03BC, 0x03C7}
# On a grid, units off the side bearings fitted gives: {(code point, style,
# grid): (left, right)}. The feet came off η κ λ ψ in their outlines, their
# side bearings the wider by the reach of each foot (η's right one by 79
# units, Bold's 72), but their cells lost less than that (Regular's η on
# 20), none (on 100, drawn without them), or more, and a side bearing rounds
# to a cell more or less than they lost: each stands where it did with its
# feet, on the same columns, and as wide
REFITTED = {(0x03B7, "Regular", 20): (0, -20), (0x03B7, "Regular", 100): (0, -100)}
REFITTED |= {(0x03B7, "Bold", 100): (0, -100)}
REFITTED |= {(0x03BA, "Regular", 50): (0, -50), (0x03BA, "Regular", 70): (70, 0)}
REFITTED |= {(0x03BA, "Bold", 35): (0, 35)}
REFITTED |= {(0x03BB, "Regular", 10): (-10, 10), (0x03BB, "Regular", 20): (-20, 0)}
REFITTED |= {(0x03BB, "Regular", 70): (0, 70), (0x03BB, "Bold", 10): (-10, 0)}
REFITTED |= {(0x03BB, "Bold", 20): (0, 20), (0x03BB, "Bold", 50): (0, -50)}
REFITTED |= {(0x03BB, "Bold", 70): (70, 70)}
REFITTED |= {(0x03C8, "Italic", 10): (-10, 0), (0x03C8, "Italic", 35): (-35, 0)}
REFITTED |= {(0x03C8, "Italic", 50): (-50, 0)}
# Italic's ρ: its left side bearing is 30 units more than it was, which on 35,
# 70 and 100 rounds to none: a cell there, as p stands from the letter before
# it, its stem and its bowl (without it, every letter touches it on 70). Not
# on 50, where its cells lean more than p's: with a cell its stem's foot is
# where p's is, but its bowl a cell further from the letter before it than
# p's, and than o's (ορ wider than ρο, οο); without, its bowl is where theirs
# is, and its foot a cell nearer than p's, clear of a comma by a cell, kerned
REFITTED |= {(0x03C1, "Italic", 35): (35, 0), (0x03C1, "Italic", 70): (70, 0)}
REFITTED |= {(0x03C1, "Italic", 100): (100, 0)}
# χ, drawn anew: as wide as it was where its side bearings round otherwise
REFITTED |= {(0x03C7, "Regular", 20): (0, -20), (0x03C7, "Bold", 50): (0, 50)}
DELTA, INCREMENT = 0x0394, 0x2206  # one design: Δ is ∆, between its own side bearings
# Δ's side bearings: how far over A's, left and right. Italic's A leans over
# its neighbours, its feet a hairline apart: Δ's base ends as far from them
APART = {"Regular": (28, 28), "Bold": (28, 28), "Italic": (10, 6)}
OHM = 0x2126  # the ohm sign: the glyph of Ω
# Straight stems: {character: [(between which heights, which stroke across,
# counted from the left or, under 0, from the right; the letter whose stem
# it is, between which heights, which stroke)]}, and Italic's where they
# differ (its α has none, its ι is ı's). The arms of υ ψ are the zero's
# sides, curves: not among them
XH, DESC, CAP = (100, 330), (-160, -30), (250, 450)
STEMS = {
    "Γ": [(CAP, 0, "F", (130, 300), 0)],
    "Φ": [(CAP, 1, "I", CAP, 0)],
    "Ψ": [((120, 220), 0, "I", (120, 220), 0), ((480, 620), 0, "U", (480, 620), -1)],
    "β": [(DESC, 0, "p", DESC, 0)],
    "η": [(XH, 0, "n", XH, 0), (DESC, 0, "n", XH, -1)],
    "ι": [(XH, 0, "u", XH, -1)],
    "κ": [((60, 260), 0, "k", (60, 260), 0)],
    "π": [(XH, 0, "t", XH, 0), (XH, -1, "t", XH, 0)],
    "ρ": [(DESC, 0, "p", DESC, 0)],
    "τ": [((120, 330), 0, "t", (120, 330), 0)],
    "φ": [(DESC, 0, "p", DESC, 0)],
    "ψ": [(DESC, 0, "p", DESC, 0)],
}
STEMS["Ψ"].append(((480, 620), -1, "U", (480, 620), -1))
ITALIC_STEMS = {"α": [], "ι": [(XH, 0, "ı", XH, 0)], "β": [((150, 400), 0, "ß", (150, 400), 0)]}
DEEP = {"η": "p", "φ": "p", "χ": "p", "ψ": "p"}  # end, below, on the row this letter does
# Kerned as Redaction's: {code point: (the letter its right side is, when
# it comes first, the letter its left side is, when it comes second)}, the
# ones of SAME as their letter. Ω stands on feet no letter of Redaction's
# has, χ's strokes reach under and over its neighbours: they are not kerned
KERNED = {cp: (letter, letter) for cp, letter in SAME.items()}
KERNED |= {0x0393: ("F", "F"), 0x0394: ("A", "A"), 0x0398: ("O", "O"), 0x039B: ("A", "A")}
KERNED |= {0x03B1: ("a", "o"), 0x03B7: (None, "n"), 0x03B8: ("o", "o"), 0x03BA: ("k", "k")}
KERNED |= {0x03BD: ("v", "v"), 0x03C1: ("o", "o"), 0x03C3: (None, "o"), 0x03C5: ("o", "u")}
KERNED |= {0x03C6: ("o", "o"), 0x03C8: ("o", "u"), 0x03C9: ("o", "o")}
ITALIC_KERNED = {0x03B1: ("x", "o")}  # Italic's α ends as its x does
# Pairs set apart, by style: {(first, second): how far, in units}, on a grid
# the cells that is, or more. χ's curl reaches under the letter after it:
# these reach down to it, 12 units apart so
PAIRS = {"Regular": {("χ", "j"): 52}, "Bold": {("χ", "j"): 47}}
PAIRS["Italic"] = {("χ", "f"): 192, ("χ", "j"): 194, ("χ", "ß"): 192, ("χ", "y"): 95}
PAIRS["Italic"] |= {("χ", "p"): 78, ("χ", "g"): 49}
# Pairs a cell further apart than all of the above sets them, on one grid:
# {(style, grid): pairs}. Italic's α ends in a's tail, which reaches further
# than x's: on 10 its tip is against ¿, on 20 against the ball J ends in,
# where x is a cell from them
FURTHER = {("Italic", 10): ["α¿"], ("Italic", 20): ["αJ", "αĴ"]}
# Σ Π μ, letterlike.py's: the letters of Redaction they stand as. They are
# as letterlike.py sets them, and only set apart from a letter they meet
OTHERS = {0x03A3: "Z", 0x03A0: "H", 0x03BC: "u"}
# What no letter is over by its side bearings alone (_cleared)
CLEARED = ",.0123456789"
AIR = 12  # units of air a pair set apart gets, without a grid
LOW, HIGH, FAR = -700, 2100, 1e6  # the rows a glyph is measured on (Reach): from, how many units
PAIRPOS = 60000  # bytes a subtable of pairs may be: its offsets are 16 bits
CELLS = "greek.txt"  # the letters drawn by hand on a grid, cell by cell
SIDES = "com.lihbr.kuronuri.sides"  # in an outline's lib: its side bearings
CODEPOINTS = {cp: f"uni{cp:04X}" for cp in sorted([*SAME, *TURNED, *DRAWN])}
CODEPOINTS[OHM] = CODEPOINTS[0x03A9]
ALTERNATES = []
SAMPLES = [
    "ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ",
    "αβηθικλμνοπρστυφχψω",
    "AΑΛΔ OΘΩΦ EΞΣΓ UΨ uμυω pρ vν kκ tτπ oσ aα xχ nη ıι",
    "aα dα oα nη pη qη nπ τπ Ππ pρ oρ tτ Tτ oφ φΦ xχ Xχ uω oω mω",
    "α版 β版 πr² φ=1.618 χ² ω=2πf 5Ω",
    "α版 β版 πr² Δt λ=h/p 10μm 5Ω 5Ω Δ∆ χ²検定",
    "xχ χ² χρ χβ φχψ ψυχή ηχ αχ χχ χ, (χ) gχ χj χy",
    "uυ υψω nυn nψn ΔΔ ΔA Δt Δx AΔ HΔH ΔT",
    "Ελληνικά ΕΛΛΗΝΙΚΑ Ωμέγα ΑΘΗΝΑ Τα Το Τυ Τω Αυ Γα Γο",
    "αβγδεζηθ ικλμνξοπ ρστυφχψω ς",
    "HΓH HΔH HΘH HΛH HΞH HΦH HΨH HΩH",
    "nαn nβn nηn nθn nιn nκn nλn nνn nπn nρn nσn nτn nυn nφn nχn nψn nωn",
    "σο σα ασ αχ οχ ρχ ηχ ιλ λι υυ ωω ψψ",
    "Τλ ΨΨ Γθ \\χ χ, χ. χ² gχ χj",
    "漢Δ版 漢Ω版 黒χ字 5Ω Δt 漢λ字 xλx xρx",
    "Τλ xλx nλn αλ λ=h/p xρx nρn πρ",
    "ψυχη φωτα πολυ καλα θαλασσα απο το ηλιο ΨΥΧΗ ΦΩΤΑ ΘΑΛΑΣΣΑ",
]


def letterlike():
    """Whether maths.py's ∆ is the letter drawn by hand from A and Z, whose
    outline Δ then takes, not its triangle of line work."""
    return INCREMENT in getattr(maths, "OPERATORS", {})


def outline(hand, cp):
    """The outline of `cp` among those drawn by hand for a style (`hand`,
    shapes.drawn), and its lib: Δ's is ∆'s, when that is the letter (in a
    font, it is ∆'s glyph: add_glyphs)."""
    if cp == DELTA and letterlike() and chr(INCREMENT) in hand:
        return hand[chr(INCREMENT)][0], hand.get(chr(cp), (None, {}))[1]
    return hand[chr(cp)]


def stems(style):
    """STEMS, as they are in `style`."""
    return STEMS | ITALIC_STEMS if style == "Italic" else STEMS


def add_glyphs(font, smooth, grid=None):
    """Add the letters to `font`: a Redaction style, or one of Redaction 10 to
    100 on `grid`, as drawn for the style of `smooth`, the same style
    without a grid."""
    style = smooth["name"].getDebugName(2)
    hand = drawn(style)
    cmap, glyf, hmtx = font.getBestCmap(), font["glyf"], font["hmtx"]
    out = {}
    for cp, letter in SAME.items():
        name = cmap[ord(letter)]
        out[CODEPOINTS[cp]] = composite(font, [(name, 0, 0)], grid), hmtx[name][0]
    for cp, (letter, like) in TURNED.items():
        x0, _, x1, y1 = path(font, letter).bounds
        shape = glyph(path(font, letter, (-1, 0, 0, -1, x0 + x1, y1)))
        sides = glyf[cmap[ord(like)]]
        sides.recalcBounds(glyf)
        shape.coordinates.translate((sides.xMin - shape.xMin, 0))
        wider = (x1 - x0) - (sides.xMax - sides.xMin)
        out[CODEPOINTS[cp]] = shape, hmtx[cmap[ord(like)]][0] + wider
    shapes = {CODEPOINTS[cp]: glyph(outline(hand, cp)[0]) for cp in DRAWN}
    if grid:
        shapes = _pixels(font, shapes, grid, style)
    if letterlike():  # Δ is ∆: maths.py's glyph, its outline or its pixels, cells drawn by hand too
        increment = glyf[cmap[INCREMENT]]  # greek comes after maths (glyphs.MODULES)
        shapes[CODEPOINTS[DELTA]] = copy.deepcopy(increment)
    for cp in DRAWN:
        name = CODEPOINTS[cp]
        shape = shapes[name]
        lsb, rsb = fitted(font, smooth, cp, grid)
        shape.recalcBounds(None)
        shape.coordinates.translate((lsb - shape.xMin, 0))
        out[name] = shape, shape.xMax - shape.xMin + lsb + rsb
    add(font, out, CODEPOINTS)
    for name in out:  # as saved, to measure them, each where its side bearing says
        if not glyf[name].isComposite():
            glyf[name].coordinates.toInt()
            glyf[name].recalcBounds(glyf)
            hmtx[name] = hmtx[name][0], glyf[name].xMin
    for name, (left, right) in _cleared(font, grid).items():
        glyf[name].coordinates.translate((left, 0))
        glyf[name].recalcBounds(glyf)
        hmtx[name] = hmtx[name][0] + left + right, glyf[name].xMin
    kerned = KERNED | ITALIC_KERNED if style == "Italic" else KERNED
    names = {
        CODEPOINTS[cp]: tuple(side and cmap[ord(side)] for side in sides)
        for cp, sides in kerned.items()
    }
    _kern(font, names)


def finish(font, smooth, grid=None):
    """Set apart the pairs of a run that meet (_fitted), once every module
    has added its glyphs: superscripts and marks drawn after these are
    among them."""
    _apart(font, _fitted(font, smooth, grid))


def add_features(font):
    """Set apart, as finish does, the pairs of a Greek letter and a
    character of its run Noto Serif JP brings to the merged `font` (′ ″ ¤
    ¦ ¬ ‒ ‑ ※ ⁂...): Redaction lacks them, so finish never saw them."""
    from family import redaction

    from . import CODEPOINTS

    family, style = font["name"].getDebugName(1).split(), font["name"].getDebugName(2)
    grid = int(family[-1]) if family[-1].isdigit() else None
    smooth = redaction(None, style)
    ours = set(smooth.getBestCmap()) | set(CODEPOINTS)
    noto = [name for name, c in within(font).items() if ord(c) not in ours]
    _apart(font, _fitted(font, smooth, grid, noto))


def fitted(font, smooth, cp, grid=None):
    """The side bearings the letter `cp` is drawn between, in `font` of
    add_glyphs, before what a comma, a period or a figure takes
    (_cleared): those its outline says (Δ, A's and APART); on `grid`, as
    far from those of MCKL's pixel letters of the same sides (SIDED) as
    drawn from theirs without a grid; Δ with a cell of air where its base
    ends (on 100, on its right only), Italic's a cell more than MCKL's A
    where the sides of that A are under a cell together: two of them meet;
    each off by what REFITTED says."""
    style = smooth["name"].getDebugName(2)
    if cp == DELTA:
        sides = tuple(a + b for a, b in zip(_sides(smooth, "A"), APART[style]))
    else:
        sides = outline(drawn(style), cp)[1][SIDES]
    if not grid:
        return tuple(sides)
    like = (ITALIC_SIDED if style == "Italic" else {}).get(cp) or SIDED.get(cp) or DRAWN[cp] * 2
    left, right = (
        pixel.snap(_sides(font, letter)[k] + sides[k] - _sides(smooth, letter)[k], grid)
        for k, letter in enumerate(like)
    )
    if cp == DELTA and style == "Italic":  # it leans: its sides are not air
        a = _sides(font, "A")
        more = grid if sum(a) < grid else 0
        left, right = max(left, a[0] + more), max(right, a[1] + more)
    elif cp == DELTA:
        left, right = left if grid == 100 else max(left, grid), max(right, grid)
    more = REFITTED.get((cp, style, grid), (0, 0))
    return left + more[0], right + more[1]


def _pixels(font, shapes, grid, style):
    """`shapes` ({name: glyph}) on `grid`: each where in a cell it falls best
    (shapes._placed, as shapes.phased ranks them), of the placements where
    its straight stems are as many cells thick as MCKL's (STEMS), or the
    best of all if there are none; those drawn by hand, their cells."""
    cmap, glyf = font.getBestCmap(), font["glyf"]
    theirs = {}
    for cp, letter in DRAWN.items():
        source = glyf[cmap[ord(letter)]]
        source.recalcBounds(glyf)
        theirs[CODEPOINTS[cp]] = list(widths(cells(source, grid)[0]))
    placed = _placed(shapes, grid, None, theirs, True, None, False)  # pixelated together
    out = dict(shapes)
    for cp in DRAWN:
        name, char = CODEPOINTS[cp], chr(cp)
        if cp == DELTA and letterlike():
            continue  # ∆'s glyph: add_glyphs
        by_hand = drawn_cells(CELLS).get((grid, style, char))
        if by_hand:
            out[name] = _cells(by_hand, grid)
            continue
        wanted = [
            (band, run, stem_cells(glyf[cmap[ord(letter)]], grid, their_band, their_run))
            for band, run, letter, their_band, their_run in stems(style).get(char, [])
        ]
        options = [option[2] for option in placed[name]]
        fit = [o for o in options if not _off(o, grid, wanted)]
        out[name] = fit[0] if fit else _held(options[0], grid, wanted)
        if char in DEEP:
            bottom = glyf[cmap[ord(DEEP[char])]]
            bottom.recalcBounds(glyf)
            out[name] = _raised(out[name], grid, bottom.yMin)
    return out


def _raised(g, grid, bottom):
    """Pixel glyph `g`, down to `bottom` and no lower: a serif or an arm
    drawn at p's descender falls a row under where MCKL's p ends. As many
    rows are taken out, each the lowest of those likest the row over it,
    the rows under it moved up."""
    on, (left, top), _ = cells(g, grid)
    over = round(bottom / grid) - (top - len(on))
    kept = list(range(len(on)))
    for _ in range(max(over, 0)):  # under its middle: the rows of its descender, or its crossing
        low = range(len(kept) // 2, len(kept))
        unlike = {k: (on[kept[k]] != on[kept[k - 1]]).sum() for k in low}
        del kept[min(unlike, key=lambda k: (unlike[k], -k))]
    return _cells_at(on[kept], left, top, grid) if over > 0 else g


def _off(g, grid, wanted):
    """The stems of pixel glyph `g` a cell or more thicker or thinner than
    `wanted` ([(band, run, cells)]): [(band, run, how many cells over)].
    Slanted, a stem is not as thick on every row: half a cell is none."""
    off = []
    for band, run, theirs in wanted:
        ours = stem_cells(g, grid, band, run)
        if ours is not None and theirs is not None and abs(ours - theirs) >= 1:
            off.append((band, run, int(ours - theirs)))
    return off


def _held(g, grid, wanted):
    """Pixel glyph `g`, each stem a cell or more off `wanted` (_off) made as
    thick, where no placement does: on each row of the stem, the cells over
    taken off its left edge, or those lacking added to it. The stem is the
    rows of its band as thick as most of them, and those above and below
    for as long as it runs alone and as thick, its edges within a cell of
    the row before: not a serif, nor where another stroke joins it or it
    branches. `g` as it is, if it would not keep its pieces and counters,
    or its stems would still be off: that one is to draw by hand."""
    off = _off(g, grid, wanted)
    if not off:
        return g
    on, (left, top), _ = cells(g, grid)
    pad = 1 + max(abs(over) for _, _, over in off)
    on = np.pad(on, ((0, 0), (pad, 0)))
    # drawn as `held` is, cells that meet at a corner too: to compare their pieces
    before = _cells_at(on, left - pad, top, grid)

    def spans(row):
        edges = np.flatnonzero(np.diff(np.concatenate([[0], row.astype(int), [0]])))
        return list(zip(edges[::2], edges[1::2]))

    for band, run, over in off:
        rows = [i for i in range(len(on)) if band[0] <= (top - i - 0.5) * grid <= band[1]]
        rows = [i for i in rows if len(spans(on[i])) > max(run, -run - 1)]
        if not rows:
            continue
        found = {i: spans(on[i])[run] for i in rows}
        thick = np.median([b - a for a, b in found.values()])
        todo = {i: ab for i, ab in found.items() if abs(ab[1] - ab[0] - thick) <= 0.5}
        for step in (-1, 1):  # up, then down
            i = rows[0] if step < 0 else rows[-1]
            if i not in todo:
                continue
            a, b = todo[i]
            while 0 <= i + step < len(on):
                i += step
                over_it = [(c, d) for c, d in spans(on[i]) if c < b and d > a]
                if len(over_it) != 1:  # it ends, or branches
                    break
                c, d = over_it[0]
                if abs(d - c - thick) > 0.5 or abs(c - a) > 1 or abs(d - b) > 1:
                    break  # a serif, a join: not as thick, or not where the stem is
                todo[i] = a, b = c, d
        for i, (a, _) in todo.items():
            if over > 0:
                on[i, a : a + over] = False
            else:
                on[i, a + over : a] = True
    held = _cells_at(on, left - pad, top, grid)
    if _off(held, grid, wanted) or _topology(held) != _topology(before):
        return g
    return held


def _topology(g):
    """How many pieces and counters glyph `g` has."""
    p = pathops.Path()
    g.draw(pathops.PathPen(p), None)
    return _pieces(p)


def _cells_at(on, left, top, grid):
    """A glyph of the cells `on`, rows top down, from the grid x of its left
    and y of its top."""
    return glyph(
        union_paths(
            [
                rect(x * grid, y * grid, (x + 1) * grid, (y + 1) * grid)
                for x, y in ((left + j, top - i - 1) for i, j in zip(*np.nonzero(on)))
            ]
        )
    )


def stem_cells(g, grid, band, run):
    """How many cells thick the stroke `run` of pixel glyph `g` is, across
    (counted from the left or, under 0, from the right), between the
    heights of `band`: the median of its rows, None without one."""
    on, (_, top), _ = cells(g, grid)
    found = []
    for i, row in enumerate(on):
        if not band[0] <= (top - i - 0.5) * grid <= band[1]:
            continue
        edges = np.flatnonzero(np.diff(np.concatenate([[0], row.astype(int), [0]])))
        lengths = edges[1::2] - edges[::2]
        if len(lengths) > max(run, -run - 1):
            found.append(lengths[run])
    return float(np.median(found)) if found else None


def _sides(font, letter):
    """The side bearings of `letter` in `font`."""
    name = font.getBestCmap()[ord(letter)]
    g = font["glyf"][name]
    g.recalcBounds(font["glyf"])
    return g.xMin, font["hmtx"][name][0] - g.xMax


def _cells(cells, grid):
    """A glyph of `cells` drawn by hand (shapes.drawn_cells), its bottom row
    where they say."""
    top = cells.at[1] + len(cells)
    return glyph(
        union_paths(
            [
                rect(j * grid, (top - i - 1) * grid, (j + 1) * grid, (top - i) * grid)
                for i, row in enumerate(cells)
                for j, c in enumerate(row)
                if c == "#"
            ]
        )
    )


def _kern(font, like):
    """Kern the glyphs of `like` ({name: (the glyph it is kerned as when it
    comes first, and when it comes second), either None}) in `font`: each
    joins the classes of those glyphs (PairPos 2) and gets their pairs
    (PairPos 1), before and after. They are the last glyphs of the font, in
    that order: added last, coverages and pairs stay sorted."""
    like = dict(sorted(like.items(), key=lambda kv: font.getGlyphID(kv[0])))
    for lookup in font["GPOS"].table.LookupList.Lookup:
        for sub in lookup.SubTable:
            if lookup.LookupType != 2:
                continue
            first = sub.Coverage.glyphs
            if sub.Format == 2:
                for new, (before, after) in like.items():
                    if before in first:
                        first.append(new)
                    if before in sub.ClassDef1.classDefs:
                        sub.ClassDef1.classDefs[new] = sub.ClassDef1.classDefs[before]
                    if after in sub.ClassDef2.classDefs:
                        sub.ClassDef2.classDefs[new] = sub.ClassDef2.classDefs[after]
                continue
            for new, (before, _) in like.items():
                if before in first:
                    sub.PairSet.append(copy.deepcopy(sub.PairSet[first.index(before)]))
                    first.append(new)
            for pairs in sub.PairSet:
                for new, (_, after) in like.items():
                    for record in [r for r in pairs.PairValueRecord if r.SecondGlyph == after]:
                        record = copy.deepcopy(record)
                        record.SecondGlyph = new
                        pairs.PairValueRecord.append(record)
                pairs.PairValueCount = len(pairs.PairValueRecord)
            sub.PairSetCount = len(sub.PairSet)


def _apart(font, pairs):
    """Kern the pairs of `pairs` ({(first, second): value}, glyph names) in
    `font`: subtables of their own, before MCKL's, which go on applying to
    every other pair of the same first glyph (PairPos 1 falls through when
    the second is not found). As many subtables as their offsets, of 16
    bits, need."""
    order, apart = font.getGlyphID, {}
    for (first, second), value in pairs.items():
        apart.setdefault(first, {})[second] = value
    lookup = next(x for x in font["GPOS"].table.LookupList.Lookup if x.LookupType == 2)
    subs, size = [], PAIRPOS
    for first in sorted(apart, key=order):
        if size + 4 + 4 * len(apart[first]) > PAIRPOS:
            sub = otTables.PairPos()
            sub.Format, sub.ValueFormat1, sub.ValueFormat2 = 1, 4, 0
            sub.Coverage = otTables.Coverage()
            sub.Coverage.glyphs, sub.PairSet, size = [], [], 16
            subs.append(sub)
        pair_set = otTables.PairSet()
        pair_set.PairValueRecord = []
        for second in sorted(apart[first], key=order):
            record = otTables.PairValueRecord()
            record.SecondGlyph = second
            record.Value1 = ValueRecord()
            record.Value1.XAdvance = apart[first][second]
            pair_set.PairValueRecord.append(record)
        pair_set.PairValueCount = len(pair_set.PairValueRecord)
        sub.Coverage.glyphs.append(first)
        sub.PairSet.append(pair_set)
        sub.PairSetCount = len(sub.PairSet)
        size += 8 + 4 * len(apart[first])
    lookup.SubTable[:0] = subs
    lookup.SubTableCount = len(lookup.SubTable)


class _Lines(BasePen):
    """The edges of an outline, its curves cut in STEPS lines."""

    STEPS = 16

    def __init__(self, glyphs):
        super().__init__(glyphs)
        self.edges, self.start = [], None

    def _moveTo(self, pt):
        self.start = pt

    def _lineTo(self, pt):
        self.edges.append((*self._getCurrentPoint(), *pt))

    def _closePath(self):
        if self._getCurrentPoint() != self.start:
            self._lineTo(self.start)

    def _qCurveToOne(self, a, b):
        p, last = self._getCurrentPoint(), self._getCurrentPoint()
        for i in range(1, self.STEPS + 1):
            t = i / self.STEPS
            pt = tuple((1 - t) ** 2 * p[k] + 2 * (1 - t) * t * a[k] + t * t * b[k] for k in (0, 1))
            self.edges.append((*last, *pt))
            last = pt


def shift(glyf, hmtx, name):
    """How far right of where its components say the composite glyph `name`
    is set (Reach.shift), 0 for a glyph of contours."""
    glyph = glyf[name]
    if not glyph.isComposite():
        return 0
    for part in glyph.components:
        if part.flags & 0x200:  # USE_MY_METRICS: set as this component is
            base = glyf[part.glyphName]
            base.recalcBounds(glyf)
            own = hmtx[part.glyphName][1] - base.xMin if not base.isComposite() else 0
            return own + shift(glyf, hmtx, part.glyphName)
    glyph.recalcBounds(glyf)
    return hmtx[name][1] - glyph.xMin


class Reach:
    """How far the glyphs of `font` reach, row by row: the rows of cells on
    `grid`, a unit high without one (from LOW up), to measure how far apart
    two glyphs set side by side are (gap), and whether they meet (meet)."""

    def __init__(self, font, grid=None):
        self.font, self.grid = font, grid
        self.glyphs, self.glyf, self.hmtx = font.getGlyphSet(), font["glyf"], font["hmtx"]
        self.sides, self.paths, self.inked = {}, {}, {}

    def shift(self, name):
        """How far right of where its components say a composite glyph is
        set: a rasterizer sets every glyph by its left side bearing, which
        in Redaction's Italic is not always where its outline starts (U,
        so Ù), a composite by that of the component whose metrics it
        takes, if any. The glyph set does it for a glyph of contours only."""
        return shift(self.glyf, self.hmtx, name)

    def edges(self, name):
        pen = _Lines(self.glyphs)
        self.glyphs[name].draw(pen)
        edges = np.array(pen.edges, float).reshape(-1, 4)
        edges[:, ::2] += self.shift(name)
        return edges

    def __getitem__(self, name):
        """(left, room) of glyph `name`: on each row, where its ink starts
        from its origin, and how far it ends before its advance, FAR on a
        row without ink. On a grid a row is a row of cells; without one,
        the unit above a height and that height, which is in two rows."""
        if name not in self.sides:
            step = self.grid or 1
            left, right = np.full(HIGH // step, FAR), np.full(HIGH // step, -FAR)
            x0, y0, x1, y1 = self.edges(name).T
            if self.grid:  # cells: the edges that go up or down bound them
                up = x0 == x1
                x, a, b = x0[up], np.minimum(y0, y1)[up], np.maximum(y0, y1)[up]
                first, count = ((a - LOW) // step).astype(int), ((b - a) // step).astype(int)
            else:  # each edge, at its ends and at every height it crosses
                a, b = np.minimum(y0, y1), np.maximum(y0, y1)
                first = np.ceil(a - LOW).astype(int)
                count = np.maximum(np.floor(b - LOW).astype(int) - first + 1, 0)
            which = np.repeat(np.arange(len(first)), count)
            rows = (
                first[which] + np.arange(count.sum()) - np.repeat(np.cumsum(count) - count, count)
            )
            if self.grid:
                xs = x[which]
            else:  # a height is in the row over it and the one under
                rise = (y1 - y0)[which]
                t = np.divide(
                    rows + LOW - y0[which], rise, out=np.zeros(len(rise)), where=rise != 0
                )
                across, flat = (x0[which] + t * (x1 - x0)[which])[rise != 0], rise == 0
                level = np.concatenate([x0[which][flat], x1[which][flat]])
                xs = np.concatenate([across, across, level, level, x0, x1])
                on, ends = np.tile(rows[flat], 2), [np.floor(y - LOW).astype(int) for y in (y0, y1)]
                rows = np.concatenate([rows[~flat], rows[~flat] - 1, on, on - 1, *ends])
            xs, rows = xs[(rows >= 0) & (rows < len(left))], rows[(rows >= 0) & (rows < len(left))]
            np.minimum.at(left, rows, xs)
            np.maximum.at(right, rows, xs)
            room = np.where(right > -FAR / 2, self.hmtx[name][0] - right, FAR)
            self.sides[name] = left, room
        return self.sides[name]

    def wide(self, name, side):
        """The `side` (0 left, 1 room) of glyph `name` on the rows over and
        under each row, the lesser: where a cell of a neighbour touches
        one of its own at a corner, or along its top or bottom. FAR
        without a grid, where a row is of the height over it too."""
        reach = self[name][side]
        wide = np.full(len(reach), FAR)
        if self.grid:
            wide[1:] = reach[:-1]
            wide[:-1] = np.minimum(wide[:-1], reach[1:])
        return wide

    def gap(self, first, second, kerning=0):
        """The least air across between glyph `first` and `second` after it,
        over their rows: 0 if they touch, less if one is over the other,
        by that much."""
        room = self[first][1]
        return float(gaps(room + kerning, self[second][0][None], self.wide(second, 0)[None])[0])

    def cells(self, name):
        """The cells of pixel glyph `name`: {(column, row)}."""
        if name not in self.inked:
            g, crossed, cells = self.grid, {}, set()
            for x0, y0, x1, y1 in self.edges(name):
                if x0 == x1:
                    for row in range(int(min(y0, y1)) // g, int(max(y0, y1)) // g):
                        crossed.setdefault(row, []).append((int(x0) // g, 1 if y1 > y0 else -1))
            for row, edges in crossed.items():
                inside = 0
                for (a, turn), (b, _) in zip(sorted(edges), sorted(edges)[1:]):
                    inside += turn
                    if inside:
                        cells.update((column, row) for column in range(a, b))
            self.inked[name] = cells
        return self.inked[name]

    def path(self, name):
        if name not in self.paths:
            p = pathops.Path()
            self.glyphs[name].draw(pathops.PathPen(p, glyphSet=self.glyphs))
            self.paths[name] = p.transform(1, 0, 0, 1, self.shift(name), 0)
        return self.paths[name]

    def meet(self, first, second, kerning=0):
        """How glyph `second`, set after `first`, `kerning` apart, meets it:
        OVER if one is over the other; else on a grid EDGE if a cell of one
        is beside or above a cell of the other, CORNER if two meet at a
        corner only; without a grid NEAR if their outlines are within a
        unit, across or up and down; 0 if they are clear."""
        dx = self.hmtx[first][0] + kerning
        if self.grid:
            a, shift = self.cells(first), round(dx / self.grid)
            b = {(column + shift, row) for column, row in self.cells(second)}
            if a & b:
                return OVER
            sides = ((-1, 0), (1, 0), (0, -1), (0, 1))
            corners = ((-1, -1), (-1, 1), (1, -1), (1, 1))
            if any((c + i, r + j) in a for c, r in b for i, j in sides):
                return EDGE
            return CORNER if any((c + i, r + j) in a for c, r in b for i, j in corners) else 0
        a, b = self.path(first), self.path(second)
        for near, x, y in ((OVER, 0, 0), (NEAR, -1, 0), (NEAR, 0, 1), (NEAR, 0, -1)):
            moved = b.transform(1, 0, 0, 1, dx + x, y)
            if abs(pathops.op(a, moved, pathops.PathOp.INTERSECTION).area) > 1e-3:
                return near
        return 0

    def rows(self, first, second, dx):
        """On a grid, the rows on which glyph `second`, set `dx` units after
        the origin of `first`, meets it: a cell of one beside a cell of the
        other, or over it, and both rows of two cells one above the other."""
        a, shift, rows = self.cells(first), round(dx / self.grid), set()
        for column, row in self.cells(second):
            c = column + shift
            if a & {(c - 1, row), (c, row), (c + 1, row)}:
                rows.add(row)
            rows.update(r for j in (-1, 1) if (c, row + j) in a for r in (row, row + j))
        return rows

    def over(self, first, second, kerning=0):
        """Whether glyph `second`, set after `first`, `kerning` apart, is
        over it: they share a cell, or ink."""
        if self.grid:
            shift = round((self.hmtx[first][0] + kerning) / self.grid)
            a, b = self.cells(first), self.cells(second)
            return any((column + shift, row) in a for column, row in b)
        if (self[first][1] + kerning + self[second][0]).min() > 1:
            return False  # a unit apart on every row
        moved = self.path(second).transform(1, 0, 0, 1, self.hmtx[first][0] + kerning, 0)
        return abs(pathops.op(self.path(first), moved, pathops.PathOp.INTERSECTION).area) > SLIVER

    def apart(self, first, second, kerning=0):
        """How much further apart than `kerning` glyph `second` is to be set
        after `first` not to be over it: the least, in units, on a grid in
        cells."""
        more, step = 0, self.grid or 1
        if not self.grid:  # from their rows, to a unit or two
            more = max(0, int(-(self[first][1] + kerning + self[second][0]).min()) - 2)
            while more and not self.over(first, second, kerning + more - 1):
                more -= 1
        while self.over(first, second, kerning + more):
            more += step
        return more


OVER, EDGE, CORNER, NEAR = 3, 2, 1, 1  # how two glyphs meet (Reach.meet)
SLIVER = 1e-5  # the area two outlines share, in square units, from which one is over the other


def like(cp, style):
    """The letters of Redaction the Greek letter `cp` stands as, on its left
    and on its right: its own for one of Redaction's."""
    if cp in SAME:
        return SAME[cp] * 2
    if cp in TURNED:
        return TURNED[cp][1] * 2
    if cp in OTHERS:
        return OTHERS[cp] * 2
    return (ITALIC_SIDED if style == "Italic" else {}).get(cp) or SIDED.get(cp) or DRAWN[cp] * 2


def gaps(mine, same, over, corners=True):
    """The least air between a glyph and each of its neighbours: `mine`, its
    side on each row (Reach), `same` and `over`, the sides of the
    neighbours that face it, on the same row and on those over and under
    ([neighbour][row]). On the same row a cell is over another, by as much
    as is under 0; on the row over it only touches: 0, if `corners`."""
    level, across = (mine + same).min(axis=1), (mine + over).min(axis=1)
    return np.minimum(level, np.maximum(across, 0)) if corners else level


def edged(cp, style):
    """The letters of Redaction the Greek letter `cp` stands as (like), left
    and right, for the edges a pair may share on a grid: EDGED's on its
    right."""
    left, right = like(cp, style)
    return left, EDGED.get(cp, right)


def _cleared(font, grid):
    """How much more each letter drawn takes on a side than the side
    bearings it is drawn between (fitted), {name: (left, right)}, not to
    be over a comma, a period or a figure (CLEARED) set before or after it
    without kerning: the least that clears them, on a grid in cells.
    Touching one is as Redaction's own letters do."""
    cmap, reach = font.getBestCmap(), Reach(font, grid)
    marks = [cmap[ord(c)] for c in CLEARED]
    out = {}
    for cp in [*DRAWN, *TURNED]:
        name = cmap[cp]
        left = max(reach.apart(mark, name) for mark in marks)
        right = max(reach.apart(name, mark) for mark in marks)
        if left or right:
            out[name] = left, right
    return out


def cleared(font, smooth, grid=None):
    """What _cleared gave each letter in `font`, as it stands there: {name:
    (left, right)}, its side bearings over those it is drawn between
    (fitted)."""
    cmap, glyf, hmtx, out = font.getBestCmap(), font["glyf"], font["hmtx"], {}
    for cp in [*DRAWN, *TURNED]:
        name = cmap[cp]
        glyf[name].recalcBounds(glyf)
        sides = glyf[name].xMin, hmtx[name][0] - glyf[name].xMax
        # one turned stands between the side bearings of the letter it is set as
        drawn = _sides(font, TURNED[cp][1]) if cp in TURNED else fitted(font, smooth, cp, grid)
        more = tuple(a - b for a, b in zip(sides, drawn))
        if any(more):
            out[name] = more
    return out


def _kerning(font):
    """How `font` kerns a pair of glyphs: a function of their names."""
    lookups = []
    for lookup in font["GPOS"].table.LookupList.Lookup:
        if lookup.LookupType == 2:
            subs = []
            for sub in lookup.SubTable:
                first = {name: i for i, name in enumerate(sub.Coverage.glyphs)}
                if sub.Format == 1:
                    pairs = [
                        {
                            r.SecondGlyph: getattr(r.Value1, "XAdvance", 0) or 0
                            for r in pair_set.PairValueRecord
                        }
                        for pair_set in sub.PairSet
                    ]
                    subs.append((first, pairs, None))
                else:
                    subs.append((first, None, sub))
            lookups.append(subs)

    def kerning(a, b):
        value = 0
        for subs in lookups:
            for first, pairs, sub in subs:
                if a not in first:
                    continue
                if pairs is not None:
                    if b not in pairs[first[a]]:
                        continue  # falls through
                    value += pairs[first[a]][b]
                else:
                    one, two = sub.ClassDef1.classDefs.get(a, 0), sub.ClassDef2.classDefs.get(b, 0)
                    v = sub.Class1Record[one].Class2Record[two].Value1
                    value += getattr(v, "XAdvance", 0) or 0
                break
        return value

    return kerning


def within(font):
    """The characters of `font` a shaper sets in one run with a Greek letter
    beside it, so kerns with it: the Greek letters, and those of every
    script (figures, punctuation, brackets, signs, superscripts): {name:
    character}."""
    cmap, out = font.getBestCmap(), {}
    for cp, name in cmap.items():
        kind = unicodedata.category(chr(cp))[0]
        greek = cp in CODEPOINTS or cp in OTHERS
        if greek or (script(cp) == "Zyyy" and kind in "NPS" and (cp < 0x2100 or cp == OHM)):
            out.setdefault(name, chr(cp))
    return out


def _fitted(font, smooth, grid, others=None):
    """The pairs to set apart in `font`: {(first, second): value}, glyph
    names, of a Greek letter and every glyph of its run and Latin letter,
    or of `others` only. Each starts as it is kerned (_kern), or as PAIRS
    says.

    Within a run (within): a letter that took more for a comma, a period
    or a figure (cleared) gets back the side bearings it is drawn between.
    Then no pair is left one over the other: it is opened by the least
    that clears it, and AIR units; on a grid by whole cells, until no cell
    of one is beside or above a cell of the other either, unless the pair
    of Redaction's letters they stand as, as MCKL kerns it, has such an
    edge, and is not one over the other: both that of like and that of
    edged, and never a pair of UNFUSED. Cells that meet at a corner are
    left.

    Beside a Latin letter, which a browser sets in a run of its own but
    some shapers do not, a pair is set apart only as far as that of the
    letter of Redaction the Greek one stands as, if that is nearer:
    Redaction's own letters meet on a grid, and a few of its pairs are
    kerned one over the other.

    On a grid, a pair with a letter of ROWED, of a run or not, is then
    opened by whole cells until it meets on no row but those where the
    letter it stands as would, set in its place: by its advance when it
    comes first, from its origin when it comes second. And the pairs of
    FURTHER, a cell more."""
    style = smooth["name"].getDebugName(2)
    cmap, reach, kerning = font.getBestCmap(), Reach(font, grid), _kerning(font)
    step, clear, more = grid or 1, grid or 1, cleared(font, smooth, grid)
    advance = {name: width for name, (width, _) in font["hmtx"].metrics.items()}
    run = within(font)
    greek = {cmap[cp]: cp for cp in [*OTHERS, *SAME, *TURNED, *DRAWN] if cp in cmap}
    latin = [n for cp, n in cmap.items() if script(cp) == "Latn" and chr(cp).isalpha()]
    latin = list(dict.fromkeys(n for n in latin if n not in run))
    hand = {
        (cmap[ord(a)], cmap[ord(b)]): -(-v // step) * step for (a, b), v in PAIRS[style].items()
    }
    further = {tuple(cmap.get(ord(c)) for c in pair) for pair in FURTHER.get((style, grid), [])}
    pairs = {}

    def fit(first, second):
        both = first in run and second in run
        as_is = kerning(first, second)
        value = hand.get((first, second), as_is)
        a = cmap[ord(like(greek[first], style)[1])] if first in greek else first
        b = cmap[ord(like(greek[second], style)[0])] if second in greek else second
        if both or (first, second) in hand:  # between the side bearings it is drawn
            value -= more.get(first, (0, 0))[1] + more.get(second, (0, 0))[0]
        if both:
            if opened := reach.apart(first, second, value):
                value += opened + (0 if grid else AIR)
            if grid and reach.meet(first, second, value) == EDGE:
                # an edge of both pairs it stands as: EDGED's takes edges away, it gives none
                c = cmap[ord(edged(greek[first], style)[1])] if first in greek else first
                d = cmap[ord(edged(greek[second], style)[0])] if second in greek else second
                shared = all(reach.meet(*p, kerning(*p)) == EDGE for p in ((a, b), (c, d)))
                if not shared or (greek.get(first), greek.get(second)) in UNFUSED:
                    value += step
                    while reach.meet(first, second, value) >= EDGE:
                        value += step
        else:  # as far as Redaction's letter is from it, over it if that one is
            wanted = min(clear, reach.gap(a, b, kerning(a, b)))
            if reach.gap(first, second, value) < wanted and reach.meet(first, second, value) > (
                0 if wanted > 0 else NEAR
            ):
                while reach.gap(first, second, value) < wanted:
                    value += step
        rowed = [greek.get(name) in ROWED for name in (first, second)]
        if grid and any(rowed):  # on the rows its letter would meet it, in its place
            c, d = a if rowed[0] else first, b if rowed[1] else second
            while not reach.rows(first, second, advance[first] + value) <= reach.rows(
                c, d, advance[c] + value
            ):
                value += step
        if (first, second) in further:
            value += step
        if value != as_is:
            pairs[first, second] = value

    for name in greek:
        for other in [*run, *latin] if others is None else others:
            fit(name, other)
            if other not in greek:
                fit(other, name)
    return pairs
