#!/usr/bin/env python3
"""Checks for the fonts in dist/.

- OTS, the sanitizer browsers run on web fonts, accepts every font and slice.
- With `tnum`, all digits have the same advance, next to Latin and Japanese.
- `calt` turns -> <- <-> -^ ^- => <=> =^ into arrows, also in Japanese
  text, but leaves <= ^= and the ^-^ ^=^ =^.^= =^_^= emoticons as typed,
  and `ss01` swaps in the alt arrows.
- The vertical metrics are Redaction's, so the baseline sits where it does
  in Redaction for the same line height.
- In pixel variants, every point, advance and component offset is on the grid.
- No space has ink: of U+000D, 0020, 00A0, 2000 to 200B, 202F, 205F, 3000
  and FEFF, those the fonts have (Redaction Italic's en and em spaces had
  its dashes).
- All kana are present, and every glyph of src/glyphs, but no Hangul,
  Bopomofo or Latin ligatures from Noto Serif JP.
- Every character has an outline, composites resolved, but whitespace,
  control and format characters, variation selectors, and blanks (BLANK):
  Redaction 100 Bold's | has none (glyphs/mended.py), and a mark smaller
  than half a cell pixelates to nothing (﹒ on 100, glyphs/small.py).
- The glyphs drawn from Redaction's are made of them: fullwidth forms are
  Redaction's glyph centred in the em; Roman numerals, ‼ and ⑴ are as wide
  as what they are made of, set with kerning; enclosed numbers and letters
  are centred on the em box.
- Enclosed glyphs, arrows, integrals and Greek letters drawn by hand on a
  grid (glyphs/drawn/cells.txt, arrows.txt, maths.txt and greek.txt) are
  so, cell for cell, in the fonts of their grid and style, and the arrows'
  alts too, or as their own cells where they are drawn apart ("↗.ss01").
- Every outline drawn by hand (glyphs/drawn) loads, is used, and has no
  self-intersections: enclosed content has the pieces and counters of
  Redaction's glyph; 〒 stands upright, as tall as T, its two bars and stem
  as thick as T's (Italic's measured across its slant), in two pieces; the
  owner's arrow head is that of Regular's → as built, in one piece; ∑ ∏ ∐
  ∂ ∫ ∆ have the pieces and counters of the letter each is drawn from (Z T
  T 6 f A), and ∬ ∭ as many pieces as integrals; ∆ is as tall as A, and ∇,
  ∆ turned over, as V, with the counter of ∆; so do Σ Π μ ℏ (Z T u, and
  Italic's ħ), every letter of letterlike.py drawn.
- Italic's enclosed lowercase grown across (enclosed.GROWN) keeps the
  points of its outline before it grew, segment for segment, so every notch
  of Redaction's carving is one cut as MCKL drew it, as open, moved, and
  it does not cross itself; on 50, 70 and 100 it is not grown. As shipped,
  every letter, blended further too, against the same drawn as before it
  grew and as grown: its points are where growth puts them, to their
  rounding, so its counters as wide and its notches as deep; its joins
  that were smooth are smooth, the flats and walls of the cuts of a letter
  grown across as long as before, to the rounding of their ends; and on
  10, 20 and 35 its pixels read as before it grew: in as many pieces, with
  no counter it had not, none fewer but those it does not have as drawn,
  touching at a corner in no more places, by its cells and by its outline.
- The Greek letters drawn by hand (glyphs/greek.py) are all there in every
  style, with their side bearings and what they are drawn from, the
  pieces and counters of that letter, or their own (Θ's bar splits O's),
  and straight stems as thick as those of the letter each is drawn from;
  Φ Ψ φ ψ have two ledges, one on each side of the stem, never two at one
  height; ρ has d's notch where its bowl comes back to its stem, as deep;
  the bars of π and τ are as thick as Π's; no lowercase letter stands on
  a serif foot (η κ λ μ ρ φ χ ψ end as thick as they run); χ's thin stroke
  runs from the upper left to the lower right; Italic's α crosses itself,
  little wider than a, its bowl as full, its arm ending in a ball over
  x's step.
  In the fonts, each stands between the side bearings its outline says, as
  far from those of MCKL's pixel letter on a grid, and no more, but the
  least that keeps it from being over a comma, a period or a figure set
  beside it without kerning; its straight stems are as many cells
  thick as that letter's, on every row of the stem, one row over the
  other; those drawn cell by cell stand on the row they say, and the
  others are, cell for cell, as pictured (test/greek-cells.json: a serif
  or a join lost fails); the ohm sign is the glyph of Ω, and Δ the shape
  of ∆ when maths.py draws it as the letter. Each is kerned as the letter
  of Redaction it is kerned as (greek.KERNED), pair for pair, but those
  set apart because they would meet. Italic's μ stands as u does, as wide
  and its body where u's is, its descender alone under the letter before
  it; Italic's ρ has its bowl as far from that letter as p's stem.
- With kerning, no Greek letter is over another one, or a figure, mark,
  bracket, sign or superscript set before or after it, in any font; on a
  grid, no cell of one is beside or above a cell of the other either,
  unless the pair of Redaction's letters they stand as has such an edge
  (and is not one over the other). Cells that meet at a corner may. Nor
  does it meet a Latin letter more than the letter of Redaction it stands
  as does. μ and χ (greek.ROWED) meet a neighbour only on the rows where u
  and x would in their place: not by a descender, a hook or a leg.
- `frac` sets any fraction of digits, from parts: numerators, the fraction
  slash and denominators, `1/2` as `11/12` and `489/603`, as many digits as
  there are (60 before the slash); the slash only between digits, so `1 1/2`
  keeps its integer; a run of two slashes or more (2024/05/06, 3/4/5,
  x.com/1/2, /1/2, 1/2/) as typed; ⁄ typed between digits as `/` with
  `frac` on, and without it (HarfBuzz turns `numr` and `dnom` on around
  it); first, before `tnum`, `sups` and `subs`. Every drawn fraction of
  digits (⅓ ⅒ ↉) is `frac`'s, in place, outline and advance, between two
  letters: n⅓n is n1/3n. No two digits of a numerator or a denominator
  touch: a cell apart at least on a grid, as far as MCKL sets ¹ ² ³ at
  least without; nor a part and the slash. Redaction's ¹ ² ³ keep their
  advance. ⁄ drawn by hand on a grid (glyphs/drawn/figures.txt) is so,
  cell for cell. / and ⁄ are alike: 1/2⁄3 is as typed, with `frac` and
  without. Measured on the shaped glyphs, not the model: every fraction of
  a digit or two over a digit or two holds its ink, ½'s right side bearing
  past it at least; none touches a letter, punctuation, a superscript or
  subscript digit, kanji, kana, halfwidth kana or fullwidth form before or
  after it (BEFORE, AFTER, and a glyph of each class the font positions
  fractions beside), a cell apart at least on a grid. In vertical text a
  fraction there is a glyph for is that glyph, with / or ⁄, `frac` on or ⁄
  typed, and others are as typed. `numr`, `sups`, `dnom`,
  `subs` and `sinf` alone give superscripts and subscripts as typed, as
  wide. `kern` uses `frac`'s positioning lookups, the same ones, which
  apply once: fractions are set alike with `kern` off, with `frac` on
  them only, and with ⁄ typed (HarfBuzz turns `frac` on around it), the
  glyph before them included (RANGED).
- Small digits are set as MCKL sets ¹ ² ³: no two superscripts, subscripts,
  `numr`, `dnom` or parts of `frac` side by side nearer than he sets any two
  of ¹ ² ³; on a grid, the parts of `frac` a cell apart at least, the others
  not over each other; and, smooth, each pair in proportion to the same
  digits full size as his are (check_small).
- /review sets text as the built fonts do: its text fonts (.tmp/review)
  shape as those of dist/, outlines and positions, across and down; every
  built font has one (unless CI is set and there is no .tmp/review).
- `ordn` raises 1st with `sups` on too.
- Every figure and width feature, and `kern`, is in every script and language
  system, as DFLT's: `ordn` and `subs` work in Japanese text (latn JAN, hani).
- `fwid`, `hwid` and `pwid` swap ASCII, katakana and their width forms, voiced
  kana split and joined: every pair Unicode decomposes so (<wide>, <narrow>)
  and those of Noto Serif JP the build keeps (NOTO_WIDTHS), into a glyph of
  the width of the form, Noto Serif JP's own where it has one.
- Italics declare Redaction Italic's slant (post, hhea); Regular and Bold none.
  Each style is one, everywhere: its name records (English and Japanese),
  OS/2 weight and fsSelection, head macStyle and the italic angle.
- No two superscript letters (ª º, those `ordn` raises, the c of ℅) are
  drawn alike, but on 100, where they are three cells high: there c and e
  have the same placements, and come out alike.
- The pixelated Japanese, on 50, 70 and 100 (check_japanese): in Regular
  and Italic, kana and kanji stand on the rows they took before they were
  lightened, as many
  rows in all, their ink in their advance; punctuation, brackets and marks
  are as they stand; every advance, vertical advance and origin of Noto's
  glyphs and their vertical forms is grade 0's on the grid; no two
  brackets, nor a bracket and a comma, period or middle dot, set across or
  down, with or without palt, halt, vpal, vhal or chws, share a cell but
  where the fonts before did (OVERLAPPING); pairs a stroke or a mark tells
  apart stay so many cells apart (APART), and divided counters stay
  divided (COUNTERS); and which of two look-alikes moves does not depend on
  the order of the glyphs (check_order). In Bold, every glyph of Noto
  Serif JP is Noto's 800 pixelated as it stands, unlightened and unphased,
  its spacing and brackets as above, and its common kanji inked BOLDER
  than Regular's (check_bold).
- review.py makes the Japanese reference only from the fonts --before
  names, with where they came from, and a vertical form changed alone
  shows as changed (check_reference).
- dist/web: index.css imports every family, each family CSS lists every
  slice with a unicode-range equal to its cmap, the slices of a style do
  not overlap and cover the whole font, and the Latin-only CSS lists the
  latin and latin-ext slices. Halfwidth katakana are in one slice a style,
  for `fwid` to join ｶﾞ.
"""

import functools
import io
import json
import math
import os
import re
import shutil
import sys
import tempfile
import unicodedata
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import ots
import pathops
import uharfbuzz as hb
from fontTools import subset
from fontTools.pens.basePen import BasePen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import otTables as ot
from fontTools.ufoLib import UFOReader
from fontTools.unicodedata import category, script

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import build  # noqa: E402
import glyphs  # noqa: E402
import pixel  # noqa: E402
import web  # noqa: E402
from family import (  # noqa: E402
    FAMILY_JA,
    GRIDS,
    NOTO_WEIGHT,
    SELECTORS,
    STYLES,
    family_name,
    light,
    noto_glyphs,
    noto_weight,
    ps_name,
    redaction,
)
from glyphs import (  # noqa: E402
    arrows,
    enclosed,
    figures,
    fullwidth,
    greek,
    letterlike,
    maths,
    numerals,
    punctuation,
)
from glyphs.shapes import (  # noqa: E402
    CORNER,
    DRAWN,
    SMOOTH,
    _contours,
    _pieces,
    broadened,
    cells,
    drawn,
    drawn_cells,
    glyph,
    grooves,
    path,
    runs,
    slope,
    stem,
)
from pixel import pixelate_font, snap, snap_advance  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
KANA = [*range(0x3041, 0x3097), *range(0x30A1, 0x30FB)]
DIGITS = "0123456789"
SPACES = [0x0D, 0x20, 0xA0, *range(0x2000, 0x200C), 0x202F, 0x205F, 0x3000, 0xFEFF]
FACE = re.compile(
    r'font-family: "([^"]+)";\s*font-style: (\w+);\s*font-weight: (\d+);'
    r'.*?url\("([^"]+)\?no-inline"\).*?unicode-range: ([^;]+);',
    re.S,
)
STYLE = {("normal", "400"): "Regular", ("italic", "400"): "Italic", ("normal", "700"): "Bold"}
ARROWS = {
    "->": 0x2192,
    "<-": 0x2190,
    "<->": 0x2194,
    "-^": 0x2191,
    "^-": 0x2193,
    "=>": 0x21D2,
    "<=>": 0x21D4,
    "=^": 0x21D1,
}
METRICS = {
    "hhea": ("ascent", "descent", "lineGap"),
    "OS/2": ("sTypoAscender", "sTypoDescender", "sTypoLineGap", "usWinAscent", "usWinDescent"),
}
# Ordinals that raise every superscript letter but c (that of ℅)
SUPERIORS = ["1st", "2nd", "3rd", "4th", "1er", "2e", "1a", "1o"]
# ordn: text, and how much of it stays as typed: ordinal suffixes after
# digits are raised, but not other letters, nor suffixes before letters or digits
ORDINALS = {"2nd": "2", "1er": "1", "3as": "3", "3am": "3am", "2e3": "2e3", "1stuff": "1stuff"}
AS_TYPED = ["^-^", "^=^", "=^.^=", "=^_^=", "<=", "^=", "a<=b"]
# Characters without ink that are not whitespace (Zs Zl Zp), control (Cc)
# or format (Cf) characters: the braille blank and the Hangul fillers
BLANK = {0x2800, 0x115F, 0x1160, 0x3164, 0xFFA0}

# frac: text, and what each character becomes: n a numerator, d a
# denominator, f the fraction slash, . as typed
FRACTIONS = {
    "1/2": "nfd",
    "11/16": "nnfdd",
    "123/456": "nnnfddd",
    "131/365": "nnnfddd",
    "489/603": "nnnfddd",
    "12/34 5/6": "nnfdd.nfd",
    "1 1/2": "..nfd",
    "1.5/2": "..nfd",
    "2024/1/2": "........",
    "2024/05/06": "..........",
    "3/4/5": ".....",
    "https://x.com/1/2": ".................",
    "/1/2": "....",
    "1/2/": "....",
    "1/x": "...",
    "1⁄2": "nfd",
    "11⁄12": "nnfdd",
    # slashes of either kind alike: two make a run as typed
    "1/2⁄3": ".....",
    "1⁄2/3": ".....",
    "1⁄2⁄3": ".....",
    "12⁄3/4": "......",
}
# Fractions whose ink their advance holds (check_inked), besides every one of
# a digit or two over a digit or two
INKED = ["489/603", "111/444", "999999/000000", "0123456789/9876543210", "1/10", "10/1"]
# What fractions are set beside (check_beside): letters, superscript and
# subscript digits (a digit next to one is part of it), punctuation of both
# scripts, kanji, kana, halfwidth kana and fullwidth forms; before them, and
# after. And a glyph of each class the font positions fractions beside
BEFORE = "TVWYFPKHfrt7([{'\"n²₂,回日、あ語話訃時ルアｱｦﾙｰＷＡ０（￥「」。…′"
AFTER = ",.;:)]}!?'\"nAjfTVW²₂回日、。語話訃時ルアあｱｦﾙｰＷＡ０）￥「」…′"
BESIDE = ["1/2", "0/1", "1/1", "7/8", "4/5", "9/7", "10/1", "11/12", "489/603", "1/10", "0/3"]
BESIDE += ["⅓", "⅞", "½", "⅟", "℅"]
# What a glyph of each class is set before (each digit first, of one or two
# digits) and after (each digit last, after the slash or another)
CLASSED = [f"{d}/1" for d in DIGITS] + ["12/3", "1/11", "1/23"] + [f"1/{d}" for d in DIGITS]
# ...and every drawn fraction: each may take a class of its own (⅗)
CLASSED += list("¼½¾⅐⅑⅒⅓⅔⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞↉℅")
# Fractions with the glyph before or after them, `frac` on the fraction
# only (and ⁄ typed, where HarfBuzz turns it on there): set as with `frac`
# on all of it
RANGED = ["f7/8", "H7/8", "T1/2", "Ｗ7/1", "Ｗ1/1", "語1/1", "1/1語", "1/1ｱ", "7/8f", "(1/2)"]
# Fractions set apart in vertical text: those not drawn, as typed
VERTICAL = ["11/12", "489/603", "2/9", "11⁄12", "1/2/3"]
LONG = (20, 21, 60)  # digits of numerators, all raised
# Text /review sets as the built fonts do, with each feature it offers on, and
# kern off, in Latin and Japanese text
REVIEWED = [
    "A A ABC abc 123 !? ·—–",
    "ｱｲｳｶﾞﾊﾟｳﾞ｡ アイウガパヴ。「ー」 ＡＢＣ１２３",
    "n1/3n n⅓n 489/603 111/444 1 1/2 2024/05/06 x.com/1/2 1234567890123456789012345/6",
    "4th; 1st 2e No. 5 H2O x² 第1回 日123円 砂糖1/2カップ",
    "-> <=> =^.^= ½ ⅒",
]
# Features on with frac, and what else they turn digits into: in a
# fraction, its digits are numerators and denominators still
WITH_FRAC = {
    ("1 1/2", "tnum"): "t.nfd",
    ("2 1/2", "sups"): "s.nfd",
    ("H2O 1/2", "subs"): ".i..nfd",
    ("1/2nd", "ordn"): "nfd..",
}
# Feature, text, language: shaped differently with the feature on, in
# Japanese text as in Latin
JAPANESE = [
    ("ordn", "1st", "ja"),
    ("subs", "日123円", "ja"),
    ("sinf", "日123円", "ja"),
    ("dnom", "日123円", "ja"),
    ("numr", "日123円", "ja"),
    ("sups", "日123円", "ja"),
    ("tnum", "日1円", "ja"),
    ("frac", "日1/2円", "ja"),
    ("fwid", "ABC123", "ja"),
]
# Width features: text, feature, what it becomes
WIDTHS = [
    ("ABC123 abc!?", "fwid", "ＡＢＣ１２３　ａｂｃ！？"),
    ("ｱｲｳｶﾞﾊﾟｳﾞ｡", "fwid", "アイウガパヴ。"),
    ("アイウガパヴ。「ー」", "hwid", "ｱｲｳｶﾞﾊﾟｳﾞ｡｢ｰ｣"),
    ("ＡＢＣ１２３", "hwid", "ABC123"),
    ("ＡＢＣ１２３", "pwid", "ABC123"),
]
# What Noto Serif JP's width features map besides Unicode's width forms, which
# the build keeps (glyphs/fullwidth.py), written out again here
NOTO_WIDTHS = {
    "fwid": {"·": "・", "—": "―"},
    "hwid": {"|": "￨"},
    "pwid": {"―": "—", "〜": "~", "∕": "/", "‵": "`", "￨": "|"},
}


@functools.cache
def hb_font(path):
    ttf = TTFont(path)
    ttf.flavor = None  # HarfBuzz cannot read WOFF2
    data = io.BytesIO()
    ttf.save(data)
    return hb.Font(hb.Face(hb.Blob(data.getvalue())))


def shape(path, text, features=None, language=None, direction=None):
    """Glyph ids and advances of `text` shaped with HarfBuzz."""
    font = hb_font(path)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    if language:
        buf.language = language
    if direction:
        buf.direction = direction
    hb.shape(font, buf, features or {})
    return [i.codepoint for i in buf.glyph_infos], [p.x_advance for p in buf.glyph_positions]


def tabular(path, text, language=None):
    """Whether the digits in `text` all have the same advance with `tnum`."""
    advances = shape(path, text, {"tnum": True}, language)[1]
    return len({a for a, c in zip(advances, text) if c.isdigit()}) == 1


def sanitize(path):
    res = ots.sanitize(str(path), capture_output=True)
    if res.returncode:
        return [f"{path.name}: OTS: {res.stderr.decode().strip().splitlines()[-1]}"]
    return []


def check_font(path):
    problems = sanitize(path)
    if path.suffix != ".ttf":
        return problems
    if not tabular(path, DIGITS) or not tabular(path, f"価格{DIGITS}円", "ja"):
        problems.append(f"{path.name}: tnum is not tabular")
    font = TTFont(path)
    cmap = font.getBestCmap()
    gid = {cp: font.getGlyphID(name) for cp, name in cmap.items()}
    for text, cp in ARROWS.items():
        if (
            shape(path, text)[0] != [gid[cp]]
            or shape(path, f"東{text}京", None, "ja")[0][1] != gid[cp]
        ):
            problems.append(f"{path.name}: {text} does not turn into {chr(cp)}")
        alt = shape(path, chr(cp), {"ss01": True})[0]
        if alt == [gid[cp]] or shape(path, text, {"ss01": True})[0] != alt:
            problems.append(f"{path.name}: ss01 does not swap in the alt {chr(cp)}")
    for text in AS_TYPED:
        if len(shape(path, text)[0]) != len(text):
            problems.append(f"{path.name}: {text} is not left as typed")
    # Figure features: frac, subs, ordn
    if shape(path, "2", {"subs": True})[0] != [gid[0x2082]]:
        problems.append(f"{path.name}: subs does not turn 2 into ₂")
    problems += check_frac(path, font)
    problems += check_inked(path, font)
    problems += check_beside(path, font)
    problems += check_vertical(path, font)
    problems += check_alone(path, font)
    problems += check_small(path, font)
    problems += check_shared_lookups(path, font)
    if shape(path, "1st", {"ordn": True, "sups": True})[0] != [
        shape(path, "1", {"sups": True})[0][0],
        *shape(path, "1st", {"ordn": True})[0][1:],
    ]:
        problems.append(f"{path.name}: ordn does not raise 1st with sups on")
    problems += check_shared(path, font)
    for text, feature, expected in WIDTHS:
        if shape(path, text, {feature: True}, "ja")[0] != [gid[ord(c)] for c in expected]:
            problems.append(f"{path.name}: {feature} does not turn {text} into {expected}")
    problems += check_widths(path, font)
    problems += check_style(path, font)
    for text, kept in ORDINALS.items():
        ordn = shape(path, text, {"ordn": True})[0]
        raised = [len(ordn) != len(text) or g != gid[ord(c)] for g, c in zip(ordn, text)]
        if raised != [i >= len(kept) for i in range(len(text))]:
            problems.append(f"{path.name}: ordn raises other than {text[len(kept) :]} in {text}")
    for text, expected in (("1a", "1ª"), ("No. 5", "№ 5")):
        if shape(path, text, {"ordn": True})[0] != [gid[ord(c)] for c in expected]:
            problems.append(f"{path.name}: ordn does not turn {text} into {expected}")
    # Drawn punctuation turns in vertical Japanese text, as Noto Serif JP's does
    for c in "，．：＝":
        if shape(path, f"日{c}", direction="ttb")[0][1] == gid[ord(c)]:
            problems.append(f"{path.name}: {c} does not turn in vertical text")
    m = re.match(r"Kuronuri(\d+)-(\w+)", path.stem)
    source = redaction(int(m.group(1)) or None, m.group(2))
    post, hhea = font["post"], font["hhea"]
    slant = (post.italicAngle, hhea.caretSlopeRise, hhea.caretSlopeRun, hhea.caretOffset)
    if STYLES[m.group(2)]["italic"]:
        angle = math.degrees(math.atan(slope(redaction(None, "Italic"))))
        run = hhea.caretSlopeRun / hhea.caretSlopeRise
        if abs(post.italicAngle + angle) > 0.5 or abs(math.degrees(math.atan(run)) - angle) > 0.5:
            problems.append(f"{path.name}: italic angle {slant} is not Redaction Italic's")
    elif slant != (0, 1, 0, 0):
        problems.append(f"{path.name}: upright, but its italic angle and caret are {slant}")
    for tag, attrs in METRICS.items():
        for attr in attrs:
            if getattr(font[tag], attr) != getattr(source[tag], attr):
                problems.append(f"{path.name}: {tag} {attr} is not Redaction's")
    if grid := int(m.group(1)):
        glyf, hmtx = font["glyf"], font["hmtx"]
        off = 0
        for name in font.getGlyphOrder():
            g = glyf[name]
            if hmtx[name][0] % grid:
                off += 1
            elif g.isComposite():
                off += any(c.x % grid or c.y % grid for c in g.components)
            elif g.numberOfContours > 0:
                off += any(x % grid or y % grid for x, y in g.coordinates)
        if off:
            problems.append(f"{path.name}: {off} glyphs off the {grid}-unit grid")
        problems += check_cells(path, font, grid)
    gs = font.getGlyphSet()
    for cp in SPACES:
        if cp in cmap:
            ink = BoundsPen(gs)
            gs[cmap[cp]].draw(ink)
            if ink.bounds:
                problems.append(f"{path.name}: U+{cp:04X} has ink {ink.bounds}")
    if empty := check_empty(font):
        shown = " ".join(f"U+{c:04X}" for c in empty[:8])
        problems.append(f"{path.name}: {len(empty)} characters without an outline: {shown}")
    problems += check_greek_font(path, font, source, int(m.group(1)), m.group(2))
    if missing := [chr(c) for c in KANA if c not in cmap]:
        problems.append(f"{path.name}: missing kana {''.join(missing)}")
    if missing := [chr(c) for c in glyphs.CODEPOINTS if c not in cmap]:
        problems.append(f"{path.name}: missing drawn glyphs {''.join(missing)}")
    # Redaction has ﬁ and ﬂ, Noto Serif JP the other Latin ligatures.
    ligatures = set(range(0xFB00, 0xFB50)) - {0xFB01, 0xFB02}
    if trimmed := [chr(c) for c in cmap if script(c) in ("Hang", "Bopo") or c in ligatures]:
        problems.append(f"{path.name}: {len(trimmed)} Hangul, Bopomofo or ligatures")
    problems += check_drawn(path, font)
    return problems


def check_empty(font):
    """The code points of `font` whose glyph has no outline, composites
    resolved, but whitespace, control and format characters, variation
    selectors, and blanks (BLANK): they show nothing where a mark is typed."""
    gs, empty = font.getGlyphSet(), []
    for cp, name in sorted(font.getBestCmap().items()):
        if cp in BLANK | SELECTORS or category(chr(cp)) in ("Zs", "Zl", "Zp", "Cc", "Cf"):
            continue
        pen = BoundsPen(gs)
        gs[name].draw(pen)
        if pen.bounds is None:
            empty.append(cp)
    return empty


def check_frac(path, font):
    """`frac` sets fractions as FRACTIONS and WITH_FRAC, ⁄ typed between
    digits without it, and numerators as LONG as they come; the drawn
    fractions of digits are as `frac` sets them; no two of its parts touch;
    and Redaction's ¹ ² ³ keep their advance."""
    problems, cmap = [], font.getBestCmap()
    num = {d: shape(path, f"{d}/1", {"frac": True})[0][0] for d in "0123456789"}
    den = {d: shape(path, f"1/{d}", {"frac": True})[0][2] for d in "0123456789"}
    forms = {"t": {"tnum": True}, "s": {"sups": True}, "i": {"subs": True}}

    def expected(text, mask):
        out = []
        for c, k in zip(text, mask):
            if k == "f":
                out.append(font.getGlyphID(cmap[0x2044]))
            elif k == ".":
                out.append(font.getGlyphID(cmap[ord(c)]))
            elif k in "nd":
                out.append((num if k == "n" else den)[c])
            else:
                out.append(shape(path, c, forms[k])[0][0])
        return out

    cases = [(text, {"frac": True}, mask) for text, mask in FRACTIONS.items()]
    cases += [(text, {"frac": True, f: True}, mask) for (text, f), mask in WITH_FRAC.items()]
    cases += [(text, {}, mask) for text, mask in FRACTIONS.items() if "⁄" in text]
    for text, features, mask in cases:
        if shape(path, text, features)[0] != expected(text, mask):
            problems.append(f"{path.name}: {' '.join(features) or 'no feature'} sets {text} wrong")
    if len(set(num.values()) | set(den.values())) != 20:
        problems.append(f"{path.name}: frac does not set numerators and denominators")
    for n in LONG:
        digits = ("1234567890" * 6)[:n]
        typed = shape(path, f"{digits}⁄6"), shape(path, f"{digits}⁄6", {"frac": True})
        slashed = shape(path, f"{digits}/6", {"frac": True})
        if slashed[0][:n] != [num[d] for d in digits] or any(t != slashed for t in typed):
            problems.append(f"{path.name}: frac does not raise {n} digits as ⁄ typed does")
    # The drawn fractions of digits, between two letters, as frac sets them
    for cp, (n, d) in figures.FRACTIONS.items():
        if not (n + d).isdigit() or not d:
            continue  # ⅟ ℀ ℅: no digits frac sets so
        typed, drawn = f"n{n}/{d}n", f"n{chr(cp)}n"
        a, b = ink(path, font, typed, {"frac": True}), ink(path, font, drawn, {"frac": True})
        advances = sum(shape(path, typed, {"frac": True})[1]), sum(shape(path, drawn)[1])
        if abs(pathops.op(a, b, pathops.PathOp.XOR).area) > 1 or advances[0] != advances[1]:
            problems.append(f"{path.name}: {typed} with frac is not {drawn}, {advances}")
    # No two parts touch: digits of numerators and denominators, a cell apart
    # at least on a grid, as far as MCKL's ¹ ² ³ at least without; the slash
    m = re.match(r"Kuronuri(\d+)-(\w+)", path.stem)
    grid, style = int(m.group(1)), m.group(2)
    apart = grid or figures._gap(redaction(None, style))
    for a in "0123456789":
        for b in "0123456789":
            for text, i in ((f"{a}{b}/1", 0), (f"1/{a}{b}", 2)):
                parts = ink(path, font, text, {"frac": True}, apart=True)
                if not figures._apart(parts[i], parts[i + 1], apart):
                    problems.append(f"{path.name}: {a}{b} touch in {text} with frac")
        for text, i in ((f"{a}/1", 0), (f"1/{a}", 2)):
            parts = ink(path, font, text, {"frac": True}, apart=True)
            if len(parts) != 3 or not figures._apart(parts[i], parts[1], grid or 1):
                problems.append(f"{path.name}: {a} touches the slash in {text} with frac")
    source = redaction(grid or None, style)
    for c in "¹²³":
        if source["hmtx"][source.getBestCmap()[ord(c)]][0] != font["hmtx"][cmap[ord(c)]][0]:
            problems.append(f"{path.name}: {c} is not as wide as Redaction's")
    return problems


def check_inked(path, font):
    """A fraction holds its ink, independently of how it is made: none of
    it left of where the fraction starts, nor right of its advance less
    ½'s right side bearing (smooth, a cell at least on a grid, at most a
    unit off), for every fraction of a digit or two over a digit or two,
    and INKED. In Italic the right is measured along the slant, as far past
    the denominators' ink as the slash leans: its letters hang over their
    advance as they stand, and what a fraction must not touch after it is
    check_beside's."""
    m = re.match(r"Kuronuri(\d+)-(\w+)", path.stem)
    grid, style = int(m.group(1)), m.group(2)
    smooth = redaction(None, style)
    half = path_of(smooth, "½")
    rsb = smooth["hmtx"][smooth.getBestCmap()[0xBD]][0] - half.bounds[2]
    least = max(grid, rsb // grid * grid) if grid else rsb - 1
    bounds, stood = _bounds(path), _bounds(path, slope(smooth))
    texts = [f"{a}/{b}" for a in range(100) for b in range(100)] + INKED
    out = []
    for text in texts:
        gids, advances = shape(path, text, {"frac": True})
        x, left, right, lean, last = 0, math.inf, -math.inf, -math.inf, 0
        for gid, advance in zip(gids, advances):
            if box := bounds[gid]:
                left, right = min(left, x + box[0]), max(right, x + box[2])
                # along the slant: the furthest of its ink, and the last digit's
                lean, last = max(lean, x + stood[gid][2]), x + stood[gid][2]
                end = x + box[2]
            x += advance
        if stood is not bounds:  # the last digit's ink, and what leans past it
            right = end + max(0, lean - last - 1)
        if left < 0 or right > x - least:
            out.append(f"{text} ({left:g} to {right:g} of {x})")
    if out:
        return [f"{path.name}: frac sets {len(out)} fractions past their ink: {', '.join(out[:5])}"]
    return []


@functools.cache
def _bounds(path, slant=0):
    """{glyph id: (xMin, yMin, xMax, yMax) or None} of the font at `path`,
    stood up from `slant` (run over rise), if any."""
    if not slant:
        return _bounds_upright(path)
    font = TTFont(path)
    gs, out = font.getGlyphSet(), {}
    for gid, name in enumerate(font.getGlyphOrder()):
        pen = BoundsPen(gs)
        gs[name].draw(TransformPen(pen, (1, 0, -slant, 1, 0, 0)))
        out[gid] = pen.bounds
    return out


@functools.cache
def _bounds_upright(path):
    font = TTFont(path)
    gs, out = font.getGlyphSet(), {}
    for gid, name in enumerate(font.getGlyphOrder()):
        pen = BoundsPen(gs)
        gs[name].draw(pen)
        out[gid] = pen.bounds
    return out


def path_of(font, char):
    """The outline of `char` in `font`, a pathops.Path."""
    p = pathops.Path()
    font.getGlyphSet()[font.getBestCmap()[ord(char)]].draw(pathops.PathPen(p))
    return p


def _grown(p, d):
    """The outline `p` grown by `d` all round."""
    q = pathops.Path(p)
    q.stroke(2 * d, pathops.LineCap.ROUND_CAP, pathops.LineJoin.ROUND_JOIN, 4)
    q.convertConicsToQuads(0.01)
    return pathops.op(q, p, pathops.PathOp.UNION)


def widths(cps):
    """[(feature, text, what it becomes)] of every width form among the
    code points `cps`, from Unicode's decompositions alone: <wide> and
    <narrow> forms and what they are of, both ways (`hwid` and `pwid` turn
    fullwidth Latin into ASCII, there being no halfwidth Latin); voiced kana
    split into halfwidth kana and a halfwidth sound mark by `hwid`, joined
    by `fwid`; and NOTO_WIDTHS."""
    marks = {"\u3099": "\u309b", "\u309a": "\u309c"}  # combining: spacing
    out, half = [], {}
    for cp in sorted(cps):
        kind, *of = unicodedata.decomposition(chr(cp)).split() or [""]
        if kind not in ("<wide>", "<narrow>") or len(of) != 1:
            continue
        c, of = chr(cp), chr(int(of[0], 16))
        of = marks.get(of, of)
        if ord(of) not in cps:
            continue
        if kind == "<wide>":
            out += [("fwid", of, c), ("hwid", c, of), ("pwid", c, of)]
        else:
            out += [("fwid", c, of), ("hwid", of, c)]
            half.setdefault(of, c)
    for combining, spacing in marks.items():
        if spacing in half and ord(combining) in cps:
            half[combining] = half[spacing]
    for cp in sorted(cps):
        parts = unicodedata.decomposition(chr(cp)).split()
        if len(parts) == 2 and parts[0][0] != "<":
            halves = "".join(half.get(chr(int(c, 16)), "") for c in parts)
            if len(halves) == 2:
                out += [("hwid", chr(cp), halves), ("fwid", halves, chr(cp))]
    for feature, pairs in NOTO_WIDTHS.items():
        out += [(feature, a, b) for a, b in pairs.items() if ord(a) in cps and ord(b) in cps]
    return list(dict.fromkeys(out))


def check_widths(path, font):
    """`fwid`, `hwid` and `pwid` turn every width form there is into the
    other (widths): into the glyph of that character, or, where Noto Serif
    JP has one of its own, which stays first (its halfwidth and
    proportional punctuation), into that, a glyph of no character, wider
    with `fwid` and narrower with the others."""
    cmap, hmtx, order = font.getBestCmap(), font["hmtx"], font.getGlyphOrder()
    unencoded, out = set(order) - set(cmap.values()), []
    for feature, text, expected in widths(set(cmap)):
        got = shape(path, text, {feature: True}, "ja")[0]
        want = [font.getGlyphID(cmap[ord(c)]) for c in expected]
        if got == want:
            continue
        if len(text) == len(got) == len(want) == 1:
            new, typed = hmtx[order[got[0]]][0], hmtx[cmap[ord(text)]][0]
            if order[got[0]] in unencoded and (new > typed if feature == "fwid" else new < typed):
                continue
        out.append(f"{feature} {text}→{expected}")
    if out:
        return [f"{path.name}: width forms not swapped: {' '.join(out[:30])} ({len(out)})"]
    return []


def check_style(path, font):
    """The style of each font is one, everywhere: its family, style, full
    and PostScript names, in English and Japanese; OS/2's weight and
    fsSelection (italic, bold, regular: one of them), head's macStyle, and
    the italic angle, slanted in Italic only."""
    m = re.match(r"Kuronuri(\d+)-(\w+)", path.stem)
    grid, style = int(m.group(1)) or None, m.group(2)
    st = STYLES[style]
    bold, italic = st["weight"] == 700, st["italic"]
    problems, name = [], font["name"]
    for lang, family in ((0x409, family_name(grid)), (0x411, family_name(grid, FAMILY_JA))):
        full = family if style == "Regular" else f"{family} {style}"
        for nid, want in ((1, family), (2, style), (4, full)):
            got = name.getName(nid, 3, 1, lang)
            if got is None or got.toUnicode() != want:
                problems.append(f"{path.name}: name {nid} ({lang:#x}) is {got}, not {want}")
    if name.getDebugName(6) != path.stem:
        problems.append(f"{path.name}: PostScript name is {name.getDebugName(6)}")
    for nid in (16, 17):  # typographic family and style: none, or the same
        if name.getName(nid, 3, 1, 0x409) is not None:
            problems.append(f"{path.name}: has name {nid}, which may disagree with 1 and 2")
    os2, head, post = font["OS/2"], font["head"], font["post"]
    selection = (0x20 if bold else 0) | (0x01 if italic else 0) or 0x40
    if os2.fsSelection & 0x61 != selection:
        problems.append(f"{path.name}: fsSelection {os2.fsSelection:#x} is not {style}")
    if head.macStyle & 0x3 != (1 if bold else 0) | (2 if italic else 0):
        problems.append(f"{path.name}: macStyle {head.macStyle:#x} is not {style}")
    if os2.usWeightClass != st["weight"]:
        problems.append(f"{path.name}: weight {os2.usWeightClass} is not {style}'s")
    if (post.italicAngle != 0) != italic or (font["hhea"].caretSlopeRun != 0) != italic:
        problems.append(f"{path.name}: italic angle {post.italicAngle} is not {style}'s")
    return problems


def check_beside(path, font):
    """No fraction (BESIDE) touches what is set before it (BEFORE) or after
    it (AFTER), with `frac`, nor does one of a digit or two (CLASSED) touch a
    glyph of each class the font positions fractions beside: their ink half
    a unit apart at least, so neither overlapping nor meeting at an edge or
    a corner, and on a grid a cell apart, pixels touching at a corner
    reading as one."""
    grid = int(re.match(r"Kuronuri(\d+)", path.stem).group(1))
    out = []
    before, after = classed(font)
    texts = [(c + f, 0) for f in BESIDE for c in BEFORE]
    texts += [(f + c, -1) for f in BESIDE for c in AFTER]
    texts += [(c + f, 0) for f in CLASSED for c in before]
    texts += [(f + c, -1) for f in CLASSED for c in after]
    for text, i in dict.fromkeys(texts):
        if touches(path, font, text, i, grid):
            out.append(text)
    if out:
        return [
            f"{path.name}: frac sets {len(out)} fractions touching a neighbour: "
            + " ".join(out[:40])
        ]
    return []


def touches(path, font, text, i, grid, features=None):
    """Whether glyph `i` of `text`, shaped with `frac` (and `features`),
    comes nearer the others than half a unit, a cell on a grid."""
    parts = ink(path, font, text, {"frac": True, **(features or {})}, apart=True)
    rest = pathops.Path()
    for j, p in enumerate(parts):
        if j != i % len(parts):
            rest.addPath(p)
    near = max(grid - 0.5, 0.5)

    def meet(a, b):  # their ink overlaps, or `b` is within `near` of `a`'s outline
        if abs(pathops.op(a, b, pathops.PathOp.INTERSECTION).area) > 1e-6:
            return True
        band = pathops.Path(a)
        band.stroke(2 * near, pathops.LineCap.ROUND_CAP, pathops.LineJoin.ROUND_JOIN, 4)
        band.convertConicsToQuads(0.01)
        return abs(pathops.op(band, b, pathops.PathOp.INTERSECTION).area) > 1e-6

    # pathops fails on some outlines: the other way round, or simplified
    tries = ((parts[i], rest), (rest, parts[i]))
    for a, b in tries + tuple((pathops.simplify(a), pathops.simplify(b)) for a, b in tries):
        try:
            return meet(a, b)
        except pathops.PathOpsError:
            continue
    raise pathops.PathOpsError(f"cannot measure {text} in {path.name}")


def classed(font):
    """A character of each class of glyphs the font positions fractions
    beside, before them and after: the classes of the contextual and pair
    positionings `frac` has, the first character of each typed, those of the
    glyphs before the fraction (backtrack, first of pairs) and after it
    (lookahead); not digits or slashes, which would make it another run."""
    gpos, cmap = font["GPOS"].table, font.getBestCmap()
    char = {}
    for cp, name in sorted(cmap.items()):
        if chr(cp) not in DIGITS + "/⁄":
            char.setdefault(name, chr(cp))
    lookups = {
        i
        for r in gpos.FeatureList.FeatureRecord
        if r.FeatureTag == "frac"
        for i in r.Feature.LookupListIndex
    }
    before, after = defaultdict(set), defaultdict(set)
    for i in sorted(lookups):
        for st in gpos.LookupList.Lookup[i].SubTable:
            st = getattr(st, "ExtSubTable", st)
            if isinstance(st, ot.ChainContextPos) and st.Format == 2:
                for side, defs in ((before, st.BacktrackClassDef), (after, st.LookAheadClassDef)):
                    for name, k in defs.classDefs.items():
                        side[i, id(defs), k].add(name)
            elif isinstance(st, ot.ChainContextPos) and st.Format == 3:
                # by coverage: the glyphs next to the fraction are one class
                for side, covers in ((before, st.BacktrackCoverage), (after, st.LookAheadCoverage)):
                    if covers:
                        side[i, id(st), 0].update(covers[0].glyphs)
            elif isinstance(st, ot.PairPos) and st.Format == 2:
                for name in st.Coverage.glyphs:
                    before[i, "pair", st.ClassDef1.classDefs.get(name, 0)].add(name)
    return tuple(
        sorted(
            {
                min(char[n] for n in names if n in char)
                for names in side.values()
                if names & set(char)
            }
        )
        for side in (before, after)
    )


def positions(path, text, features=None, direction=None):
    """Glyph ids and (x advance, y advance) of `text` shaped with HarfBuzz."""
    font = hb_font(path)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    if direction:
        buf.direction = direction
    hb.shape(font, buf, features or {})
    return [
        (i.codepoint, p.x_advance, p.y_advance)
        for i, p in zip(buf.glyph_infos, buf.glyph_positions)
    ]


def check_vertical(path, font):
    """In vertical text, `frac` sets a fraction there is a glyph for (⅓ ½
    ⅒ ↉) as that glyph, with / or ⁄, and those there are not (VERTICAL) as
    typed, as without it."""
    problems, cmap = [], font.getBestCmap()
    drawn = {**figures.FRACTIONS, **figures.REDACTION}
    for cp, (n, d) in drawn.items():
        if not (n + d).isdigit() or not d:
            continue
        one = positions(path, chr(cp), None, "ttb")
        for slash in "/⁄":
            if positions(path, f"{n}{slash}{d}", {"frac": True}, "ttb") != one:
                problems.append(f"{path.name}: {n}{slash}{d} is not {chr(cp)} in vertical text")
        if positions(path, f"{n}⁄{d}", None, "ttb") != one:
            problems.append(f"{path.name}: {n}⁄{d} is not {chr(cp)} in vertical text, typed")
    for text in VERTICAL:
        typed = [(font.getGlyphID(cmap[ord(c)]), 0, 0) for c in text]
        got = positions(path, text, {"frac": True}, "ttb")
        if [(g, x, 0) for g, x, _ in got] != typed or len({y for *_, y in got}) != 1:
            problems.append(f"{path.name}: {text} is not as typed in vertical text, with frac")
    return problems


def check_alone(path, font):
    """`numr`, `sups`, `dnom`, `subs` and `sinf` alone give the digits the
    forms they gave before `frac` set fractions of parts of their own:
    superscripts (typed ⁰ ¹ ⁹), as wide and drawn alike; superscripts as
    wide, drawn alike, on the baseline as the denominators of ½; and
    subscripts (₀ ₉)."""
    problems, gs, order = [], font.getGlyphSet(), font.getGlyphOrder()
    sups, subs = "⁰¹²³⁴⁵⁶⁷⁸⁹", "₀₁₂₃₄₅₆₇₈₉"

    def outline(gid):
        p = pathops.Path()
        gs[order[gid]].draw(pathops.PathPen(p, glyphSet=gs))
        return p

    def moved(p, to):  # `p` moved to the bottom left of `to`
        x, y = to.bounds[0] - p.bounds[0], to.bounds[1] - p.bounds[1]
        return p.transform(1, 0, 0, 1, x, y)

    den = {d: shape(path, f"1/{d}", {"frac": True})[0][2] for d in DIGITS}
    forms = (("numr", sups), ("sups", sups), ("dnom", sups), ("subs", subs), ("sinf", subs))
    for feature, typed in forms:
        gids, advances = shape(path, DIGITS, {feature: True})
        expected, widths = shape(path, typed)
        if advances != widths:
            problems.append(f"{path.name}: {feature} sets digits {advances}, not {widths}")
        for d, got, want in zip(DIGITS, gids, expected):
            a, b = outline(got), outline(want)
            if feature == "dnom" and a.bounds[1] != outline(den[d]).bounds[1]:
                problems.append(f"{path.name}: dnom {d} does not stand as fractions' do")
            if abs(pathops.op(a, moved(b, a), pathops.PathOp.XOR).area) > 1:
                problems.append(f"{path.name}: {feature} draws {d} unlike {order[want]}")
    return problems


# Small digits, how each form sets two of them: text, the features on, and
# which of the glyphs shaped are the two
SMALL = {
    "sups": (lambda a, b: chr(SUPS[a]) + chr(SUPS[b]), {}, 0),
    "subs": (lambda a, b: chr(0x2080 + int(a)) + chr(0x2080 + int(b)), {}, 0),
    "numr": (lambda a, b: a + b, {"numr": True}, 0),
    "dnom": (lambda a, b: a + b, {"dnom": True}, 0),
    "frac numr": (lambda a, b: f"{a}{b}/1", {"frac": True}, 0),
    "frac dnom": (lambda a, b: f"1/{a}{b}", {"frac": True}, 2),
}
SUPS = {d: cp for d, cp in zip(DIGITS, (0x2070, 0xB9, 0xB2, 0xB3, *range(0x2074, 0x207A)))}
# How far the proportion of a pair of small digits to the full-size pair
# may stray past the least and most of MCKL's ¹ ² ³ (check_small)
STRAY = 0.25
# Letters a subscript comes near, before it (what hangs below them, moved
# back along the slant in italic) or after it (hanging back under it), and
# the forms that give subscripts (check_small)
LETTERED = ("gğyjpqçxuQ", "jf")
SUBSCRIPTS = {
    "typed": (lambda d: chr(0x2080 + int(d)), {}),
    "subs": (lambda d: d, {"subs": True}),
    "sinf": (lambda d: d, {"sinf": True}),
}


def _gap(path, font, text, features, i):
    """How far apart the ink of glyphs `i` and `i` + 1 of `text` shaped is:
    -1 if they overlap."""
    parts = ink(path, font, text, features, apart=True)
    a, b = parts[i], parts[i + 1]
    try:
        if not figures._apart(a, b, 0):
            return -1
        return figures._distance(a, b)
    except pathops.PathOpsError:  # growing one fails at times: the other, mirrored
        a, b = (q.transform(-1, 0, 0, 1, 0, 0) for q in (a, b))
        return figures._distance(b, a)


def small_gaps(path, font):
    """{form: {pair: gap}} of every pair of digits, small as each form of
    SMALL sets them, and full size ("full"), and MCKL's ¹ ² ³ ("own")."""
    out = {
        form: {a + b: _gap(path, font, text(a, b), features, i) for a in DIGITS for b in DIGITS}
        for form, (text, features, i) in SMALL.items()
    }
    pairs = [a + b for a in DIGITS for b in DIGITS]
    out["full"] = {p: _gap(path, font, p, {"kern": False}, 0) for p in pairs}  # as spaced
    out["own"] = {
        a + b: _gap(path, font, chr(SUPS[a]) + chr(SUPS[b]), {}, 0) for a in "123" for b in "123"
    }
    return out


def check_small(path, font):
    """Small digits that are not MCKL's (⁰ ⁴ to ⁹, and every subscript,
    numerator and denominator) are set as he sets ¹ ² ³: no two of them,
    superscripts, subscripts, `numr`, `dnom`, or the parts of `frac`, nearer
    than MCKL sets any two of ¹ ² ³; on a grid, the parts of `frac` a cell
    apart at least, the others not over each other (MCKL's touch there);
    on a grid, each pair of denominators of `frac` as far apart as its
    numerators, and of subscripts as its superscripts below COARSE, placed
    each on its own from there up (_placed); and, but on a grid, each
    pair in proportion to the same digits full size, spaced as typed (no
    kerning), shrunk as tall as ¹, as his are, within STRAY of the least and
    most of his. And in Italic, a subscript, typed, `subs` or `sinf`, as far
    from a letter before or after it that comes near it (LETTERED, g₂ ₂j) as
    two of them, a cell on a grid, not over it from COARSE up (_lettered)."""
    m = re.match(r"Kuronuri(\d+)-(\w+)", path.stem)
    grid, style = int(m.group(1)), m.group(2)
    gaps, problems = small_gaps(path, font), []
    for form in SMALL:
        least = (
            (grid if form.startswith("frac") else 0)
            if grid
            else figures._gap(redaction(None, style))
        )
        near = {p: g for p, g in gaps[form].items() if g < 0 or g < least - 0.5}
        if near:
            shown = " ".join(f"{p}:{g:g}" for p, g in list(near.items())[:6])
            how = f"nearer than {least}" if least else "overlapping"
            problems.append(f"{path.name}: {form} sets {len(near)} pairs {how}: {shown}")
    if style == "Italic":
        need = (
            (grid if grid < figures.COARSE else 0) if grid else figures._gap(redaction(None, style))
        )
        problems += _lettered(path, font, need)
    if grid:
        coarse = grid >= figures.COARSE
        for form, as_ in (("frac dnom", "frac numr"), *(() if coarse else (("subs", "sups"),))):
            off = {
                p: (g, gaps[as_][p]) for p, g in gaps[form].items() if abs(g - gaps[as_][p]) > 0.5
            }
            if off:
                shown = " ".join(f"{p}:{g:g}/{h:g}" for p, (g, h) in list(off.items())[:6])
                problems.append(
                    f"{path.name}: {form} sets {len(off)} pairs apart unlike {as_}: {shown}"
                )
        return problems + (_placed(path, font, grid, gaps) if coarse else [])
    cmap, scale = font.getBestCmap(), []
    for c in "1¹":
        g = font["glyf"][cmap[ord(c)]]
        g.recalcBounds(font["glyf"])
        scale.append(g.yMax - g.yMin)
    scale = scale[1] / scale[0]
    own = [g / (gaps["full"][p] * scale) for p, g in gaps["own"].items()]
    lo, hi = min(own) - STRAY, max(own) + STRAY
    for form in SMALL:
        off = {
            p: r
            for p, g in gaps[form].items()
            if not lo <= (r := g / (gaps["full"][p] * scale)) <= hi
        }
        if off:
            shown = " ".join(f"{p}:{r:.2f}" for p, r in list(off.items())[:6])
            problems.append(
                f"{path.name}: {form} sets {len(off)} pairs out of MCKL's proportion "
                f"{lo:.2f} to {hi:.2f}: {shown}"
            )
    return problems


def _placed(path, font, grid, gaps):
    """From COARSE up, each subscript as figures.add_glyphs places it on its
    own: its ink starting at its origin, back along the slant, or where its
    superscript's does, upright; its advance its superscript's, or its ink
    and ¹'s right bearing if that is more; and no pair of them more than
    two cells farther apart than the same superscripts (Italic ₇₃ on 70:
    ⁷'s ink passes its advance by two cells, ₇ moved back past them)."""
    cmap, glyf, hmtx, problems = font.getBestCmap(), font["glyf"], font["hmtx"], []

    def ink_x(name):
        glyf[name].recalcBounds(glyf)
        return glyf[name].xMin, glyf[name].xMax

    right = hmtx[cmap[0xB9]][0] - ink_x(cmap[0xB9])[1]
    for d in DIGITS:
        sub, sup = cmap[0x2080 + int(d)], cmap[SUPS[d]]
        start, end = ink_x(sub)
        if start not in (0, ink_x(sup)[0]):
            problems.append(f"{path.name}: {sub} starts at {start:g}, not its origin")
        want = max(hmtx[sup][0], pixel.snap(end + right, grid))
        if hmtx[sub][0] != want:
            problems.append(f"{path.name}: {sub} advance {hmtx[sub][0]}, not {want}")
    far = {
        p: (g, gaps["sups"][p])
        for p, g in gaps["subs"].items()
        if g > gaps["sups"][p] + 2 * grid + 0.5
    }
    if far:
        shown = " ".join(f"{p}:{g:g}/{h:g}" for p, (g, h) in list(far.items())[:6])
        problems.append(
            f"{path.name}: subs sets {len(far)} pairs two cells farther than sups: {shown}"
        )
    return problems


def _lettered(path, font, need):
    """Pairs of a subscript and a letter of LETTERED nearer than `need`."""
    near = []
    for letters, after in zip(LETTERED, (False, True)):
        for form, (sub, features) in SUBSCRIPTS.items():
            for c in letters:
                for d in DIGITS:
                    pair = (sub(d), c) if after else (c, sub(d))
                    a, b = ink(path, font, "".join(pair), features, apart=True)
                    if not figures._apart(a, b, need):
                        near.append(f"{form} {d + c if after else c + d}")
    if not near:
        return []
    return [
        f"{path.name}: {len(near)} subscripts nearer a letter than {need}: {' '.join(near[:6])}"
    ]


def check_shared_lookups(path, font):
    """`frac` positions fractions with lookups `kern` uses too, the same
    ones, and they apply once: fractions set alike with `kern` on and off,
    and with `frac` on them only."""
    problems, gpos = [], font["GPOS"].table
    records = gpos.FeatureList.FeatureRecord
    for rec in gpos.ScriptList.ScriptRecord:
        ls = rec.Script.DefaultLangSys
        if ls is None:
            continue
        frac = {
            i
            for f in ls.FeatureIndex
            if records[f].FeatureTag == "frac"
            for i in records[f].Feature.LookupListIndex
        }
        kern = {
            i
            for f in ls.FeatureIndex
            if records[f].FeatureTag == "kern"
            for i in records[f].Feature.LookupListIndex
        }
        if not frac or not frac <= kern:
            problems.append(f"{path.name}: {rec.ScriptTag} kern lacks frac's positioning")
    for text in ("1/2", "11/12", "T1/2", "n1/3n", "1/1回", "489/603"):
        on = positions(path, text, {"frac": True})
        if positions(path, text, {"frac": True, "kern": False}) != on:
            problems.append(f"{path.name}: {text} is set otherwise with kern off")
        ranged = positions(path, f"x {text} y", {"frac": [(2, 2 + len(text), True)]})
        if ranged[2 : 2 + len(on)] != on:
            problems.append(f"{path.name}: {text} is set otherwise with frac on it only")
    for text in RANGED:
        whole = placed(path, text, {"frac": True})
        at = re.search(r"\d+/\d+", text).span()
        typed = text.replace("/", "⁄")
        for t, features in (
            (text, {"frac": [(*at, True)]}),
            (text, {"frac": [(*at, True)], "kern": False}),
            (typed, {}),
            (typed, {"kern": False}),
        ):
            if placed(path, t, features) != whole:
                problems.append(f"{path.name}: {t} is set otherwise with {features}")
    return problems


def ink(path, font, text, features=None, apart=False):
    """The outline of `text` as shaped, a pathops.Path, the glyphs moved where
    `frac` and its kerning put them, or a list of them, `apart`."""
    gs, order, out, whole = font.getGlyphSet(), font.getGlyphOrder(), [], pathops.Path()
    for gid, x, y in placed(path, text, features):
        p = pathops.Path()
        for pen in (pathops.PathPen(p, glyphSet=gs), pathops.PathPen(whole, glyphSet=gs)):
            gs[order[gid]].draw(TransformPen(pen, (1, 0, 0, 1, x, y)))
        out.append(p)
    return out if apart else pathops.simplify(whole)


def placed(path, text, features=None, language=None):
    """Glyph ids of `text` shaped with HarfBuzz, and where each is drawn,
    (x, y), its offsets included."""
    font = hb_font(path)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    if language:
        buf.language = language
    hb.shape(font, buf, features or {})
    out, x = [], 0
    for i, p in zip(buf.glyph_infos, buf.glyph_positions):
        out.append((i.codepoint, x + p.x_offset, p.y_offset))
        x += p.x_advance
    return out


def check_review():
    """The fonts /review sets text in (.tmp/review/fonts/text, review.py)
    shape REVIEWED as the built fonts of the same name: the outline of
    every glyph, its advances and offsets, across and down, with each
    feature the page offers on, kern off, and ss01. Every built font has
    one, and every one review.json lists is there: without .tmp/review at
    all, as in CI (CI set), there is nothing to check."""
    root = ROOT / ".tmp" / "review"
    text, listing = root / "fonts" / "text", root / "review.json"
    if not listing.exists():
        return [] if os.environ.get("CI") else ["no /review fonts in .tmp/review: run review.py"]
    review, problems = json.loads(listing.read_text()), []
    listed = {f["name"] for f in review["fonts"]}
    for built in sorted((DIST / "ttf").glob("*.ttf")):
        if built.stem not in listed or not (text / built.name).exists():
            problems.append(f"{built.name}: /review has no text font of it, run review.py")
    for name in sorted(listed):
        if not (text / f"{name}.ttf").exists():
            problems.append(f"{name}: review.json lists it, .tmp/review has no text font")
    features = [{}, {"kern": False}, {"ss01": True}]
    features += [{f: True} for f in review.get("features", [])]
    for font in sorted(text.glob("*.ttf")):
        built = DIST / "ttf" / font.name
        if not built.exists():
            continue
        for t in REVIEWED:
            for f in features:
                for lang, direction in ((None, None), ("ja", None), ("ja", "ttb")):
                    if _shaped(font, t, f, lang, direction) != _shaped(
                        built, t, f, lang, direction
                    ):
                        problems.append(
                            f"{font.name}: /review sets {t!r} with {f} {direction or ''} otherwise"
                        )
    return problems


def _shaped(path, text, features, language, direction=None):
    font = hb_font(path)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    if language:
        buf.language = language
    if direction:
        buf.direction = direction
    hb.shape(font, buf, features)
    return [
        (_drawn(path, i.codepoint), p.x_advance, p.y_advance, p.x_offset, p.y_offset)
        for i, p in zip(buf.glyph_infos, buf.glyph_positions)
    ]


@functools.cache
def _drawn(path, gid):
    """A hash of the outline of glyph `gid` of the font at `path`, decomposed."""
    font = _font(path)
    pen = DecomposingRecordingPen(font.getGlyphSet())
    font.getGlyphSet()[font.getGlyphOrder()[gid]].draw(pen)
    return hash(repr(pen.value))


@functools.cache
def _font(path):
    return TTFont(path)


def check_shared(path, font):
    """Every feature of glyphs.SHARED is in every script and language system
    of the font, and as DFLT's (`kern`, Noto Serif JP's too); and shapes
    Japanese text (JAPANESE)."""
    problems = []
    for tag, features in glyphs.SHARED.items():
        table = font[tag].table
        records = table.FeatureList.FeatureRecord

        systems = {}
        for rec in table.ScriptList.ScriptRecord:
            systems[rec.ScriptTag, "dflt"] = rec.Script.DefaultLangSys
            for lrec in rec.Script.LangSysRecord:
                systems[rec.ScriptTag, lrec.LangSysTag] = lrec.LangSys
        dflt = _lookups(records, systems["DFLT", "dflt"])
        for (script_tag, lang), ls in systems.items():
            have = _lookups(records, ls)
            missing = sorted(f for f in features if f in dflt and not dflt[f] <= have[f])
            if missing:
                problems.append(f"{path.name}: {script_tag} {lang} lacks {' '.join(missing)}")
    for feature, text, language in JAPANESE:
        if shape(path, text, {feature: True}, language) == shape(path, text, None, language):
            problems.append(f"{path.name}: {feature} does nothing to {text} in Japanese")
    latin, japanese = shape(path, "1/2", {"frac": True}), shape(path, "日1/2", {"frac": True}, "ja")
    if japanese[0][1:] != latin[0] or japanese[1][1:] != latin[1]:
        problems.append(f"{path.name}: frac sets 1/2 otherwise in Japanese text")
    return problems


def _lookups(records, ls):
    """{feature tag: lookup indices} of the language system `ls`."""
    out = defaultdict(set)
    for i in ls.FeatureIndex:
        out[records[i].FeatureTag] |= set(records[i].Feature.LookupListIndex)
    return out


def check_cells(path, font, grid):
    """Glyphs drawn by hand on `grid`, cell by cell, are so in the font, of
    its style: enclosed ones (enclosed.by_cells), arrows and their alts
    (arrows.CELLS), or the alts as their own cells ("↗.ss01"), Italic's as
    they stand, integrals, ∆ and ∇ (maths.CELLS), Greek letters
    (greek.CELLS), and kanji and kana (pixel.JAPANESE), with the vertical
    forms of the kana on pixel.FOLLOW."""
    style = path.stem.split("-")[1]
    gs, cmap, problems = font.getGlyphSet(), font.getBestCmap(), []
    names = {}
    for (g, s, char), rows in enclosed.by_cells().items():
        names[g, s, cmap[ord(char)]] = char, rows
    by_hand = drawn_cells(arrows.CELLS)
    for (g, s, char), rows in by_hand.items():
        base, _, own = char.partition(".")
        alt = font.getGlyphName(shape(path, base, {"ss01": True})[0][0])
        apart = (g, s, f"{base}.ss01") in by_hand  # its alt has its own cells
        for name in [alt] if own else [cmap[ord(base)]] + [alt] * (not apart):
            names[g, s, name] = char, rows
    for name in (maths.CELLS, greek.CELLS):
        for (g, s, char), rows in drawn_cells(name).items():
            if name == greek.CELLS and ord(char) == greek.DELTA and greek.letterlike():
                continue  # Δ is ∆'s glyph then, maths.py's cells
            names[g, s, cmap[ord(char)]] = char, rows
    down = verticals(font)
    for (g, s, char), rows in drawn_cells(pixel.JAPANESE).items():
        names[g, s, cmap[ord(char)]] = char, rows
        if g >= pixel.FOLLOW and (vertical := down.get(cmap[ord(char)])):
            names[g, s, vertical] = f"{char}, vertical", rows
    for (g, s, char), rows in drawn_cells(figures.CELLS).items():
        names[g, s, cmap[ord(char)]] = char, rows
    for (g, s, name), (char, rows) in names.items():
        if (g, s) != (grid, style):
            continue
        p = pathops.Path()
        gs[name].draw(pathops.PathPen(p, glyphSet=gs))
        x0, y0, x1, y1 = p.bounds
        cells = [
            "".join(
                "#" if p.contains((x0 + (c + 0.5) * grid, y1 - (r + 0.5) * grid)) else "."
                for c in range(round((x1 - x0) / grid))
            )
            for r in range(round((y1 - y0) / grid))
        ]
        if cells != _trimmed(rows):
            problems.append(f"{path.name}: {name} ({char}) is not as drawn cell by cell")
        # Greek letters say the row their bottom row of cells is: there, not only so shaped
        if len(char) == 1 and ord(char) in greek.DRAWN and rows.at:
            under = next(i for i, r in enumerate(reversed(rows)) if "#" in r)
            if round(y0 / grid) != rows.at[1] + under:
                problems.append(f"{path.name}: {name} ({char}) is not on the row it is drawn on")
    return problems


def check_greek_font(path, font, source, grid, style):
    """The Greek letters of greek.py in a font of `style` on `grid` (0
    without), `source` Redaction's: each stands between the side bearings
    its outline says (Δ, A's), on a grid as far from those of MCKL's pixel
    letters of the same sides as drawn (greek.fitted), or more, by whole
    cells, for a comma, a period or a figure (check_greek_alone); each straight stem
    (greek.STEMS) is as thick as that of the letter it is drawn from, to 4
    units (a slanted stem carried on is not to the unit), or as many cells on a grid
    (slanted, a stem is not as thick on every row: under a cell off); and
    the ohm sign is the glyph of Ω. On a grid, every row of a stem has it,
    as thick, over the row under it (Italic's leans: within a cell). Δ is
    the shape of ∆ when that is the letter. And they are kerned, apart,
    not over a comma without kerning and as pictured (check_greek_kerning,
    check_greek_apart, check_greek_alone, check_greek_pictures); Italic's
    μ and ρ stand as u and p do (check_greek_stood)."""
    cmap, glyf, hmtx, problems = font.getBestCmap(), font["glyf"], font["hmtx"], []
    if cmap.get(greek.OHM) != cmap.get(0x03A9):
        problems.append(f"{path.name}: the ohm sign is not the glyph of Ω")
    if greek.letterlike() and greek.DELTA in cmap and greek.INCREMENT in cmap:
        a, b = (_outline(font, cmap[cp]) for cp in (greek.DELTA, greek.INCREMENT))
        same = pathops.op(a, b.transform(1, 0, 0, 1, a.bounds[0] - b.bounds[0], 0), XOR)
        if abs(same.area) > 1:
            problems.append(f"{path.name}: Δ is not the shape of ∆")
    smooth, theirs = redaction(None, style), source.getBestCmap()
    more = {}  # what each has over the side bearings it is drawn between
    for cp in greek.DRAWN:
        if cp not in cmap:
            continue  # reported as missing
        glyph = glyf[cmap[cp]]
        glyph.recalcBounds(glyf)
        sides = glyph.xMin, hmtx[cmap[cp]][0] - glyph.xMax
        drawn_sides = greek.fitted(source, smooth, cp, grid)
        more[cmap[cp]] = tuple(a - b for a, b in zip(sides, drawn_sides))
        if min(more[cmap[cp]]) < 0 or any(m % (grid or 1) for m in more[cmap[cp]]):
            problems.append(
                f"{path.name}: {chr(cp)} stands between {sides}, not {drawn_sides} as drawn or more"
            )
    for cp, (_, as_letter) in greek.TURNED.items():  # between that letter's side bearings
        glyph, letter = glyf[cmap[cp]], source["glyf"][theirs[ord(as_letter)]]
        glyph.recalcBounds(glyf)
        letter.recalcBounds(source["glyf"])
        right = source["hmtx"][theirs[ord(as_letter)]][0] - letter.xMax
        more[cmap[cp]] = glyph.xMin - letter.xMin, hmtx[cmap[cp]][0] - glyph.xMax - right
    problems += check_greek_kerning(path, font, style, more)
    problems += check_greek_apart(path, font, style)
    problems += check_greek_alone(path, font, more)
    problems += check_greek_pictures(path, font, style)
    if style == "Italic":
        problems += check_greek_stood(path, font, grid)
    for char, stems in greek.stems(style).items():
        for band, run, letter, their_band, their_run in stems:
            if grid:
                a = greek.stem_cells(glyf[cmap[ord(char)]], grid, band, run)
                mckl = source["glyf"][theirs[ord(letter)]]
                b = greek.stem_cells(mckl, grid, their_band, their_run)
                off = a is None or b is None or abs(a - b) >= 1
                rows = ROWS.get((char, band), band)
                if broken := _broken(glyf[cmap[ord(char)]], grid, rows, run, style == "Italic"):
                    problems.append(f"{path.name}: a stem of {char} is broken at {broken}")
            else:
                a = _stem(font, char, band, run)
                b = _stem(source, letter, their_band, their_run)
                off = a is None or b is None or abs(a - b) > 4
            if off:
                problems.append(
                    f"{path.name}: a stem of {char} is {a} thick, not {b} as that of {letter}"
                )
    return problems


# Where a stem is straight and alone, when not all its band, {(character,
# band): heights}: κ's is cut for the top of ı, π's legs end as t does, Ψ's
# arms and stem run into its cup, ψ's has a ledge under its bowl
ROWS = {("κ", (60, 260)): (60, 190), ("π", greek.XH): (150, 330)}
ROWS |= {("Ψ", (480, 620)): (510, 620), ("Ψ", (120, 220)): (120, 200)}
ROWS |= {("ψ", greek.DESC): (-160, -45)}  # a ledge in its stem, under its bowl


def _broken(glyph, grid, band, run, leaning):
    """Where the stroke `run` of pixel `glyph` is not one stem between the
    heights of `band`: the heights of the rows where no run of cells has
    all the columns the stem has on most rows (wider is a serif, a bar or
    a join). `leaning`, Italic's: where none is as thick but for a cell,
    and over the stem on the row above but for a cell."""
    on, (_, top), _ = cells(glyph, grid)
    rows = {}
    for i, row in enumerate(on):
        y = (top - i - 0.5) * grid
        if band[0] <= y <= band[1]:
            edges = np.flatnonzero(np.diff(np.concatenate([[0], row.astype(int), [0]])))
            rows[y] = list(zip(edges[::2].tolist(), edges[1::2].tolist()))
    found = [s[run] for s in rows.values() if len(s) > max(run, -run - 1)]
    if not found:
        return []
    thick = int(np.median([b - a for a, b in found]))
    most = max(set(found), key=found.count)
    broken, last = [], None
    for y, spans in rows.items():
        if leaning:
            over = [s for s in spans if s[1] - s[0] >= thick - 1]
            if last:
                over = [s for s in over if min(s[1], last[1]) - max(s[0], last[0]) >= thick - 1]
            near = most if last is None else last
            last = min(over, key=lambda s: abs(s[0] - near[0]), default=None) or last
        else:
            over = [s for s in spans if s[0] <= most[0] and s[1] >= most[1]]
        if not over:
            broken.append(y)
    return broken


def check_greek_stood(path, font, grid):
    """Italic's μ and ρ where the letters they stand as are, as set, whatever
    side bearings their outlines say. μ is u where u is: as wide, on a grid
    to a cell (to NEAR units on 10: pixelated, it is not u's cells), and its
    body, the upper half of the x-height (BODY), as far from its origin as
    u's, to NEAR units, on a grid to a cell: its descender alone reaches
    under the letter before it. As wide as u and its descender (184 units
    more, as it was), it stands a third of an em from that letter. Without
    a grid, ρ's bowl at MID is as far from its origin as p's stem, to NEAR
    units."""
    cmap, reach, problems = font.getBestCmap(), greek.Reach(font, grid or None), []
    step = grid or 1

    def left(char, low, high):
        rows = slice((low - greek.LOW) // step, max((high - greek.LOW) // step, 1))
        return float(reach[cmap[ord(char)]][0][rows].min())

    if all(ord(c) in cmap for c in "μu"):
        wide = [font["hmtx"][cmap[ord(c)]][0] for c in "μu"]
        if abs(wide[0] - wide[1]) > (max(grid, NEAR) if grid else 0):
            problems.append(f"{path.name}: μ is {wide[0]} wide, not {wide[1]} as u")
        body = [left(c, *BODY) for c in "μu"]
        if abs(body[0] - body[1]) > (grid or NEAR):
            problems.append(
                f"{path.name}: μ's body is {body[0]:.0f} from its origin, not {body[1]:.0f} as u's"
            )
    if not grid and all(ord(c) in cmap for c in "ρp"):
        bowl, stem = (left(c, MID, MID + 1) for c in "ρp")
        if abs(bowl - stem) > NEAR:
            problems.append(
                f"{path.name}: ρ's bowl is {bowl:.0f} from its origin, not {stem:.0f} as p's stem"
            )
    return problems


# Greek letters and the others kerning is compared with
KERNED_WITH = "AOTVYWaoevtxyn.,-ΑΤΥΟΛΓΔαουωνκφ"
XOR, AND = pathops.PathOp.XOR, pathops.PathOp.INTERSECTION
PICTURES = Path(__file__).resolve().parent / "greek-cells.json"


def _outline(font, name):
    """The outline of glyph `name` of `font`, its components too, where a
    rasterizer sets it: by its left side bearing, not always where the
    outline starts in Redaction's Italic (the glyph set moves a glyph of
    contours so, not one of components, nor a component: greek.shift).
    As HarfBuzz draws it."""
    glyphs, glyph = font.getGlyphSet(), font["glyf"][name]
    pen = DecomposingRecordingPen(glyphs)
    glyphs[name].draw(pen)
    p = pathops.Path()
    pen.replay(pathops.PathPen(p))
    if glyph.isComposite():
        p = p.transform(1, 0, 0, 1, greek.shift(font["glyf"], font["hmtx"], name), 0)
    return p


class Set:
    """Glyphs of a font, to set two side by side and see if they meet:
    their outlines, their cells on a grid, kept."""

    def __init__(self, font, grid):
        self.font, self.grid, self.hmtx = font, grid, font["hmtx"]
        self.outlines, self.inked, self.reach = {}, {}, greek.Reach(font, grid)

    def outline(self, name):
        if name not in self.outlines:
            p = _outline(self.font, name)
            self.outlines[name] = p, (p.bounds if p.contours else None)
        return self.outlines[name]

    def cells(self, name):
        """The cells of pixel glyph `name`: {(column, row)}."""
        if name not in self.inked:
            g, crossed, cells = self.grid, defaultdict(list), set()
            for contour in self.outline(name)[0].contours:
                pts = [(round(x), round(y)) for x, y in contour.points]
                for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
                    if x0 == x1:
                        for row in range(min(y0, y1) // g, max(y0, y1) // g):
                            crossed[row].append((x0 // g, 1 if y1 > y0 else -1))
            for row, edges in crossed.items():
                inside, edges = 0, sorted(edges)
                for (a, turn), (b, _) in zip(edges, edges[1:]):
                    inside += turn
                    if inside:
                        cells.update((column, row) for column in range(a, b))
            self.inked[name] = cells
        return self.inked[name]


OVERLAP, EDGE, TOUCH = 3, 2, 1  # how two glyphs meet


def meet(first, a, second, b, dx):
    """How glyph `b` of the Set `second`, set `dx` after the origin of glyph
    `a` of the Set `first`, meets it: OVERLAP if one is over the other
    (they share a cell, or ink); else on a grid EDGE if a cell of one is
    beside or above a cell of the other, TOUCH if two meet at a corner
    only; without a grid TOUCH if their outlines touch anywhere; else 0."""
    (p, pb), (q, qb) = first.outline(a), second.outline(b)
    pad = first.grid or 1
    if not pb or not qb or pb[2] + pad < qb[0] + dx or qb[2] + dx + pad < pb[0]:
        return 0
    if pb[3] + pad < qb[1] or qb[3] + pad < pb[1]:
        return 0
    if grid := first.grid:
        mine, shift = first.cells(a), round(dx / grid)
        theirs = {(column + shift, row) for column, row in second.cells(b)}
        if mine & theirs:
            return OVERLAP
        sides = ((-1, 0), (1, 0), (0, -1), (0, 1))
        if mine & {(c + i, r + j) for c, r in theirs for i, j in sides}:
            return EDGE
        around = {(c + i, r + j) for c, r in theirs for i in (-1, 1) for j in (-1, 1)}
        return TOUCH if mine & around else 0
    q = q.transform(1, 0, 0, 1, dx, 0)
    if abs(pathops.op(p, q, AND).area) > 1e-5:
        return OVERLAP
    halo = pathops.Path(q)
    halo.stroke(0.02, pathops.LineCap.BUTT_CAP, pathops.LineJoin.ROUND_JOIN, 4)
    halo.convertConicsToQuads()
    return TOUCH if abs(pathops.op(halo, p, AND).area) > 1e-7 else 0


MET = {TOUCH: "touch", EDGE: "share an edge", OVERLAP: "overlap"}


def over(first, a, second, b, dx):
    """How much glyph `b` set `dx` after `a` meets it (meet), to compare two
    pairs of one font: 0 if they are clear, 0.5 if they touch, an edge or
    a corner, else 1 and how far one reaches over the other, across."""
    if (how := meet(first, a, second, b, dx)) < OVERLAP:
        return min(how, 1) / 2
    return 1 + max(0, round(-first.reach.gap(a, b, dx - first.hmtx[a][0])))


def fused(glyphs, a, b, dx, refs, never=False):
    """Whether glyph `b` set `dx` after `a` is nearer than a pair of a run
    may be: one over the other; or, on a grid, sharing an edge, when a pair
    of Redaction's letters they stand as (`refs`: (first, second, how far
    after it) for greek.like and for greek.edged) does not, an edge of
    theirs, not one over the other; or when it `never` may (greek.UNFUSED).
    How (MET), else 0."""
    how = meet(glyphs, a, glyphs, b, dx)
    shared = all(meet(glyphs, x, glyphs, y, d) == EDGE for x, y, d in refs)
    if how == OVERLAP or (how == EDGE and (never or not shared)):
        return how
    return 0


def rows(glyphs, a, b, dx):
    """On a grid, the rows on which glyph `b`, set `dx` after the origin of
    `a`, meets it: a cell of one beside a cell of the other, or over it, and
    both rows of two cells one above the other."""
    mine, shift, found = glyphs.cells(a), round(dx / glyphs.grid), set()
    for column, row in glyphs.cells(b):
        c = column + shift
        if mine & {(c - 1, row), (c, row), (c + 1, row)}:
            found.add(row)
        found.update(r for j in (-1, 1) if (c, row + j) in mine for r in (row, row + j))
    return found


def unlike(glyphs, style, a, b, dx):
    """On a grid, whether glyph `b`, set `dx` after `a`, one of them a letter
    of greek.ROWED (μ, χ), meets it on a row where the letter of Redaction
    that one stands as (greek.like: u, x) would not meet the other, set in
    its place: its advance where that one's ends when it comes first, from
    its origin when it comes second. By its descender, its hook or its leg,
    which u and x have not."""
    cmap, hmtx = glyphs.font.getBestCmap(), glyphs.hmtx
    rowed = {cmap[cp]: cp for cp in greek.ROWED if cp in cmap}
    if not glyphs.grid or not {a, b} & set(rowed):
        return False
    c = cmap[ord(greek.like(rowed[a], style)[1])] if a in rowed else a
    d = cmap[ord(greek.like(rowed[b], style)[0])] if b in rowed else b
    return not rows(glyphs, a, b, dx) <= rows(glyphs, c, d, dx - hmtx[a][0] + hmtx[c][0])


def stood_as(path, font, style, pair):
    """For fused, of a pair of a run: the pairs of Redaction's letters it
    stands as (greek.like, greek.edged), as kerned, and whether it may
    never share an edge."""
    order, refs = font.getGlyphOrder(), []
    for how in (greek.like, greek.edged):
        theirs = "".join(_like(font, style, c, how)[1 - i] for i, c in enumerate(pair))
        ids, advances = shape(path, theirs, {"kern": True})
        if len(ids) == 2:
            refs.append((order[ids[0]], order[ids[1]], advances[0]))
    return refs, tuple(map(ord, pair)) in greek.UNFUSED


def _kerning(path, pair):
    """How far kerning moves the second character of `pair`."""
    return sum(shape(path, pair, {"kern": True})[1]) - sum(shape(path, pair, {"kern": False})[1])


def check_greek_kerning(path, font, style, more):
    """Each letter of greek.KERNED is kerned as the letter of Redaction it
    stands for, before and after every character of KERNED_WITH (a Greek
    one there as the letter it stands for): the same value, so none where
    MCKL has none; the letters not in it (β, χ, Ω...) are not kerned with
    them, but as greek.PAIRS says. That is from the side bearings they are
    drawn between: in a run of Greek, what they have over those (`more`,
    {name: (left, right)}) is kerned back. A pair of a run is further apart
    only if it would be fused so (fused), and then by the least that is
    not: a cell on a grid, the least that clears it and greek.AIR units
    without one. Beside a Latin letter, only if it would meet it more than
    Redaction's does, and by no more than that takes. Or, of a run or not,
    if a letter of greek.ROWED would meet it on a row where its letter
    would not (unlike)."""
    cmap, problems = font.getBestCmap(), []
    grid = grid_of(path)
    kerned = greek.KERNED | (greek.ITALIC_KERNED if style == "Italic" else {})
    apart, run, glyphs = greek.PAIRS[style], greek.within(font), Set(font, grid)
    step, order = grid or 1, font.getGlyphOrder()
    for cp in [*greek.SAME, *greek.TURNED, *greek.DRAWN]:
        first, second = kerned.get(cp, (None, None))
        for other in KERNED_WITH:
            if cp not in cmap or ord(other) not in cmap:
                continue
            theirs = kerned.get(ord(other), (other, other) if ord(other) < 0x370 else (None, None))
            for pair, latin in (
                (chr(cp) + other, first and theirs[1] and first + theirs[1]),
                (other + chr(cp), second and theirs[0] and theirs[0] + second),
            ):
                a, b = (cmap[ord(c)] for c in pair)
                want = _kerning(path, latin) if latin else 0
                if tuple(pair) in apart:
                    want = -(-apart[tuple(pair)] // step) * step
                if (a in run and b in run) or tuple(pair) in apart:
                    want -= more.get(a, (0, 0))[1] + more.get(b, (0, 0))[0]
                got = _kerning(path, pair)
                if got == want:
                    continue
                together, advance = a in run and b in run, font["hmtx"][a][0]
                how = greek.edged if together else greek.like
                theirs_ = _like(font, style, pair[0], how)[1] + _like(font, style, pair[1], how)[0]
                ids, advances = shape(path, theirs_, {"kern": True})
                ref = order[ids[0]], order[ids[1]]
                if together:  # fused as kerned, and a step nearer than it is
                    back = got - (step if grid else greek.AIR + 1)
                    refs, never = stood_as(path, font, style, pair)
                    fine = got > want and all(
                        fused(glyphs, a, b, advance + v, refs, never)
                        or unlike(glyphs, style, a, b, advance + v)
                        for v in (want, back)
                    )
                else:  # meets it more than Redaction's as kerned, and a step nearer
                    as_is = over(glyphs, ref[0], glyphs, ref[1], advances[0] - (0 if grid else 1))
                    near, back = advance - (0 if grid else 1), got - step if grid else want - 1

                    def nearer(v, a=a, b=b, near=near, as_is=as_is):
                        more = over(glyphs, a, glyphs, b, near + v) > as_is
                        return more or unlike(glyphs, style, a, b, near + v)

                    fine = got > want and nearer(want) and (back < want or nearer(back))
                if not fine:
                    problems.append(f"{path.name}: {pair} is kerned {got}, not {want} ({latin})")
    return problems


def grid_of(path):
    """The grid of a font file named Kuronuri<grid>-<style>."""
    return int(re.search(r"(\d+)-", path.name).group(1))


def _like(font, style, char, how=greek.like):
    """The letters of Redaction `char` stands as, left and right, if it is a
    Greek letter of greek.py, else itself: `how` is greek.like, or
    greek.edged for the edges a pair may share."""
    cp = font.getBestCmap()[ord(char)] == font.getBestCmap().get(greek.OHM) and 0x03A9 or ord(char)
    known = cp in greek.CODEPOINTS or cp in greek.OTHERS
    return how(cp, style) if known else char * 2


def check_greek_apart(path, font, style):
    """With kerning, as HarfBuzz sets them. Within a run: no Greek letter is
    over another, or any character a shaper sets in its run (greek.within:
    figures, marks, brackets, the slash and backslash, the underscore,
    superscripts), before or after it; and on a grid no cell of one is
    beside or above a cell of the other, unless the pair of Redaction's
    letters they stand as (greek.edged), kerned, has such an edge, and is
    not one over the other (fused). Cells that meet at a corner may:
    slanted letters of pixels do everywhere. Across runs: nor does it meet
    a Latin letter, capitals and accented ones too, more than the letter
    of Redaction it stands as meets that one, kerned: Redaction's own
    letters touch on a grid, and a few overlap. And μ and χ (greek.ROWED)
    meet a neighbour, of their run or Latin, only on the rows where the
    letter they stand as would, in their place (unlike)."""
    cmap, problems = font.getBestCmap(), []
    glyphs, order = Set(font, grid_of(path)), font.getGlyphOrder()
    run = greek.within(font)
    letters = [chr(cp) for cp in [*greek.OTHERS, *greek.SAME, *greek.TURNED, *greek.DRAWN]]
    latin = [chr(cp) for cp in cmap if script(cp) == "Latn" and chr(cp).isalpha()]
    latin = [c for c in latin if cmap[ord(c)] not in run]

    def set_(pair):
        ids, advances = shape(path, pair, {"kern": True})
        return (order[ids[0]], order[ids[1]], advances[0]) if len(ids) == 2 else None

    def met(pair, how=meet):
        placed = set_(pair)
        return how(glyphs, placed[0], glyphs, placed[1], placed[2]) if placed else 0

    found = defaultdict(list)
    for letter in letters:
        if ord(letter) not in cmap:
            continue
        for other in dict.fromkeys([*letters, *run.values()]):
            pairs = [letter + other] if other in letters else [letter + other, other + letter]
            for pair in pairs:
                ours = set_(pair)
                if ours and (how := fused(glyphs, *ours, *stood_as(path, font, style, pair))):
                    found[MET[how]].append(pair)
                if ours and unlike(glyphs, style, *ours):
                    found["meet on a row the letter it stands as would not"].append(pair)
        left, right = _like(font, style, letter)
        for other in latin:
            for pair, theirs in ((letter + other, right + other), (other + letter, other + left)):
                if (how := met(pair)) and met(pair, over) > met(theirs, over):
                    found[f"{MET[how]}, more than Redaction's"].append(pair)
                if (ours := set_(pair)) and unlike(glyphs, style, *ours):
                    found["meet on a row the letter it stands as would not"].append(pair)
    for how, pairs in found.items():
        problems.append(f"{path.name}: {len(pairs)} pairs {how}, kerned: {' '.join(pairs[:12])}")
    return problems


def check_greek_alone(path, font, more):
    """Without kerning: no Greek letter drawn is over a comma, a period or a
    figure (greek.CLEARED) set before or after it; and none has more than
    the side bearings it is drawn between, those of the Latin letter of
    that side (`more`, {name: (left, right)} over them), but the least
    that takes: with a unit less, on a grid a cell, it would be over one."""
    cmap, hmtx, problems = font.getBestCmap(), font["hmtx"], []
    grid = grid_of(path)
    glyphs, step = Set(font, grid), grid or 1
    for cp in [*greek.TURNED, *greek.DRAWN]:
        name, needed = cmap[cp], [False, False]
        for mark in greek.CLEARED:
            it = cmap[ord(mark)]
            for side, (a, b) in enumerate(((it, name), (name, it))):
                dx = hmtx[a][0]
                if meet(glyphs, a, glyphs, b, dx) == OVERLAP:
                    pair = mark + chr(cp) if side == 0 else chr(cp) + mark
                    problems.append(f"{path.name}: {pair} overlap, unkerned")
                if meet(glyphs, a, glyphs, b, dx - step) == OVERLAP:
                    needed[side] = True
        for side in (0, 1):
            if more.get(name, (0, 0))[side] and not needed[side]:
                problems.append(
                    f"{path.name}: {chr(cp)} has more than the side bearing it is drawn"
                    f" between, side {side}, and no comma, period or figure takes it"
                )
    return problems


def pictures(font, style, grid):
    """The cells of each Greek letter of greek.py in `font`, on `grid`, as
    text: {character: "row its bottom row is on" and its rows, top down}."""
    cmap, glyphs, out = font.getBestCmap(), Set(font, grid), {}
    for cp in [*greek.TURNED, *greek.DRAWN]:
        cells = glyphs.cells(cmap[cp])
        columns, rows = [c for c, _ in cells], [r for _, r in cells]
        out[chr(cp)] = [str(min(rows))] + [
            "".join("#" if (c, r) in cells else "." for c in range(min(columns), max(columns) + 1))
            for r in range(max(rows), min(rows) - 1, -1)
        ]
    return out


def check_greek_pictures(path, font, style):
    """On a grid, every Greek letter drawn is, cell for cell and on its row,
    as pictured (PICTURES, written by `check.py --pictures` once looked
    at): the letters pixelated, not drawn cell by cell, too, whose serifs
    and joins nothing else holds. A cell lost or gained fails."""
    grid = grid_of(path)
    if not grid:
        return []
    stored = json.loads(PICTURES.read_text()).get(path.stem, {}) if PICTURES.exists() else {}
    problems = []
    for char, rows in pictures(font, style, grid).items():
        if (wanted := stored.get(char)) is None:
            problems.append(f"{path.name}: {char} has no picture in {PICTURES.name}")
        elif unpacked(wanted) != rows:
            off = sum(a != b for a, b in zip(unpacked(wanted), rows))
            problems.append(f"{path.name}: {char} is not as pictured ({off} rows differ)")
    return problems


def packed(rows):
    """Rows of cells, each as runs: "3.5#2." is three of air, five of ink..."""
    return [rows[0]] + [
        "".join(f"{len(m.group())}{m.group()[0]}" for m in re.finditer(r"#+|\.+", row))
        for row in rows[1:]
    ]


def unpacked(rows):
    return [rows[0]] + [
        "".join(c * int(n) for n, c in re.findall(r"(\d+)([#.])", row)) for row in rows[1:]
    ]


def write_pictures(fonts):
    """Write PICTURES from `fonts` (paths of pixel fonts)."""
    out = {}
    for file in fonts:
        if grid := grid_of(file):
            found = pictures(TTFont(file), file.stem.split("-")[1], grid)
            out[file.stem] = {c: packed(rows) for c, rows in found.items()}
    PICTURES.write_text(json.dumps(out, ensure_ascii=False, indent=0) + "\n")


def _stem(font, char, band, run, p=None):
    """How thick the stroke `run` of `char` in `font` (or of outline `p`) is,
    across, halfway up `band`: None without one."""
    found = runs(p or path(font, char), y=sum(band) / 2)
    return found[run][1] - found[run][0] if len(found) > max(run, -run - 1) else None


def _trimmed(rows):
    """Cells `rows` without rows and columns of air around them."""
    full = [i for i, r in enumerate(rows) if "#" in r]
    used = [c for c in range(len(rows[0])) if any(r[c] == "#" for r in rows)]
    return [r[used[0] : used[-1] + 1] for r in rows[full[0] : full[-1] + 1]]


def check_drawn(path, font):
    """The glyphs drawn from Redaction's are made of them, where they should be."""
    g = int(re.match(r"Kuronuri(\d+)-", path.name).group(1)) or 1
    em = snap_advance(1000, g)
    cmap, hmtx, gs = font.getBestCmap(), font["hmtx"], font.getGlyphSet()

    def bounds(cp):
        pen = BoundsPen(gs)
        gs[cmap[cp]].draw(pen)
        return tuple(round(v, 3) for v in pen.bounds)

    problems = []
    for cp, c in fullwidth.SOURCES.items():
        dx = snap((em - hmtx[cmap[ord(c)]][0]) / 2, g)
        x0, y0, x1, y1 = bounds(ord(c))
        moved = tuple(round(v, 3) for v in (x0 + dx, y0, x1 + dx, y1))
        if hmtx[cmap[cp]][0] != em or bounds(cp) != moved:
            problems.append(f"{path.name}: {chr(cp)} is not {c} centred in the em")
    for cp, letters in (numerals.SOURCES | punctuation.SOURCES | enclosed.TYPED).items():
        if [hmtx[cmap[cp]][0]] != [snap(sum(shape(path, letters, {"liga": False})[1]), g)]:
            problems.append(f"{path.name}: {chr(cp)} is not as wide as {letters}")
    # Raised ones (🅪) are as high as ™, not centred up and down
    raised = {
        cp for kind, contents, _, _ in enclosed.ENCLOSURES if kind == "raised" for cp in contents
    }
    for cp in enclosed.ENCLOSED:
        x0, y0, x1, y1 = bounds(cp)
        if (
            hmtx[cmap[cp]][0] != em
            or abs(x0 + x1 - em) > g
            or (cp not in raised and abs(y0 + y1 - 2 * enclosed.CENTRE) > 2 * g)
            or (g > 1 and (x0 < g or x1 > em - g))
        ):
            problems.append(f"{path.name}: {chr(cp)} is not centred in the em box")
    if g != 100:
        order, glyf = font.getGlyphOrder(), font["glyf"]
        letters = {"c": glyf[cmap[0x2105]].components[0].glyphName}
        for text in SUPERIORS:
            for c, i in zip(text[1:], shape(path, text, {"ordn": True})[0][1:]):
                letters[c] = order[i]
        drawn = defaultdict(list)
        for c, name in sorted(letters.items()):
            coords, ends, _ = glyf[name].getCoordinates(glyf)
            x0, y0 = min(x for x, _ in coords), min(y for _, y in coords)
            drawn[tuple((x - x0, y - y0) for x, y in coords), tuple(ends)].append(c)
        for alike in (cs for cs in drawn.values() if len(cs) > 1):
            problems.append(f"{path.name}: superscript {' '.join(alike)} are drawn alike")
    return problems


class _Flat(BasePen):
    """The edges of an outline, its curves cut in STEPS lines, per contour."""

    STEPS = 8

    def __init__(self):
        super().__init__(None)
        self.contours = []

    def _moveTo(self, pt):
        self.contours.append([pt])

    def _lineTo(self, pt):
        self.contours[-1].append(pt)

    def _qCurveToOne(self, a, b):
        p0 = self._getCurrentPoint()
        for i in range(1, self.STEPS + 1):
            t = i / self.STEPS
            self.contours[-1].append(
                tuple((1 - t) ** 2 * p0[k] + 2 * (1 - t) * t * a[k] + t * t * b[k] for k in (0, 1))
            )

    def _curveToOne(self, a, b, c):
        p0 = self._getCurrentPoint()
        for i in range(1, self.STEPS + 1):
            t, u = i / self.STEPS, 1 - i / self.STEPS
            w = (u**3, 3 * u * u * t, 3 * u * t * t, t**3)
            pts = (p0, a, b, c)
            self.contours[-1].append(tuple(sum(wi * q[k] for wi, q in zip(w, pts)) for k in (0, 1)))


def crossings(p):
    """How many pairs of edges of path `p` cross, but those that meet."""
    flat = _Flat()
    p.draw(flat)
    edges = np.array(
        [(*a, *b) for c in flat.contours for a, b in zip(c, c[1:] + c[:1]) if a != b], float
    )
    x0, y0, x1, y1 = edges.T

    def side(px, py, ax, ay, bx, by):
        return (bx - ax) * (py[:, None] - ay) - (by - ay) * (px[:, None] - ax)

    d1 = side(x0, y0, x0[None], y0[None], x1[None], y1[None]).T
    d2 = side(x1, y1, x0[None], y0[None], x1[None], y1[None]).T
    d3, d4 = d1.T, d2.T
    crossed = (d1 * d2 < 0) & (d3 * d4 < 0)
    return int(np.triu(crossed, 1).sum())


def check_hand():
    """Every outline drawn by hand (shapes.drawn) loads, is used, and does not
    cross itself: enclosed content (enclosed.by_hand) is content of an
    enclosure, made heavier so, with the pieces and counters of Redaction's
    glyph, and slanted content drawn for another style than Italic's (Bold's
    🄬) is used there, of Italic's glyph; 〒 is fullwidth's (check_postal);
    the owner's arrow head is arrows' (check_arrows); the operators are
    maths' (check_operators)."""
    problems = []
    used = {c for _, contents, _, _ in enclosed.ENCLOSURES for t in contents.values() for c in t}
    slanted = {
        c for _, contents, _, s in enclosed.ENCLOSURES if s for t in contents.values() for c in t
    }
    postal = chr(fullwidth.POSTAL)
    italic = redaction(None, "Italic")
    for style in STYLES:
        ufo = DRAWN / f"{style}.ufo"
        every, hand = drawn(style), enclosed.by_hand(style)
        theirs = enclosed.by_hand(style, True)
        # each glyph once, those of two code points (μ µ, Ω Ω) too
        loaded = {id(p) for p, _ in [*every.values(), *drawn(style, True).values()]}
        if ufo.exists() and len(UFOReader(ufo).getGlyphSet()) != len(loaded):
            problems.append(f"{ufo.name}: not every glyph loads, with a code point")
        font = redaction(None, style)
        for c, (p, amount) in theirs.items():
            plan = (0, enclosed._limit("Italic", c), 0, 0)
            q, route = enclosed._heavy(italic, c, plan, enclosed._of(c), style)
            k = (q.bounds[3] - q.bounds[1]) / (p.bounds[3] - p.bounds[1])
            if style == "Italic" or c not in slanted or route != "drawn":
                problems.append(f"{ufo.name}: slanted {c} is not used")
            elif abs(abs(q.area) - abs(p.area) * k * k) > 1:
                problems.append(f"{ufo.name}: slanted {c} is not the one drawn for it")
            if not amount > 0 or _pieces(p) != _pieces(path(italic, c)):
                problems.append(f"{ufo.name}: slanted {c} is not Redaction's made heavier")
            if crossed := crossings(p):
                problems.append(f"{ufo.name}: slanted {c} crosses itself ({crossed})")
        operators = {chr(cp) for cp in [*maths.OPERATORS, *letterlike.LETTERS, *greek.DRAWN]}
        for c in sorted(set(every) - set(hand) - {postal} - set(arrows.SOURCES) - operators):
            problems.append(f"{ufo.name}: {c} is not used")
        for c, (p, amount) in hand.items():
            plan = (0, enclosed._limit(style, c), 0, 0)
            if c not in used or enclosed._heavy(font, c, plan, enclosed._of(c))[1] != "drawn":
                problems.append(f"{ufo.name}: {c} is not used")
            if not amount > 0 or _pieces(p) != _pieces(path(font, c)):
                problems.append(f"{ufo.name}: {c} is not Redaction's made heavier")
        for c, (p, _) in every.items():
            if c in arrows.SOURCES:  # as SVGs are filled, by their winding: → twists at its notch
                p = pathops.simplify(p, clockwise=True)
            if crossed := crossings(p):
                problems.append(f"{ufo.name}: {c} crosses itself ({crossed})")
        if postal in every:
            problems += [f"{ufo.name}: 〒 {p}" for p in check_postal(font, every[postal][0])]
        if any(c in every for c in arrows.SOURCES):
            problems += [f"{ufo.name}: {p}" for p in check_arrows(font, every)]
        problems += [f"{ufo.name}: {p}" for p in check_operators(font, every)]
        problems += [f"{ufo.name}: {p}" for p in check_letters(font, every)]
        problems += [f"{ufo.name}: {p}" for p in check_greek(font, every)]
    return problems


# Farthest Italic's enclosed lowercase is grown across in checks: more than
# any enclosure grows it (y, 7.2), or as far as it goes (w, 7.75)
ACROSS = 8
# Least of each gap of its carving it keeps so: grown as far as enclosures
# grow it, all of it but k (0.90), y (0.94), v and x (0.96), where a curve
# or an edge that slants less leaves the wall of a slit
OPEN = 0.85
# Longest edge of a cut of an enclosed letter, as shipped (k's flat, 23), and
# most it is longer or shorter than before the letter grew, a point is from
# where the letter grown has it, or a counter is wider or narrower: the
# rounding of two ends, of a point to a corner of its unit
CUT, ROUNDED = 30, 1.5
# Most degrees a join of two lines that was smooth turns on whole units,
# and no more than SMOOTH more than it did: only a corner moved would
# straighten it (Italic's l's flag, a line of 120 units then 9: 2.2° for 1.6°)
KINK = 3


def check_grown():
    """Italic's lowercase grown across (enclosed._grown_across), every
    letter, as far as ACROSS: its outline has the segments it had before, each of as many
    points, so no notch of its carving comes out in steps (swept and cut
    again, m had 101 points for 57); it does not cross itself, keeps its
    height, and each gap of its carving (shapes.grooves) is as open as it
    was, moved across, to OPEN. And content is grown on GROWN and the
    smooth font only, its letters that blend blended further there
    (enclosed._fuller): on 50, 70 and 100 it is as its limit alone makes
    it (enclosed._plan)."""
    problems = []
    font = redaction(None, "Italic")
    n = stem(path(font, "n"))
    for c in enclosed.LOWER:
        # At a size it would be grown at: as small as half, heavier than it goes
        plans = {
            grid: enclosed._plan(font, c, 0.5, 0.5, 0, n, False, grid)[0]
            for grid in (None, 10, 20, 35, 50, 70, 100)
        }
        plain = enclosed._plan(font, c, 0.5, 0.5, 0, n, False, None, False)[0]
        for grid, plan in plans.items():
            if (plan != plain) != (not grid or grid in enclosed.GROWN):
                problems.append(f"Italic {c}: on {grid or 0}, {plan} for {plain} not grown")
        if enclosed._heavy(font, c, plans[None], "n")[1] == "blended":
            if not plans[None][0] > plain[0] or plans[None][3]:
                problems.append(f"Italic {c}: blended {plans[None]} for {plain} not grown")
            continue
        p, _, _ = enclosed._drawn(font, c, plans[None], "n")
        q = enclosed._grown_across(p, ACROSS, c)
        if q is p or abs(q.area) < abs(broadened(p, ACROSS - 1).area):
            problems.append(f"Italic {c}: not grown across by {ACROSS}, or near")
            continue
        was = [[(op, len(args)) for _, op, args in contour] for contour in _contours(p)]
        now = [[(op, len(args)) for _, op, args in contour] for contour in _contours(q)]
        if was != now:
            points = [sum(k for contour in cs for _, k in contour) for cs in (was, now)]
            problems.append(f"Italic {c}: grown across, {points[1]} points for {points[0]}")
        if crossed := crossings(q):
            problems.append(f"Italic {c}: grown across, it crosses itself ({crossed})")
        if abs(p.bounds[1] - q.bounds[1]) > 0.01 or abs(p.bounds[3] - q.bounds[3]) > 0.01:
            problems.append(f"Italic {c}: grown across, it is not as tall")
        for gap, _ in grooves(p):
            # As open somewhere it may have moved to: no farther than it grew
            left = min(
                abs(
                    pathops.op(
                        gap.transform(1, 0, 0, 1, d / 4, 0), q, pathops.PathOp.INTERSECTION
                    ).area
                )
                for d in range(-4 * ACROSS, 4 * ACROSS + 1)
            )
            if left > (1 - OPEN) * abs(gap.area):
                x, y = gap.bounds[:2]
                problems.append(
                    f"Italic {c}: grown across, its carving at {x:.0f},{y:.0f} closes by "
                    f"{left / abs(gap.area):.0%}"
                )
    return problems


def _joins(g):
    """Of each point of glyph `g`, by contour: whether it is on the curve,
    the degrees its outline turns there, between it and the points before
    and after it, left above 0 (into its ink: glyphs wind clockwise), how
    long those two edges are, and where it is."""
    out, start = [], 0
    for end in g.endPtsOfContours:
        pts = list(g.coordinates[start : end + 1])
        on = [f & 1 for f in g.flags[start : end + 1]]
        start, contour = end + 1, []
        for i, q in enumerate(pts):
            a, b = pts[i - 1], pts[(i + 1) % len(pts)]
            u, v = (q[0] - a[0], q[1] - a[1]), (b[0] - q[0], b[1] - q[1])
            turn = math.degrees(math.atan2(u[0] * v[1] - u[1] * v[0], u[0] * v[0] + u[1] * v[1]))
            contour.append((on[i], turn, math.hypot(*u), math.hypot(*v), tuple(q)))
        out.append(contour)
    return out


def _smooth(turn, before, after):
    """Whether a join that turns `turn` degrees is smooth (SMOOTH), to a
    unit of rounding across each of its edges, `before` and `after` long,
    and no corner (CORNER)."""
    rounding = math.atan(1 / max(before, 1)) + math.atan(1 / max(after, 1))
    return abs(turn) <= min(SMOOTH + math.degrees(rounding), CORNER)


def _cuts(contour):
    """The points of a contour (_joins) a cut starts at: an edge no longer
    than CUT between two corners (CORNER), one of them into its ink: the
    flat and the wall of a terminal's cut, where e's bar meets its bowl,
    the floor of a slit."""
    out = []
    for i, (on, turn, _, far, _) in enumerate(contour):
        on2, turn2, *_ = contour[(i + 1) % len(contour)]
        cut = on and on2 and far <= CUT and min(abs(turn), abs(turn2)) >= CORNER
        if cut and max(turn, turn2) > 0:
            out.append(i)
    return out


def _as_grown(was, grown, now, across):
    """What is not right of a letter in the smooth font, `now`, a glyph as
    shipped, against `was`, as stored before it grew, and `grown`, the
    letter grown as it is drawn, stored without its joins smoothed
    (shapes.rounded): check_shipped. Grown `across`, not blended further,
    it has the points of `was`."""
    same = [list(g.endPtsOfContours) == list(now.endPtsOfContours) for g in (was, grown)]
    same = [
        s and [f & 1 for f in g.flags] == [f & 1 for f in now.flags]
        for s, g in zip(same, (was, grown))
    ]
    if across and not same[0]:
        return ["has not the points it had before it grew"]
    if not same[1]:
        return ["has not the points of the letter grown"]
    problems = []
    ja, jr, jb = _joins(was), _joins(grown), _joins(now)
    if len(ja) != len(jb) or any(
        sum(p[0] for p in a) != sum(p[0] for p in b) for a, b in zip(ja, jb)
    ):
        return ["has not the points on the curve it had before it grew"]
    for k, (ca, cr, cb) in enumerate(zip(ja, jr, jb)):
        # A point where growth puts it, to its rounding
        for i, (r, b) in enumerate(zip(cr, cb)):
            if (far := math.dist(r[4], b[4])) > ROUNDED:
                problems.append(f"has point {i} of contour {k} {far:.1f} from where it is grown")
        # Its points on the curve, in turn, are those it had: a join smooth then is smooth
        ons = [[i for i, p in enumerate(c) if p[0]] for c in (ca, cb)]
        for i0, i in zip(*ons):
            (_, t0, *edges0, _), (_, t1, *edges1, _) = ca[i0], cb[i]
            lines = cb[i - 1][0] and cb[(i + 1) % len(cb)][0]
            most = min(abs(t0) + SMOOTH, KINK) if lines else SMOOTH
            kinked = abs(t0) <= SMOOTH and abs(t1) > most
            if kinked or (_smooth(t0, *edges0) and not _smooth(t1, *edges1)):
                problems.append(
                    f"turns {abs(t1):.1f}° at point {i} of contour {k}, "
                    f"smooth before it grew ({abs(t0):.1f}°)"
                )
        for i in _cuts(ca) if across else ():
            if abs(cb[i][3] - ca[i][3]) > ROUNDED:
                problems.append(
                    f"has a cut {cb[i][3]:.1f} long from point {i} of "
                    f"contour {k}, for {ca[i][3]:.1f} before it grew"
                )
        # A notch as deep as growth leaves it: the edges either side of each cut
        for i in _cuts(cr):
            for j, side in ((i, 2), ((i + 1) % len(cr), 3)):
                if abs(cb[j][side] - cr[j][side]) > ROUNDED:
                    problems.append(
                        f"has a cut {cb[j][side]:.1f} deep at point {j} of "
                        f"contour {k}, for {cr[j][side]:.1f} as grown"
                    )
    # A counter as wide and as tall as growth leaves it: wound as the
    # inside of its enclosure, the second contour
    boxes = []
    for g in (grown, now):
        boxes.append([])
        start = 0
        for end in g.endPtsOfContours:
            pts = list(g.coordinates[start : end + 1])
            area = sum(a[0] * b[1] - a[1] * b[0] for a, b in zip(pts, pts[1:] + pts[:1]))
            xs, ys = [x for x, _ in pts], [y for _, y in pts]
            boxes[-1].append((area, max(xs) - min(xs), max(ys) - min(ys)))
            start = end + 1
    for k, (r, b) in enumerate(zip(*boxes)):
        if (
            k > 1
            and r[0] * boxes[0][1][0] > 0
            and max(abs(r[1] - b[1]), abs(r[2] - b[2])) > ROUNDED
        ):
            problems.append(
                f"has a counter {b[1]:.0f} by {b[2]:.0f}, contour {k}, for "
                f"{r[1]:.0f} by {r[2]:.0f} as grown"
            )
    return problems


def _as_before(was, now, grid, drawn):
    """What does not read of a letter on a grid, `now`, a glyph as shipped,
    as `was`, the same before it grew, in its enclosure: check_shipped
    (enclosed._reads, `drawn`: the counters it has drawn, in its
    enclosure)."""
    (pieces, n, corners, _), (pieces0, n0, corners0, _) = (
        enclosed._census(g, grid) for g in (now, was)
    )
    problems = []
    if pieces != pieces0:
        problems.append(f"is in {pieces} pieces for {pieces0}")
    if not min(n0, drawn) <= n <= n0:
        problems.append(f"closes {n} counters for {n0}, {drawn} drawn")
    if corners > corners0:
        problems.append(f"touches at a corner in {corners} places for {corners0}")
    if (pinched := enclosed._pinched(now)) > (pinched0 := enclosed._pinched(was)):
        problems.append(f"has its outline pass a point again in {pinched} places for {pinched0}")
    if not problems and not enclosed._reads(now, was, grid, drawn):
        problems.append("closes a counter where it had none")
    return problems


def check_shipped():
    """Italic's enclosed lowercase and 🆥, every one, as shipped, against
    the same drawn as before it grew (enclosed._enclosed, not grown), which
    is as approved, and against it grown, as drawn (_as_grown, _as_before).

    In the smooth font, each point is where the letter grown has it, to
    its rounding (ROUNDED), so each counter is as wide and as tall, to
    ROUNDED, and each notch as deep: the edges either side of each cut, an
    edge no longer than CUT between two corners (CORNER), one of them into
    its ink (_cuts), are as long, to ROUNDED: a notch's floor three units
    deeper, a counter pinched to a fifth, passed. Its points on the curve
    are those it had before it grew, in turn, and each join among them
    that was smooth (SMOOTH) is: on whole units, moving its points broke
    Italic's i's foot by 20°, blending g further made a point of 11° of
    its upper bowl's left; between two lines, it turns no more than KINK,
    nor SMOOTH more; and none smooth to a unit of rounding across each of
    its edges is not. A letter grown across, not blended further (MCKL's
    outlines, of other points), has its points, contour for contour, and
    each of its cuts as long as before it grew, to ROUNDED: y's tail's flat
    came out 1.4 times as long.

    On GROWN, each letter's pixels read as before it grew, pixelated as it
    was (enclosed._pixelated, _reads): in as many pieces, their counters
    those it had, none new (a slit of ⓐ's carving shut into a hole of two
    cells on 10), and none fewer but those it does not have as drawn
    (ⓡ's, shut at a corner before, open grown); and they touch at a corner
    only in no more places, by their cells (the arch of ⓗ hung off its
    stem by one on 35) and by their outline, a point passed again within
    a contour (ⓖ's ear on 20)."""
    problems = []
    smooth = redaction(None, "Italic")
    cps = [*range(0x24D0, 0x24EA), 0x1F1A5]
    for grid in (None, *enclosed.GROWN):
        file = DIST / "ttf" / f"{ps_name(grid, 'Italic')}.ttf"
        if not file.exists():
            continue
        font = TTFont(file)
        name, glyf = f"{file.name} enclosed", font["glyf"]
        em, radius, stroke, cy = enclosed._layout(smooth, grid)
        drawn, ts, redraw, grown = enclosed._enclosed(smooth, em, radius, stroke, cy, grid=grid)
        if set(cps) - grown:
            lost = "".join(chr(cp) for cp in sorted(set(cps) - grown))
            problems.append(f"{name}: {lost} not grown")
            continue
        before = {cp: (*drawn[cp][:2], redraw(cp, 0, False)) for cp in cps}
        names = {cp: font.getBestCmap()[cp] for cp in cps}
        was = {names[cp]: glyph(enclosed._put(*before[cp])) for cp in cps}
        if grid:
            eased = (ts, functools.partial(redraw, grown=False), name)
            eased = eased if grid in enclosed.EASED else None
            was = enclosed._pixelated(font, before, was, grid, eased)
        n = stem(path(smooth, "n"))
        for cp in cps:
            a, b = was[names[cp]], glyf[names[cp]]
            if grid:
                # The counters of the letter, and the air in its enclosure
                found = _as_before(a, b, grid, enclosed._counted(drawn[cp][2])[1] + 1)
            else:
                c = "d" if cp == 0x1F1A5 else enclosed.LOWER[cp - 0x24D0]
                across = enclosed._plan(smooth, c, 0.5, 0.5, 0, n, False)[0][3]
                found = _as_grown(a, glyph(enclosed._put(*drawn[cp])), b, across)
            problems += [f"{name}: {chr(cp)} {p}" for p in found]
    return problems


# Letters of letterlike.py drawn from one of Redaction's, of its Italic if so
FROM = {"Σ": ("Z", False), "Π": ("T", False), "μ": ("u", False)}
FROM |= {"ℏ": ("ħ", True)}


def check_letters(font, every):
    """The letters drawn by hand for `font`, a Redaction style (`every`, its
    glyphs drawn by hand), are all there, those drawn from one of
    Redaction's (FROM) with its pieces and counters."""
    problems = []
    italic = redaction(None, "Italic")
    for cp in letterlike.LETTERS:
        c = chr(cp)
        if c not in every:
            problems.append(f"{c} is missing")
        elif c in FROM:
            letter, of_italic = FROM[c]
            if _pieces(every[c][0]) != _pieces(path(italic if of_italic else font, letter)):
                problems.append(f"{c} has not the pieces and counters of {letter}")
    return problems


# Greek letters of greek.py with the pieces and counters of one of Redaction's
GREEK = dict(zip("ΓΨηικλνυψ", "FUnıkvvuu")) | dict(zip("ρσ", "po"))
# And of the others: a bar closes the counter of Δ, splits those of Θ θ; Ξ
# is three bars; a stem splits the counter of Φ; Ω is open, ω has none; β
# closes the bowls of ß, which are open, each into the stem: two counters
PIECES = {"Δ": (1, 1), "Θ": (1, 2), "Ξ": (3, 0), "Φ": (1, 2), "Ω": (1, 0)}
PIECES |= {"θ": (1, 2), "ω": (1, 0), "β": (1, 2)}
# Drawn, not from one letter: α's strokes cross and close its bowl; π τ are
# a bar on legs; φ's left arc is open, its right bowl closed; χ is two
# strokes that cross
PIECES |= {"α": (1, 1), "π": (1, 0), "τ": (1, 0), "φ": (1, 1), "χ": (1, 0)}


# Details of the letters drawn, in their outlines. Where a hairline crosses
# a stem (Φ Ψ φ ψ), two ledges, one on each side of the stem and at two
# heights: {character: (two heights its stem runs straight at, between two
# other strokes, the heights its ledges are between)}. A ledge is a step
# LEDGE units into the stem, for HIGH units
LEDGED = {"Φ": ((250, 450), (100, 600)), "Ψ": ((400, 550), (150, 400))}
LEDGED |= {"ψ": ((200, 400), (-80, 120)), "φ": ((100, 300), (-50, 470))}
LEDGE, HIGH = (8, 60), (8, 40)
# ρ's notch, where its bowl comes back to its stem, is d's: as deep into the
# stem, to NOTCH units, and that deep by half for NOTCHED units at least
# (d's is, for 54, Italic's on a longer slant). (Which stroke across is the
# stem, the two heights it runs straight at, the heights its notch is
# between, the side it is on); d's from over its tail, which Italic's curls
NOTCH, NOTCHED = 3, 50
NOTCHES = {"ρ": (0, (-200, -100), (0, 200), 1), "d": (0, (520, 590), (60, 250), 0)}
BAR = 1  # units the bars of π and τ may be off Π's
# Greek lowercase has no feet: a stroke ends as thick as it runs, to FOOT
# units (a leg that slants, to SLANTED: k's widens a little), from PLAIN to
# TIP units from its end (a foot that flares up from the stem, as u's, is
# widest at its tip, Bold's 27 to 45 units up) as STRAIGHT units from it.
# {character: [(which stroke across
# at its end, counted from the left or, under 0, from the right; where it
# ends: the baseline, the letter's lowest point (None) or its top)]}; in
# Italic, κ's leg ends in k's curl, λ in x's terminals and μ in the stroke
# u leaves by, not feet. Italic
# ρ's stem runs on into its bowl: its left edge is a straight line from its
# foot to RUNS, to BEND units every 10 of height.
FOOT, SLANTED, PLAIN, TIP, STRAIGHT = 4, 12, 12, 48, 130
ENDS = {"η": [(0, 0), (0, None)], "μ": [(0, None), (-1, 0)], "ρ": [(0, None)]}
ENDS |= {"φ": [(0, None)], "ψ": [(0, None)], "κ": [(0, 0), (-1, 0)], "λ": [(0, 0), (-1, 0)]}
ENDS |= {"χ": [(0, None), (-1, "top")]}
ITALIC_ENDS = {"κ": [(0, 0)], "λ": [], "μ": [(0, None)]}
RUNS, BEND = 300, 1
# χ is the Greek letter, not x set low: a fifth of its height from its top,
# and from its foot, two strokes, the thick one (THICKER times the other or
# more) on the right above and on the left below
THICKER = 1.8
# Italic α is one stroke that crosses itself: its two strokes are apart
# below and above the crossing (PARTED), one at it (CROSSED). It is a's
# bowl with two short strokes right of it: no wider than a, ink to ink, by
# more than WIDER units, its counter at FULL of the x-height as wide as
# a's there by COUNTER or more (a tilted egg with x's arms through it, as
# it was, is 131 wider, its counter 0.64 of a's)
PARTED, CROSSED = (140, 340), 240
WIDER, FULL, COUNTER = 70, 360, 0.72
# Its arm ends in a ball as x's: x's step under the stroke, straight down to
# the ball's side, STEP of x's or more (a flag with a slit of 22 units, as it
# was, is 0.61), the ball under it and right of it for BALL of the step or
# more (x's is 2.4 times its step across)
STEP, BALL = 0.8, 2
# In the fonts (check_greek_stood): Italic's μ is u where u is, its body (the
# heights of BODY, over where u's stem turns into its bowl and μ's goes on
# down) as far from its origin as u's, to NEAR units (it is 13 nearer: MCKL
# sets Italic's u 12 units right of its outline, by its side bearing); Italic's
# ρ, without a grid, has its bowl at MID as far from its origin as p's stem,
# to NEAR units (16 nearer; 46, as it was, and a letter before it is nearer
# its bowl than p's stem by a third of its side bearing)
BODY, MID, NEAR = (250, 420), 240, 20


def _edges(p, run, straight, band, step=2):
    """The stem of outline `p`, the stroke `run` across at the two heights of
    `straight`, row by row: [(height, how far in its left edge is, how far
    in its right edge)] every `step` units of `band`, from the lines its
    edges run along at those heights. Under 0 where a stroke joins it."""
    (y0, y1), found = straight, []
    lines = [runs(p, y=y)[run] for y in straight]
    for y in range(band[0], band[1] + 1, step):
        left, right = (a + (b - a) * (y - y0) / (y1 - y0) for a, b in zip(*lines))
        at = [r for r in runs(p, y=y) if r[0] < (left + right) / 2 < r[1]]
        if at:
            found.append((y, at[0][0] - left, right - at[0][1]))
    return found


def ledges(p, straight, band):
    """The ledges cut into the stem of outline `p` (LEDGED): [(side, from
    which height, to which)], side 0 its left and 1 its right. A ledge is
    LEDGE units into the stem on rows that follow each other, HIGH units of
    them, and ends in a step, the stem whole on the row after or before:
    not where it bends or tapers."""
    rows, found = _edges(p, 1, straight, band), []
    for side in (0, 1):
        cut = [LEDGE[0] <= row[1 + side] <= LEDGE[1] for row in rows]
        whole = [abs(row[1 + side]) < 2 for row in rows]
        i = 0
        while i < len(rows):
            j = i
            while j < len(rows) and cut[j]:
                j += 1
            step = (i and whole[i - 1]) or (j < len(rows) and whole[j])
            if j > i and step and HIGH[0] <= rows[j - 1][0] - rows[i][0] + 2 <= HIGH[1]:
                found.append((side, rows[i][0], rows[j - 1][0]))
            i = max(j, i + 1)
    return found


def notch(p, run, straight, band, side):
    """The notch cut into the stem of outline `p` on `side` (NOTCHES): (how
    deep, for how many units of height it is that deep by half). It is the
    rows where the stem's edge is in, up to the row it ends on, at once: where
    its bowl joins the stem."""
    deep = [row[1 + side] for row in _edges(p, run, straight, band, 1)]
    top = next((i for i in range(1, len(deep)) if deep[i] < 0.5 and deep[i - 1] - deep[i] > 8), 0)
    low = next((i for i in range(top - 1, -1, -1) if deep[i] <= 0.5), -1)
    most = max(deep[low + 1 : top], default=0)
    return most, sum(d >= most / 2 for d in deep[low + 1 : top])


def step(p):
    """The step under the ball that ends the upper right arm of outline `p`
    (Italic's x, α): (how high, how far the ball goes on right of it), of
    the edge that goes straight up, 15 units or more, in the upper right
    quarter, the one furthest right; (0, 0) without one."""
    x0, y0, x1, y1 = p.bounds
    found, last = [], None
    for verb, points in p.segments:
        if verb == "lineTo" and last:
            (ax, ay), (bx, by) = last, points[-1]
            high, right = abs(by - ay), ax > (x0 + x1) / 2 and min(ay, by) > (y0 + y1) / 2
            if abs(ax - bx) < 0.5 and high >= 15 and right:
                found.append((ax, round(high), round(x1 - ax)))
        last = points[-1] if points else last
    return max(found, default=(0, 0, 0))[1:]


def bar(p, over=None, lean=0):
    """How thick the bar over outline `p` is (Π π τ): of its strokes down
    from its top, every 5 units across, the thickness most have. Or, a bar
    `over` units thick or so: the thinnest and the thickest it is (least,
    most), right of where its first leg comes down from it, so past its
    beak, to 15 units short of its end, but where a leg comes down and for
    15 units after: Italic's legs lean more than its bar's cut. `lean`, the
    slant of its style (shapes.slope): it is measured upright."""
    top = p.bounds[3]
    p = pathops.Path(p)
    p.transform(1, 0, -lean, 1, lean * top, 0)
    x0, x1 = min(a for a, _ in runs(p, y=top - 1)), max(b for _, b in runs(p, y=top - 1))
    across = range(int(x0) + 5, int(x1) - 14, 5)
    down = [next((b - a for a, b in runs(p, x=x)[::-1] if b > top - 1), 0) for x in across]
    if not over:
        return Counter(round(d) for d in down).most_common(1)[0][0]
    legs = [i for i, d in enumerate(down) if d >= 3 * over]  # a beak is twice the bar or so
    beside = {i + k for i in legs for k in range(4)}
    plain = [d for i, d in enumerate(down) if legs and i > legs[0] and i not in beside]
    return min(plain, default=0), max(plain, default=0)


def check_greek(font, every):
    """The Greek letters drawn by hand for `font`, a Redaction style (`every`,
    its glyphs drawn by hand), are all there, with their side bearings and
    a note of what they are drawn from, the pieces and counters of the
    letter each is drawn from (GREEK), or their own (PIECES), and their
    straight stems (greek.STEMS) as thick as that letter's, to 4 units (a
    slanted stem carried on is not as thick to the unit). And the details
    drawn into them: Φ Ψ φ ψ have two ledges, one on each side of the stem,
    not at one height (LEDGED); ρ has d's notch, as deep and as high
    (NOTCHES); the bars of π and τ are as thick as Π's (BAR); no lowercase
    letter has feet (ENDS); χ's thin stroke runs from upper left to lower
    right (THICKER); Italic ρ's stem runs on into its bowl (BEND) and
    Italic α crosses itself (PARTED), a's bowl and little wider (WIDER),
    its arm ending in a ball over x's step (STEP, BALL)."""
    problems = []
    style = font["name"].getDebugName(2)
    for cp in greek.DRAWN:
        c = chr(cp)
        if cp == greek.DELTA and greek.letterlike() and chr(greek.INCREMENT) in every:
            continue  # ∆'s outline, maths.py's: check_operators
        if c not in every:
            problems.append(f"{c} is missing")
            continue
        p, lib = every[c]
        if len(lib.get(greek.SIDES, ())) != 2 or not lib.get("com.lihbr.kuronuri.source"):
            problems.append(f"{c} lacks its side bearings or its source")
        pieces = _pieces(path(font, GREEK[c])) if c in GREEK else PIECES[c]
        if _pieces(p) != pieces:
            problems.append(f"{c} has not the pieces and counters of {GREEK.get(c, pieces)}")
        for band, run, letter, their_band, their_run in greek.stems(style).get(c, []):
            a, b = _stem(None, c, band, run, p), _stem(font, letter, their_band, their_run)
            if a is None or b is None or abs(a - b) > 4:
                problems.append(f"a stem of {c} is {a} thick, not {b} as that of {letter}")
    for c, (straight, band) in LEDGED.items():
        if c not in every:
            continue
        found = ledges(every[c][0], straight, band)
        apart = len(found) == 2 and (found[0][2] < found[1][1] or found[1][2] < found[0][1])
        if sorted(side for side, _, _ in found) != [0, 1] or not apart:
            problems.append(
                f"{c} has not a ledge on each side of its stem, not at one height: {found}"
            )
    if "ρ" in every:
        ours, theirs = notch(every["ρ"][0], *NOTCHES["ρ"]), notch(path(font, "d"), *NOTCHES["d"])
        if abs(ours[0] - theirs[0]) > NOTCH or ours[1] < NOTCHED:
            problems.append(
                f"ρ's notch is {ours[0]:.0f} deep for {ours[1]}, not {theirs[0]:.0f} as d's"
                f" for {NOTCHED} or more"
            )
    for c, ends in (ENDS | ITALIC_ENDS if style == "Italic" else ENDS).items():
        p = every[c][0] if c in every else None
        for run, where in ends if p else []:
            y, up = {None: (p.bounds[1], 1), "top": (p.bounds[3], -1)}.get(where, (where, 1))
            feet = [runs(p, y=y + up * k) for k in range(PLAIN, TIP + 1, PLAIN)]
            stem = runs(p, y=y + up * STRAIGHT)
            if not all(len(r) > max(run, -run - 1) for r in (*feet, stem)):
                problems.append(f"{c} has no stroke {run} to end plain at {y:.0f}")
                continue
            (a, b), (d, e) = max((r[run] for r in feet), key=lambda r: r[1] - r[0]), stem[run]
            leans = abs((a + b) - (d + e)) / 2 > (STRAIGHT - PLAIN) * (abs(slope(font)) + 0.2)
            if b - a > e - d + (SLANTED if leans else FOOT):
                problems.append(f"{c}'s stroke {run} ends in a foot at {y:.0f}, {b - a:.0f} wide")
    if "χ" in every:
        p = every["χ"][0]
        low, top = p.bounds[1], p.bounds[3]
        above, below = (runs(p, y=y) for y in (top - (top - low) / 5, low + (top - low) / 5))
        wide = [[b - a for a, b in found] for found in (above, below)]
        if [len(w) for w in wide] != [2, 2] or not (
            wide[0][1] > THICKER * wide[0][0] and wide[1][0] > THICKER * wide[1][1]
        ):
            problems.append(f"χ's thin stroke does not run from upper left to lower right: {wide}")
    if style == "Italic" and "ρ" in every:
        p = every["ρ"][0]
        edge = [runs(p, y=y)[0][0] for y in range(int(p.bounds[1]) + 20, RUNS, 10)]
        lean = [b - a for a, b in zip(edge, edge[1:])]
        if max(abs(b - a) for a, b in zip(lean, lean[1:])) > BEND:
            problems.append("ρ's stem does not run on straight into its bowl")
    if style == "Italic" and "α" in every:
        p = every["α"][0]
        if [len(runs(p, y=y)) for y in (PARTED[0], CROSSED, PARTED[1])] != [3, 2, 3]:
            problems.append("α's strokes do not cross, apart below and above the crossing")
        a = path(font, "a")
        wider = (p.bounds[2] - p.bounds[0]) - (a.bounds[2] - a.bounds[0])
        ours, theirs = (runs(q, y=FULL) for q in (p, a))
        full = (ours[1][0] - ours[0][1]) / (theirs[1][0] - theirs[0][1])
        if wider > WIDER or full < COUNTER:
            problems.append(f"α is {wider:.0f} wider than a, its counter {full:.2f} of a's")
        (high, across), theirs = step(p), step(path(font, "x"))
        if high < STEP * theirs[0] or across < BALL * high:
            problems.append(
                f"α's arm does not end in a ball: its step is {high} high, not {STEP} of x's"
                f" {theirs[0]} or more, the ball {across} across from it"
            )
    if "Π" in every:
        theirs, lean = bar(every["Π"][0]), slope(font)
        for c in "πτ":
            ours = bar(every[c][0], theirs, lean) if c in every else (theirs, theirs)
            if max(abs(t - theirs) for t in ours) > BAR:
                problems.append(
                    f"{c}'s bar is {ours[0]:.0f} to {ours[1]:.0f} thick, not {theirs} as that of Π"
                )
    return problems


def check_operators(font, every):
    """The operators drawn by hand for `font`, a Redaction style (`every`,
    its glyphs drawn by hand), are all there: ∬ ∭ in as many pieces as
    integrals, the others but ∮ with the pieces and counters of the letter
    each is drawn from, Italic's f for ∫; ∆ is as tall as A, and ∇, it
    turned over, as tall as V, with ∆'s counter, which V has not."""
    problems = []
    italic = redaction(None, "Italic")
    for cp, letter in maths.OPERATORS.items():
        c = chr(cp)
        if c not in every:
            problems.append(f"{c} is missing")
            continue
        pieces = _pieces(every[c][0])
        if cp in maths.REPEATED:
            if pieces != (maths.REPEATED[cp], 0):
                problems.append(f"{c} is not {maths.REPEATED[cp]} integrals apart")
        elif cp == 0x2207:
            if "∆" not in every or pieces != _pieces(every["∆"][0]):
                problems.append(f"{c} has not the pieces and counters of ∆")
        elif cp != 0x222E and pieces != _pieces(path(italic if letter == "f" else font, letter)):
            problems.append(f"{c} has not the pieces and counters of {letter}")
        if cp in (0x2206, 0x2207) and every[c][0].bounds[1::2] != path(font, letter).bounds[1::2]:
            problems.append(f"{c} is not as tall as {letter}")
    return problems


def check_arrows(font, every):
    """The owner's head of → (`every`, the glyphs drawn by hand for `font`, a
    Redaction style) is in one piece, and that of its → as built: within
    it, as tall; only in Regular."""
    problems = []
    if font["name"].getDebugName(2) != "Regular":
        return [f"{c} is drawn in another style than Regular" for c in arrows.SOURCES]
    built = arrows._paths(arrows.Arrows(arrows.Pen(font, font)))
    for c, name in zip(arrows.SOURCES, ("arrowright",)):
        if c not in every:
            problems.append(f"{c} is missing")
            continue
        p = every[c][0]
        if _pieces(p) != (1, 0):
            problems.append(f"{c} is not one piece")
        b = built[name]
        x0, y0, x1, y1 = p.bounds
        bx0, by0, bx1, by1 = b.bounds
        p = p.transform(1, 0, 0, 1, bx1 - x1, 0)  # tips together
        out = abs(pathops.op(p, b, pathops.PathOp.DIFFERENCE).area)
        if out > 1 or abs((y1 - y0) - (by1 - by0)) > 1:  # as tall as its head
            problems.append(f"{c} is not the head of {name} as built")
    return problems


def check_postal(font, p):
    """〒 drawn by hand, `p`, of `font`, a Redaction style, is fullwidth's:
    as drawn in its smooth font, centred; upright, as tall as T, in two
    pieces without counters, its two bars as thick as T's, its stem as T's
    measured across (Italic's slanted)."""
    problems = []
    built = pathops.Path()
    fullwidth._postal(font, font, None, 1000).draw(pathops.PathPen(built), None)
    if round(abs(built.area)) != round(abs(p.area)) or built.bounds[1::2] != p.bounds[1::2]:
        problems.append("is not used")
    t = path(font, "T")
    if p.bounds[1::2] != t.bounds[1::2]:
        problems.append("is not as tall as T")
    if _pieces(p) != (2, 0):
        problems.append("is not two pieces")
    top = t.bounds[3]
    bar = top - max(y for _, y in path_points(t) if y < top)
    x0, _, x1, _ = p.bounds
    bars = [r for r in runs(p, x=x0 + (x1 - x0) / 4) if r[0] > p.bounds[1]]  # not the foot
    if len(bars) != 2 or any(abs(b - a - bar) > 1 for a, b in bars):
        return [*problems, f"bars are not as thick as T's ({bar:.0f})"]
    below = bars[0][0]
    a, b = runs(t, y=below / 2)[0]
    across = (b - a) / (1 + slope(font) ** 2) ** 0.5
    stems = [runs(p, y=below * k) for k in (0.3, 0.7)]
    if any(len(r) != 1 for r in stems) or stems[0] != stems[1]:
        problems.append("does not stand upright")
    elif abs(stems[0][0][1] - stems[0][0][0] - across) > 2:
        problems.append(f"stem is not as thick as T's ({across:.0f})")
    return problems


def path_points(p):
    """The points of path `p`, on and off its curves."""
    return [pt for _, pts in p.segments for pt in pts]


def check_slice(task):
    path, declared = task
    problems = sanitize(path)
    cmap = set(TTFont(path).getBestCmap())
    if cmap != declared:
        problems.append(f"{path.name}: unicode-range differs from cmap")
    if re.search(r"-latin-\d", path.name):
        if not tabular(path, DIGITS):
            problems.append(f"{path.name}: tnum is not tabular")
        arrow, alt = shape(path, "->")[0], shape(path, "->", {"ss01": True})[0]
        if len(arrow) != 1 or len(alt) != 1 or arrow == alt:
            problems.append(f"{path.name}: -> does not turn into an arrow, or its alt")
    return cmap, problems


def parse_range(text):
    cps = set()
    for part in text.split(","):
        a, _, b = part.strip()[2:].partition("-")
        cps.update(range(int(a, 16), int(b or a, 16) + 1))
    return cps


def check_web():
    web = DIST / "web"
    families = sorted(
        p.name for p in web.glob("*.css") if p.name != "index.css" and not p.stem.endswith("-latin")
    )
    problems = []
    if sorted(re.findall(r'@import "\./([^"]+)";', (web / "index.css").read_text())) != families:
        problems.append("index.css does not import every family")
    for css in families:
        latin = (web / css.replace(".css", "-latin.css")).read_text()
        if FACE.findall(latin) != [
            face
            for face in FACE.findall((web / css).read_text())
            if re.search(r"-latin(-ext)?-", face[3])
        ]:
            problems.append(f"{css}: the Latin-only CSS does not list its latin slices")
    faces = [face for css in families for face in FACE.findall((web / css).read_text())]
    for css in families:  # fwid joins ｶ and ﾞ into ガ within a slice only
        ranges = [parse_range(rng) for *_, rng in FACE.findall((web / css).read_text())]
        halfwidth = set(range(0xFF61, 0xFFA0))
        if sum(bool(r & halfwidth) for r in ranges) > len(STYLE):
            problems.append(f"{css}: halfwidth katakana are split across slices")
    if unlisted := set((web / "files").iterdir()) - {web / url for *_, url, _ in faces}:
        problems.append(f"{len(unlisted)} slices missing from the CSS")
    if missing := [url for *_, url, _ in faces if not (web / url).exists()]:
        return problems + [f"the CSS lists missing files: {missing[:3]}"]
    tasks = [(web / url, parse_range(rng)) for *_, url, rng in faces]
    by_font = defaultdict(list)
    with ProcessPoolExecutor() as ex:
        for (family, style, weight, *_), (cmap, probs) in zip(
            faces, ex.map(check_slice, tasks, chunksize=16)
        ):
            problems += probs
            by_font[f"{family.replace(' ', '')}-{STYLE[style, weight]}"].append(cmap)
    for ps, cmaps in by_font.items():
        union = set().union(*cmaps)
        if sum(map(len, cmaps)) != len(union):
            problems.append(f"{ps}: slices overlap")
        if union != set(TTFont(DIST / "ttf" / f"{ps}.ttf").getBestCmap()):
            problems.append(f"{ps}: slices do not cover the font")
    return problems


# --- The pixelated Japanese, on the coarse grids (from COARSE) ---------------

COARSE = 50  # grids whose Japanese is checked, phased (pixel.PHASED) or not

# Characters whose rows and spacing are checked: kana, and the most frequent
# kanji (Google's slices from review.FREQUENT up)
COMMON = 105
# Not phased: placed as they stand, as Noto Serif JP's instance of the style
# pixelated without any of it would be (pixel.phased_glyphs)
PLACED = (
    "、。・，．「」『』（）［］｛｝〈〉《》【】〔〕〖〗〘〙〚〛｟｠"
    "ー々〆〃ゝゞヽヾ゛゜ぁぃぅぇぉっゃゅょァィゥェォッャュョ"
)
# Shaped next to each other, bracket against bracket and against these
MARKS = "、。・，．"
# Overlaps the fonts before phasing had already, vertically on 70: braces,
# and their vertical forms
OVERLAPPING = {(70, pair) for pair in "『｝ 〘｝ ｛｝ 『︸ 〘︸ ︷︸ ︷｝ ﹃︸ ﹃｝ ｛︸".split()}
# Pairs drawn apart by a stroke or a mark, and how many cells apart they stay
# at least, by grid: pixel.APART at least, more where the grid has room
APART = {
    "間問": {50: 20, 70: 8, 100: 6},
    "未末": {50: 8, 70: 4, 100: 3},
    "土士": {50: 6, 70: 4, 100: 3},
    "千干": {50: 8, 70: 4, 100: 3},
    "杮柿": {50: 3, 70: 3, 100: 3},
    "べぺ": {50: 6, 70: 4, 100: 3},
    "ベペ": {50: 6, 70: 4, 100: 3},
    "ぶぷ": {50: 6, 70: 4, 100: 3},
}
# Counters closed by a bar each keeps at least, by grid: 日 within 書, the
# box of 車 and of 重 divided, 間's 門 and 日
COUNTERS = {
    "日": {50: 2, 70: 2, 100: 2},
    "目": {50: 3, 70: 3, 100: 2},
    "書": {50: 2, 70: 2, 100: 1},
    "車": {50: 2, 70: 2, 100: 2},
    "重": {50: 2, 70: 2, 100: 2},
    "間": {50: 5, 70: 4, 100: 3},  # on 100, 門 and 日 are nine rows of ten: 日 ends on its feet
}

# Look-alikes a reader tells apart by what one has more of than the other,
# on 100, where a stroke is a cell: the first of each pair has more of it
# (meaning). Kept apart in cells (APART), they may still read alike: 書
# drawn with two verticals through its top reads 昔, 間 with one box in its
# 門 reads 問, 車 with its box undivided 巾, 末 with its bars alike 未
MEANING = {
    "書昔": "single",  # one stem above 聿's top bar, where 廿 has two
    "書吾": "single",  # and 五 none
    "書舌": "counters",  # ヨ and 日 boxed, where 舌 has 口
    "主全": "dot",  # its dot apart, where 人 is a roof
    "間問": "below",  # 日 in 門, two counters below its middle where 口 has one
    "聞問": "below",  # 耳 in 門, boxed, where 口 has one
    "聞冊": "gate",  # 門's two boxes atop it, apart
    "車巾": "counters",  # the box of 車 divided, 巾 open
    "目日": "counters",
    "土士": "foot",  # the bottom bar longer than the top one
    "未末": "foot",
}
# Kana a voicing mark (゛) and a semi-voicing one (゜) tell apart: on 100, at
# least pixel.APART cells apart, a ring not a blot of ticks
VOICED = "ばぱ びぴ ぶぷ べぺ ぼぽ バパ ビピ ブプ ベペ ボポ".split()
# What a reader needs of a character, on 100, by the strokes that make it
# (shape): each measure true. Drawn by hand where phasing lost it
# (glyphs/drawn/japanese.txt), each once read as another or broken
SHAPES = {
    "書": "single",  # its stem above ヨ: without it, 吾 or 舌
    "土": "sole",  # its bottom bar whole, under the stem
    "主": "sole dot",  # and its dot apart: a roof is 全
    "亜": "flat",  # nothing above its top bar
    "間": "gate",
    "聞": "gate",
    "問": "gate",
    "関": "gate",  # 門's boxes apart, its legs whole
    "単": "dots",  # three dots above 田, its four counters
    "順": "stems",  # 川's three stems apart, beside 頁
    "価": "capped",  # 西's top bar whole, no terminal alone
    "会": "roof",  # 人 open under its apex, not 去's top
    "テ": "clear",  # nothing loose where ゛ goes: デ
    "き": "clear",
    "さ": "clear",
    "せ": "clear",
    "デ": "ticks",  # its ゛ two ticks
}
# The same, for one style only
STYLED = {("車", "Bold"): "single"}  # its stem above the top bar


def single(cells):
    """1 if one stroke rises above the first bar (top), as 書's stem does, 0
    if more, as 廿's two do in 昔, or none, as in 吾."""
    return int(len(pieces(top(cells)[1])) == 1)


def top(cells):
    """(row, cells above it) of the first bar from the top: a row of ink as
    long as half the glyph is wide. (None, cells) if none."""
    cols = [c for c, _ in cells]
    width = max(cols) - min(cols) + 1
    for r in sorted({r for _, r in cells}, reverse=True):
        if 2 * longest(cells, r) >= width:
            return r, {(c, rr) for c, rr in cells if rr > r}
    return None, set(cells)


def longest(cells, row):
    """The longest run of ink along a row of cells."""
    cols = sorted(c for c, r in cells if r == row)
    best = run = 0
    for k, c in enumerate(cols):
        run = run + 1 if k and c == cols[k - 1] + 1 else 1
        best = max(best, run)
    return best


def flat(cells):
    """1 if nothing stands above the first bar: 亜 without a stray end."""
    return int(not top(cells)[1])


def dot(cells):
    """1 if the topmost stroke is a dot apart from the rest, three cells at
    most, above the first bar: 主's, where 全's 人 is a roof over 王."""
    row, above = top(cells)
    highest = max(r for _, r in cells)
    piece = next(p for p in pieces(cells) if any(r == highest for _, r in p))
    return int(row is not None and len(piece) <= 3 and piece <= above)


def sole(cells):
    """1 if the bottom row is one bar, the longest of the glyph: 土's foot
    whole, not a bar and a terminal past a gap."""
    rows = {r for _, r in cells}
    low = min(rows)
    return int(
        longest(cells, low) == sum(1 for _, r in cells if r == low)
        and longest(cells, low) >= max(longest(cells, r) for r in rows)
    )


def gate(cells):
    """1 if the top three rows are two pieces or more, each boxing a
    counter, and the leftmost and rightmost columns run whole from top to
    bottom: 門, its boxes apart, its legs unbroken."""
    cols = [c for c, _ in cells]
    rows = [r for _, r in cells]
    high = {(c, r) for c, r in cells if r >= max(rows) - 2}
    boxes = [p for p in pieces(high) if holes(p)]
    legs = all(
        (c, r) in cells for c in (min(cols), max(cols)) for r in range(min(rows), max(rows) + 1)
    )
    return int(len(boxes) >= 2 and legs)


def dots(cells):
    """1 if three pieces stand above the first bar, and four counters: 単's
    dots apart, its 田 whole."""
    return int(len(pieces(top(cells)[1])) == 3 and counters(cells) >= 4)


def stems(cells):
    """1 if a row in the middle third crosses four strokes or more: 川's
    three stems apart, and 頁 beside them."""
    rows = sorted({r for _, r in cells})
    third = len(rows) // 3
    return int(max(len(_runs_of(cells, r)) for r in rows[third : len(rows) - third]) >= 4)


def _runs_of(cells, row):
    """Runs of ink along a row of cells, as (start, stop)."""
    cols = sorted(c for c, r in cells if r == row)
    out = []
    for c in cols:
        if out and out[-1][1] == c:
            out[-1][1] = c + 1
        else:
            out.append([c, c + 1])
    return out


def capped(cells):
    """1 if every run of the top row in the right half is three cells or
    longer: 価's 西 under a whole bar, not a terminal alone."""
    cols = [c for c, _ in cells]
    mid = (min(cols) + max(cols)) / 2
    high = max(r for _, r in cells)
    right = [(a, b) for a, b in _runs_of(cells, high) if b - 1 > mid]
    return int(bool(right) and all(b - a >= 3 for a, b in right))


def roof(cells):
    """1 if the three rows under the topmost cell are two strokes each,
    spreading from it: 人's roof open, as in 会, not shut into a bar."""
    rows = sorted({r for _, r in cells}, reverse=True)
    if len(rows) < 4 or len(_runs_of(cells, rows[0])) != 1:
        return 0
    left, right = _runs_of(cells, rows[0])[0]
    for r in rows[1:4]:
        runs = _runs_of(cells, r)
        if len(runs) != 2 or not (runs[0][0] < left and runs[1][1] > right):
            return 0
        left, right = runs[0][0], runs[1][1]
    return 1


def zone(cells):
    """Pieces of `cells`, side by side only, of two cells or fewer, wholly
    where ゛ goes: the right half and the top two fifths."""
    cols = [c for c, _ in cells]
    rows = [r for _, r in cells]
    mid, low = (min(cols) + max(cols)) / 2, max(rows) - 0.4 * (max(rows) - min(rows))
    return [
        p
        for p in pieces(cells, diagonal=False)
        if len(p) <= 2 and all(c > mid and r >= low for c, r in p)
    ]


def clear(cells):
    """1 if no loose cell stands where ゛ goes: テ, not デ."""
    return int(not zone(cells))


def ticks(cells):
    """1 if two ticks or more stand where ゛ goes, three cells at least: デ's
    ゛, not the end of a bar."""
    marks = zone(cells)
    return int(len(marks) >= 2 and sum(map(len, marks)) >= 3)


def below(cells):
    """Counters of a cell set wholly below its middle row: 日 in 間."""
    rows = [r for _, r in cells]
    middle = (max(rows) + min(rows)) / 2
    return sum(all(r < middle for _, r in hole) for hole in holes(cells))


def pieces(cells, diagonal=True):
    """Pieces of a cell set, cells side by side or (if `diagonal`) corner to
    corner."""
    near = [(i, j) for i in (-1, 0, 1) for j in (-1, 0, 1) if diagonal or not (i and j)]
    left, out = set(cells), []
    while left:
        piece, todo = set(), [left.pop()]
        while todo:
            c, r = todo.pop()
            piece.add((c, r))
            for n in [(c + i, r + j) for i, j in near]:
                if n in left:
                    left.remove(n)
                    todo.append(n)
        out.append(piece)
    return out


def foot(cells):
    """How much longer the lowest bar is than the highest: bars, the
    longest run along a row, are those half as wide as the glyph."""
    cols = [c for c, _ in cells]
    width = max(cols) - min(cols) + 1
    bars = []
    for r in sorted({r for _, r in cells}):
        run = longest = 0
        for c in range(min(cols), max(cols) + 1):
            run = run + 1 if (c, r) in cells else 0
            longest = max(longest, run)
        if 2 * longest >= width:
            bars.append(longest)
    return bars[0] - bars[-1] if len(bars) > 1 else 0


def meaning(font, grid, style=None, vertical=False):
    """Look-alikes (MEANING) that do not differ as a reader tells them
    apart, characters without a stroke a reader needs of them (SHAPES, and
    STYLED for `style`), kana voiced and semi-voiced (VOICED) fewer than
    pixel.APART cells apart, and kana without a voicing mark that look
    voiced: a piece of two cells or fewer apart in their top right corner,
    where ゛ goes, as ぎ's on き. If `vertical`, of the vertical forms (GSUB
    vert), where a character has one."""
    glyf, cmap = font["glyf"], font.getBestCmap()
    down = verticals(font) if vertical else {}
    measure = {
        "single": single,
        "below": below,
        "counters": counters,
        "foot": foot,
        "dot": dot,
        "gate": gate,
        "flat": flat,
        "sole": sole,
        "dots": dots,
        "stems": stems,
        "capped": capped,
        "clear": clear,
        "ticks": ticks,
        "roof": roof,
    }

    def of(c):
        name = cmap[ord(c)]
        return cells_of(glyf[down.get(name, name)], glyf, grid)

    problems = []
    shapes = dict(SHAPES)
    for (c, s), what in STYLED.items():
        if s == style:
            shapes[c] = f"{shapes.get(c, '')} {what}".strip()
    for c, whats in shapes.items():
        if ord(c) not in cmap:
            continue
        cells = of(c)
        if missing := [w for w in whats.split() if not measure[w](cells)]:
            problems.append(f"{c}: not {', '.join(missing)}")
    for pair, what in MEANING.items():
        a, b = (measure[what](of(c)) for c in pair)
        if a <= b:
            problems.append(f"{pair}: {pair[0]} has no more {what} than {pair[1]} ({a}, {b})")
    for pair in VOICED:
        if (n := apart(*(of(c) for c in pair))) < pixel.APART:
            problems.append(f"{pair}: {n} cells apart, not {pixel.APART}")
    loose = []
    for cp in KANA:
        base = unicodedata.decomposition(chr(cp)).split()
        if len(base) != 2 or base[1] not in ("3099", "309A") or int(base[0], 16) not in cmap:
            continue
        if (plain := chr(int(base[0], 16))) not in loose and corner(of(plain)):
            loose.append(plain)
    if loose:
        problems.append(f"{''.join(loose)}: loose cells where ゛ goes")
    return problems


# Words set down the page, each of a character drawn by hand on 100 and
# one that took the top or the bottom row of its em before phasing: on 100,
# where an em is ten rows, the glyph that takes the bottom row meets the
# one under it that takes the top row (meets)
DOWN = (
    "読書 図書 全書 証書 願書 報告書 乗車 電車 車内 主人 君主 吾輩 会合 社会 大会 "
    "土地 週末 重要 プール ポスト"
)


def meets(path, font, grid, style, stood):
    """Glyphs of `font` that meet the glyph above or below them in vertical
    text, on `grid`: phased kanji and kana, and their vertical forms, that
    take the top or the bottom row of their vertical advance where they did
    not unshifted (`stood`, {character: (glyph, glyf)}), and glyphs drawn
    by hand that take its top row, so that the glyph above meets them (kanji
    stand on its bottom row); then, of the words of DOWN set down the page,
    the glyphs that meet for one of these."""
    glyf, cmap, vmtx = font["glyf"], font.getBestCmap(), font["vmtx"]
    down, order = verticals(font), font.getGlyphOrder()
    drawn = {c for (g, s, c) in drawn_cells(pixel.JAPANESE) if (g, s) == (grid, style)}
    wrong, problems = {}, []
    for c, (was, _) in stood.items():
        if ord(c) not in cmap or c in PLACED or not was.numberOfContours:
            continue
        for name in dict.fromkeys((cmap[ord(c)], down.get(cmap[ord(c)], cmap[ord(c)]))):
            glyph = glyf[name]
            glyph.recalcBounds(glyf)
            vadv, tsb = vmtx[name]
            top = glyph.yMax + tsb  # its vertical origin, as unshifted (check_spacing)
            edges = [(g.yMax > top - grid, g.yMin < top - vadv + grid) for g in (was, glyph)]
            ends = {e for e, b, n in zip(("top", "bottom"), *edges) if n and not b}
            if c in drawn and edges[1][0]:
                ends.add("top")
            for end in sorted(ends):
                why = (
                    "drawn by hand" if c in drawn and end == "top" else "where it did not unshifted"
                )
                form = " (vertical)" if name != cmap[ord(c)] else ""
                problems.append(f"{c}{form}: takes the {end} row of its em, {why}")
            if ends:
                wrong[name] = ends
    for word in DOWN.split():
        buf = hb.Buffer()
        buf.add_str(word)
        buf.guess_segment_properties()
        buf.direction = "ttb"
        hb.shape(hb_font(path), buf)
        y, placed = 0, []
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            name = order[info.codepoint]
            dx, dy = pos.x_offset // grid, (y + pos.y_offset) // grid
            placed.append((name, {(c + dx, r + dy) for c, r in cells_of(glyf[name], glyf, grid)}))
            y += pos.y_advance
        for (a, upper), (b, under) in zip(placed, placed[1:]):
            near = {(c + i, r + j) for c, r in upper for i in (-1, 0, 1) for j in (-1, 0, 1)}
            if near & under and ("bottom" in wrong.get(a, ()) or "top" in wrong.get(b, ())):
                problems.append(f"{word}, set down the page: its glyphs meet")
    return problems


# The kanji drawn by hand are no darker than this share of the common ones
DARKEST = 0.95


def colour(font, grid, style):
    """Kanji drawn by hand on `grid` (glyphs/drawn/japanese.txt) darker than
    DARKEST of the common kanji of the font, in cells: 車, its box as wide
    as its long bar, among lighter kanji."""
    glyf, cmap = font["glyf"], font.getBestCmap()

    def ink(c):
        return len(cells_of(glyf[cmap[ord(c)]], glyf, grid))

    inks = sorted(ink(c) for c in common() if script(ord(c)) == "Hani" and ord(c) in cmap)
    most = inks[int(DARKEST * (len(inks) - 1))]
    drawn = sorted({c for (g, s, c) in drawn_cells(pixel.JAPANESE) if (g, s) == (grid, style)})
    return [
        f"{c}: {ink(c)} cells, darker than {DARKEST:.0%} of the common kanji ({most})"
        for c in drawn
        if script(ord(c)) == "Hani" and ink(c) > most
    ]


def verticals(font):
    """{glyph name: its vertical form}, of GSUB vert, one glyph for one."""
    out = {}
    if "GSUB" not in font:
        return out
    table = font["GSUB"].table
    for record in table.FeatureList.FeatureRecord:
        if record.FeatureTag == "vert":
            for i in record.Feature.LookupListIndex:
                for sub in table.LookupList.Lookup[i].SubTable:
                    sub = getattr(sub, "ExtSubTable", sub)
                    for a, b in getattr(sub, "mapping", {}).items():
                        out.setdefault(a, b)
    return out


def corner(cells, most=2):
    """Loose cells of `cells` in the top right of the glyph (its right half,
    its top third), where ゛ goes: pieces of `most` cells or fewer that
    touch nothing, or a cell alone but for one at its corner, the end of a
    bar (き's slant, broken, beside its top bar)."""
    cols = [c for c, _ in cells]
    rows = [r for _, r in cells]
    mid, top = (min(cols) + max(cols)) / 2, max(rows) - (max(rows) - min(rows)) / 3
    near = [(i, j) for i in (-1, 0, 1) for j in (-1, 0, 1) if i or j]
    left, out = set(cells), []
    while left:
        piece, todo = set(), [left.pop()]
        while todo:
            c, r = todo.pop()
            piece.add((c, r))
            for n in [(c + i, r + j) for i, j in near]:
                if n in left:
                    left.remove(n)
                    todo.append(n)
        if len(piece) <= most and all(c > mid and r >= top for c, r in piece):
            out.append(piece)
    for c, r in cells:
        touching = [(i, j) for i, j in near if (c + i, r + j) in cells]
        if c > mid and r >= top and len(touching) == 1 and all(touching[0]):
            i, j = touching[0]
            if all((c + i * k, r + j) in cells for k in (1, 2, 3)):
                out.append({(c, r)})
    return out


def cells_of(glyph, glyf, grid):
    """The filled cells (column, row) of a pixelated glyph, rows up."""
    coords, ends, _ = glyph.getCoordinates(glyf)
    coords = [tuple(p) for p in coords]
    edges, start, out = defaultdict(list), 0, set()
    for end in ends:
        pts = coords[start : end + 1]
        start = end + 1
        for (x, y), (xx, yy) in zip(pts, pts[1:] + pts[:1]):
            if x == xx and y != yy:
                for r in range(min(y, yy) // grid, max(y, yy) // grid):
                    edges[r].append((x // grid, 1 if yy > y else -1))
    for r, row in edges.items():
        winding, last = 0, 0
        for x, d in sorted(row):
            if winding:
                out.update((c, r) for c in range(last, x))
            winding, last = winding + d, x
    return out


def apart(a, b):
    """Cells two cell sets differ by, the best of their offsets within two."""
    return min(
        len(a ^ {(c + dc, r + dr) for c, r in b}) for dc in range(-2, 3) for dr in range(-2, 3)
    )


def counters(cells):
    """Counters of a cell set: regions of air, side by side, not reaching out."""
    return len(holes(cells))


def holes(cells):
    """The counters of a cell set, each a set of cells of air."""
    if not cells:
        return []
    cols = [c for c, _ in cells]
    rows = [r for _, r in cells]
    x0, y0, x1, y1 = min(cols) - 1, min(rows) - 1, max(cols) + 1, max(rows) + 1
    air = {(c, r) for c in range(x0, x1 + 1) for r in range(y0, y1 + 1)} - set(cells)
    out = []
    while air:
        todo, hole, outside = [air.pop()], set(), False
        while todo:
            c, r = todo.pop()
            hole.add((c, r))
            outside |= c in (x0, x1) or r in (y0, y1)
            for n in ((c + 1, r), (c - 1, r), (c, r + 1), (c, r - 1)):
                if n in air:
                    air.remove(n)
                    todo.append(n)
        if not outside:
            out.append(hole)
    return out


@functools.cache
def common():
    """Kana and the most frequent kanji, as text."""
    kanji = {
        cp
        for sl in web.SLICES
        if sl["name"].isdigit() and int(sl["name"]) >= COMMON
        for a, b in sl["ranges"]
        for cp in range(a, b + 1)
        if script(cp) == "Hani"
    }
    return "".join(map(chr, sorted({*KANA, *kanji} - set(glyphs.CODEPOINTS))))


def unshifted(style, grid, text):
    """Noto Serif JP of `style` cut to `text`, pixelated on `grid` without
    phasing, each glyph as it stands: {character: glyph} at the weight of
    its spacing and punctuation (NOTO_WEIGHT), where the kanji stood before
    they were lightened, and at the weight of its kanji, as lightened
    (build.lighten). Their bounds are calculated."""
    weight = STYLES[style]["weight"]
    out = []
    for lightened in (False, True):
        font = noto_glyphs(NOTO_WEIGHT[weight], text)
        if lightened and noto_weight(weight, grid) != NOTO_WEIGHT[weight]:
            font = build.lighten(font, noto_glyphs(noto_weight(weight, grid), text))
        pixelate_font(font, grid)
        glyf = font["glyf"]
        for name in font.getGlyphOrder():
            glyf[name].recalcBounds(glyf)
        out.append({chr(cp): (glyf[n], glyf) for cp, n in font.getBestCmap().items()})
    return out


def check_japanese():
    """The Japanese of the coarse grids, in each font of dist/ttf from
    COARSE. Where it is lightened (family.light), kana and kanji keep
    the rows they took unshifted before they were lightened (or, failing any
    spot, as lightened), no more rows in all, and their ink in their
    advance; punctuation, brackets and marks are as they stand; advances
    and vertical metrics are those of grade 0, the Noto weight of the
    style, on the grid; no bracket, beside another or a mark, runs into it
    but where the fonts before phasing did (OVERLAPPING); pairs drawn apart
    stay so (APART), and counters divided by a bar (COUNTERS). Elsewhere,
    in Bold and on 50, every glyph of Noto Serif JP is as it stands at the weight of
    the style (stand), its spacing and brackets as above."""
    problems = []
    for ttf in sorted(DIST.glob("ttf/*.ttf")):
        grid, style = re.match(r"Kuronuri(\d+)-(\w+)", ttf.stem).groups()
        grid = int(grid)
        if grid < COARSE:
            continue
        font = TTFont(ttf)
        cmap, glyf, hmtx = font.getBestCmap(), font["glyf"], font["hmtx"]
        # Rows and advance, against each glyph unshifted
        hand = "".join(
            sorted({c for (g, s, c) in drawn_cells(pixel.JAPANESE) if g == grid} - set(common()))
        )
        stood, stands = unshifted(style, grid, common() + PLACED + hand)
        if not light(STYLES[style]["weight"], grid):
            problems += stand(ttf, font, stood)
            problems += check_spacing(ttf, font, grid, style)
            problems += check_brackets(ttf, font, grid)
            continue
        moved, wide, placed, rows = [], [], [], defaultdict(set)
        # Drawn by hand, a glyph may leave its top row free, as other kanji
        # do, its bottom row kept (土 on 100, which meets nothing above it so)
        drawn, lower = (
            {c for (g, s, c) in drawn_cells(pixel.JAPANESE) if (g, s) == (grid, style)},
            [],
        )
        for c, (was, was_glyf) in stood.items():
            if ord(c) not in cmap or ord(c) in glyphs.CODEPOINTS or not was.numberOfContours:
                continue
            ours = glyf[cmap[ord(c)]]
            ours.recalcBounds(glyf)
            own = stands[c][0]
            if c in PLACED:
                if ours.getCoordinates(glyf)[:2] != was.getCoordinates(was_glyf)[:2]:
                    placed.append(c)
                continue
            rows["before"].add((was.yMin, was.yMax))
            rows["now"].add((ours.yMin, ours.yMax))
            if (ours.yMin, ours.yMax) not in ((was.yMin, was.yMax), (own.yMin, own.yMax)):
                if c in drawn and ours.yMin == was.yMin and ours.yMax < was.yMax:
                    lower.append((c, ours.yMax))
                else:
                    moved.append(c)
            elif ours.xMin < min(0, own.xMin) or ours.xMax > max(hmtx[cmap[ord(c)]][0], own.xMax):
                wide.append(c)
        tops = {r[1] for r in rows["before"]}
        moved += [c for c, high in lower if high not in tops]
        for what, chars in (
            ("move up or down", moved),
            ("leave their advance", wide),
            ("are not placed as they stand", placed),
        ):
            if chars:
                problems.append(f"{ttf.name}: {len(chars)} {what}: {''.join(chars[:20])}")
        for k, edge in ((0, "bottom"), (1, "top")):
            now, before = ({r[k] for r in rows[v]} for v in ("now", "before"))
            if len(now) > len(before):
                problems.append(
                    f"{ttf.name}: kanji and kana take {len(now)} {edge} rows, not {len(before)}"
                )
        problems += check_spacing(ttf, font, grid, style)
        problems += check_brackets(ttf, font, grid)
        for pair, least in APART.items():
            a, b = (cells_of(glyf[cmap[ord(c)]], glyf, grid) for c in pair)
            if apart(a, b) < least[grid]:
                problems.append(f"{ttf.name}: {pair} are {apart(a, b)} cells apart")
        for c, least in COUNTERS.items():
            if (n := counters(cells_of(glyf[cmap[ord(c)]], glyf, grid))) < least[grid]:
                problems.append(f"{ttf.name}: {c} has {n} counters, not {least[grid]}")
        if grid == 100:
            problems += [f"{ttf.name}: {p}" for p in meaning(font, grid, style)]
            problems += [f"{ttf.name}: vertical {p}" for p in meaning(font, grid, style, True)]
            problems += [f"{ttf.name}: {p}" for p in colour(font, grid, style)]
            problems += [f"{ttf.name}: {p}" for p in meets(ttf, font, grid, style, stood)]
    return problems + check_order() + check_bold()


def stand(path, font, stood):
    """Glyphs of Noto Serif JP in `font` unlike `stood` ({character: (glyph,
    glyf)}), the same pixelated as it stands (unshifted)."""
    cmap, glyf = font.getBestCmap(), font["glyf"]
    off = [
        c
        for c, (was, was_glyf) in stood.items()
        if ord(c) in cmap
        and ord(c) not in glyphs.CODEPOINTS
        and glyf[cmap[ord(c)]].getCoordinates(glyf)[:2] != was.getCoordinates(was_glyf)[:2]
    ]
    if off:
        return [f"{path.name}: {len(off)} of Noto's not as they stand: {''.join(off[:20])}"]
    return []


# Bold's common kanji are at least this much as inked as Regular's, in
# cells, by grid: Noto's 800 against 500 on 50 (Regular's not lightened
# there, family.light), 1.33 times, and against 400 on 70 and 100, 1.38 and
# 1.22; 700, lightened as Regular's, they were 1.41 against 400 on 50, about
# 1.23 against 500, then 1.31 and 1.13, and did not read bold
BOLDER = {50: 1.3, 70: 1.35, 100: 1.17}


def check_bold():
    """Bold's kanji and kana are Noto Serif JP's at the weight of the style,
    800, on every grid (family.noto_weight), and its common kanji, on the
    coarse grids, at least BOLDER as inked as Regular's, where both are in
    dist/ttf."""
    problems = []
    weight = STYLES["Bold"]["weight"]
    for grid in (None, *GRIDS):
        if noto_weight(weight, grid) != NOTO_WEIGHT[weight]:
            problems.append(f"Bold's kanji are Noto's {noto_weight(weight, grid)} on {grid}")
    kanji = [c for c in common() if script(ord(c)) == "Hani"]
    for grid, least in BOLDER.items():
        paths = [DIST / "ttf" / f"{ps_name(grid, s)}.ttf" for s in ("Regular", "Bold")]
        if not all(p.exists() for p in paths):
            continue
        regular, bold = (_inked(TTFont(p), kanji, grid) for p in paths)
        if bold < least * regular:
            problems.append(
                f"{paths[1].name}: its common kanji {bold / regular:.2f} as inked as Regular's,"
                f" not {least}"
            )
    return problems


def _inked(font, chars, grid):
    """Cells inked by the glyphs of `chars` in `font`, a font on `grid`."""
    glyf, cmap = font["glyf"], font.getBestCmap()
    return sum(len(cells_of(glyf[cmap[ord(c)]], glyf, grid)) for c in chars if ord(c) in cmap)


def check_spacing(path, font, grid, style):
    """Advances, vertical advances and origins of the glyphs of Noto Serif
    JP, and of their vertical forms, are those of grade 0 on the grid, as
    pixel.pixelate_font rounds them."""
    zero = DIST / "ttf" / f"Kuronuri0-{style}.ttf"
    if not zero.exists():
        return []
    smooth = TTFont(zero)
    latin = set(redaction(None, style).getBestCmap()) | set(glyphs.CODEPOINTS)
    cps = [cp for cp in smooth.getBestCmap() if cp not in latin and cp >= 0x80]
    off = []
    for cp in cps:
        a, b = (_spacing(f, p, chr(cp)) for f, p in ((font, path), (smooth, zero)))
        want = []
        for (adv, vadv, origin), (adv0, vadv0, origin0) in zip(a, b):
            v = snap_advance(vadv0, grid)
            if origin is not None:
                origin = (origin, snap(origin0 - (vadv0 - v) / 2, grid))
            want.append(
                (
                    adv == snap_advance(adv0, grid),
                    vadv == v,
                    origin is None or origin[0] == origin[1],
                )
            )
        if not all(all(w) for w in want):
            off.append(chr(cp))
    if off:
        return [f"{path.name}: {len(off)} of Noto's spaced unlike grade 0: {''.join(off[:20])}"]
    return []


def _spacing(font, path, text):
    """(advance, vertical advance, vertical origin or None if empty) of the
    glyph `text` is set in, across and down (its vertical form)."""
    out = []
    glyf, hmtx, vmtx = font["glyf"], font["hmtx"], font["vmtx"]
    for direction in ("ltr", "ttb"):
        name = font.getGlyphName(shape(path, text, direction=direction)[0][0])
        g = glyf[name]
        vadv, tsb = vmtx[name]
        if g.numberOfContours:
            g.recalcBounds(glyf)
        out.append((hmtx[name][0], vadv, g.yMax + tsb if g.numberOfContours else None))
    return out


def check_brackets(path, font, grid):
    """Shape every opening bracket with every closing one, both ways, and
    each with MARKS, both ways, across and down, with each of palt, halt,
    vpal, vhal and chws or none: no two glyphs share a cell but in
    OVERLAPPING."""
    cmap, glyf = font.getBestCmap(), font["glyf"]
    opening = [c for c in map(chr, cmap) if unicodedata.category(c) == "Ps" and ord(c) >= 0x3000]
    closing = [c for c in map(chr, cmap) if unicodedata.category(c) == "Pe" and ord(c) >= 0x3000]
    pairs = [a + b for a in opening for b in closing] + [b + a for a in opening for b in closing]
    pairs += [a + m for a in opening + closing for m in MARKS]
    pairs += [m + a for a in opening + closing for m in MARKS]
    hbf, order = hb_font(path), font.getGlyphOrder()
    cache, problems = {}, set()
    for text in pairs:
        for direction in ("ltr", "ttb"):
            for features in (
                {},
                {"palt": True},
                {"halt": True},
                {"vpal": True},
                {"vhal": True},
                {"chws": True},
            ):
                buf = hb.Buffer()
                buf.add_str(text)
                buf.guess_segment_properties()
                buf.direction = direction
                hb.shape(hbf, buf, features)
                x = y = 0
                spots = []
                for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
                    spots.append((info.codepoint, x + pos.x_offset, y + pos.y_offset))
                    x, y = x + pos.x_advance, y + pos.y_advance
                unit = grid
                for _, sx, sy in spots:
                    unit = math.gcd(unit, sx, sy)
                k = grid // unit
                placed = []
                for gid, sx, sy in spots:
                    if gid not in cache:
                        cache[gid] = cells_of(glyf[order[gid]], glyf, grid)
                    placed.append(
                        {
                            (c * k + i + sx // unit, r * k + j + sy // unit)
                            for c, r in cache[gid]
                            for i in range(k)
                            for j in range(k)
                        }
                    )
                allowed = direction == "ttb" and (grid, text) in OVERLAPPING
                if placed[0] & placed[1] and not allowed:
                    problems.add(f"{text} {direction}")
    return (
        [f"{path.name}: brackets run into each other: {', '.join(sorted(problems))}"]
        if problems
        else []
    )


def check_order():
    """Which of two kanji drawn apart takes which cells does not depend on
    the order of the glyphs of the font: 土 and 士, 杮 and 柿, 未 and 末,
    in a font of the two, in both orders, and each alone: they come out
    unlike, the same in both orders, and one of them as it does alone."""
    problems = []
    for pair in ("土士", "杮柿", "未末"):
        for style in ("Regular", "Bold"):
            weight = STYLES[style]["weight"]
            for grid in (g for g in (50, 70, 100) if light(weight, g)):
                made = {}
                for order in (pair, pair[::-1], pair[0], pair[1]):
                    stands = _alone(noto_glyphs(NOTO_WEIGHT[weight], pair), order)
                    lighter = noto_glyphs(noto_weight(weight, grid), pair)
                    font = build.lighten(
                        _alone(noto_glyphs(NOTO_WEIGHT[weight], pair), order), lighter
                    )
                    pixelate_font(font, grid, phased=True, stands=stands, log=lambda *_: None)
                    glyf, cmap = font["glyf"], font.getBestCmap()
                    made[order] = {
                        c: tuple(sorted(cells_of(glyf[cmap[ord(c)]], glyf, grid))) for c in order
                    }
                name = f"{pair} {style} {grid}"
                if made[pair] != made[pair[::-1]]:
                    problems.append(f"{name}: placed otherwise in the other order")
                if made[pair][pair[0]] == made[pair][pair[1]]:
                    problems.append(f"{name}: come out alike")
                if all(made[pair][c] != made[c][c] for c in pair):
                    problems.append(f"{name}: neither placed as alone")
    return problems


def _alone(font, chars):
    """`font` cut down to `chars`, its glyphs in their order, without layout."""
    options = subset.Options()
    options.layout_features = []
    options.glyph_names = True
    options.notdef_outline = True
    options.drop_tables += ["GSUB", "GPOS", "GDEF", "BASE"]
    s = subset.Subsetter(options)
    s.populate(text=chars)
    s.subset(font)
    cmap = font.getBestCmap()
    order = [".notdef", *(cmap[ord(c)] for c in chars)]
    font["glyf"].glyphOrder = order
    font.setGlyphOrder(order)
    data = io.BytesIO()
    font.save(data)
    data.seek(0)
    return TTFont(data)


def check_reference():
    """review.py's reference for the Japanese: none until --before names
    built fonts, then a copy of them, with where they came from, when, and
    a hash (the one for text before too), read from the noto tab's former
    record as well; and a change of a vertical form alone shows as a
    change."""
    import review

    fonts = sorted(DIST.glob("ttf/Kuronuri*-Regular.ttf"))
    if not fonts:
        return []
    problems = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        review.SNAPSHOT = tmp / "before"
        review.RECORD, review.LEGACY = tmp / "before.json", tmp / "before.txt"
        review.INK = review.SNAPSHOT / "reference.json"
        if review.reference() is not None:
            problems.append("review.py: a reference before --before")
        built = tmp / "built"
        built.mkdir()
        shutil.copy(fonts[0], built)
        review.snapshot(built)
        ref = review.reference()
        if not ref or ref["source"] != str(built.resolve()) or not ref["hash"] or not ref["taken"]:
            problems.append("review.py: --before keeps no record of where its fonts came from")
        if not ref or fonts[0].stem not in ref["fonts"]:
            problems.append("review.py: --before copies no font")
        review.RECORD.unlink()
        ink = {
            "from": "x",
            "at": "2026-01-01 00:00:00 +0900",
            "hash": "abc",
            "fonts": [fonts[0].stem],
        }
        review.INK.write_text(json.dumps(ink))
        ref = review.reference()
        if not ref or ref["hash"] != "abc" or fonts[0].stem not in ref["fonts"]:
            problems.append("review.py: the noto tab's former record is not read")
        font = TTFont(fonts[0])
        vertical = shape(fonts[0], "「", direction="ttb")[0][0]
        name = font.getGlyphName(vertical)
        if name == font.getBestCmap()[ord("「")]:
            return problems + [f"{fonts[0].name}: 「 has no vertical form"]
        vadv, tsb = font["vmtx"][name]
        font["vmtx"][name] = (vadv, tsb + 100)
        font.save(tmp / "moved.ttf")
        same, moved = (
            review.japanese_font(f, tmp / f"{k}.woff2", {ord("「")})
            for k, f in enumerate((fonts[0], tmp / "moved.ttf"))
        )
        if same == moved:
            problems.append("review.py: a vertical form moved does not show as changed")
    return problems


def main():
    fonts = sorted(DIST.glob("ttf/*.ttf")) + sorted(DIST.glob("woff2/*.woff2"))
    if not fonts:
        sys.exit("no fonts in dist/, run the build first")
    if "--pictures" in sys.argv:  # the Greek letters as they are now: looked at, kept
        return write_pictures(sorted(DIST.glob("ttf/*.ttf")))
    with ProcessPoolExecutor() as ex:
        problems = [p for font in ex.map(check_font, fonts) for p in font]
    problems += check_web()
    problems += check_hand()
    problems += check_grown()
    problems += check_shipped()
    problems += check_japanese()
    problems += check_reference()
    problems += check_review()
    for p in problems:
        print("FAIL", p)
    slices = len(list((DIST / "web" / "files").iterdir()))
    print(f"{len(fonts)} fonts, {slices} slices: {len(problems)} problems")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
