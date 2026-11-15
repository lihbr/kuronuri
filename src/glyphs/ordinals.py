"""Ordinals drawn from Redaction's own: ª º, the letters of ordinal suffixes
raised, №, and `ordn` for them.

ª, º and the superscript letters c d e h n r s t (c for ℀ ℅ of
figures.py) are Redaction's letters shrunk as the superscript digits of
figures.py, their x-height at the top of ¹, keeping their carving: in
Regular, Bold's thinned; in Italic and Bold, made heavier as Bold is of
Regular, or grown across only (figures._heavier). On a grid, none comes out
as another. № is N and º, as typed.

`ordn` (font-variant-numeric: ordinal) raises the suffixes of ordinals after
digits, when no letter or digit follows: 1ª 2º, 1st 2nd 3rd 4th, 1er 1re 2e
2nde, but 3am and 2e3 stay as typed. It turns No. before a number into №.
"""

from fontTools.otlLib import builder as otl

import layout

from .figures import superiors
from .shapes import add, shaper, typed

ORDINALS = {0xAA: ("a", "ordfeminine"), 0xBA: ("o", "ordmasculine")}
# Suffixes `ordn` raises after digits: English, French, and Spanish,
# Portuguese and Italian ones
SUFFIXES = ["st", "nd", "rd", "th"]
SUFFIXES += ["er", "ers", "re", "res", "e", "es", "nde", "ndes", "nds"]
SUFFIXES += ["a", "as", "o", "os"]
# Superscript letters: ª º, those of the other suffixes, and c of ℀ ℅,
# placed together so that none comes out as another
LETTERS = {c: name for c, name in ORDINALS.values()}
LETTERS |= {c: f"{c}.superior" for c in sorted(set("".join(SUFFIXES) + "c") - set(LETTERS))}
CODEPOINTS = {cp: name for cp, (_, name) in ORDINALS.items()} | {0x2116: "uni2116"}
ALTERNATES = [name for name in LETTERS.values() if name not in CODEPOINTS.values()]
SAMPLES = [
    "1ª 2º, № 5",
    "1a 2o 3as 4os, 1st 2nd 3rd 4th 11th 21st 102nd, 1er 1re 2e 2nde 1ers",
    "No. 5, No.12, No 5, say No.",
    "as typed: 3am 2e3 2h30 10s 1stuff A4",
    "4th; 4th: 1st, 2nd.",
    "1stと2nd、No. 5の3rd (japanese), 1st 2nd (sups too)",
]
FEATURES = ["ordn"]


def add_glyphs(font, smooth, grid=None):
    ordinals = {cp: name for cp, (_, name) in ORDINALS.items()}
    add(font, superiors(font, smooth, grid, LETTERS), ordinals)
    add(font, {"uni2116": typed(font, shaper(font), "Nº", grid)}, {0x2116: "uni2116"})
    # First, before Redaction's `sups`: 1st with both on would lose its digit
    # to it, and the suffix its context (figures.py puts `frac` before)
    layout.add_feature(font["GSUB"].table, "ordn", _ordn(font), at=2)


def _ordn(font):
    """A lookup raising the suffixes of ordinals after digits (1st, 2e,
    1ª), but not other letters after them (3am, 2e3), longer suffixes
    first, and turning No. before a number into №. The lookups it applies
    are inserted first in the font."""
    gsub, cmap = font["GSUB"].table, font.getBestCmap()
    word = {name for cp, name in cmap.items() if chr(cp).isalnum()}
    digits = {cmap[ord(d)] for d in "0123456789"}

    raise_ = otl.SingleSubstBuilder(font, None)
    raise_.mapping = {cmap[ord(c)]: name for c, name in LETTERS.items() if c != "c"}
    numero = otl.LigatureSubstBuilder(font, None)
    numero.ligatures = {tuple(cmap[ord(c)] for c in "No."): "uni2116"}
    # the first two lookups, the third applying them
    for i, builder in zip(
        layout.insert_lookups(gsub, [raise_.build(), numero.build()], 0), (raise_, numero)
    ):
        builder.lookup_index = i

    ordn = otl.ChainContextSubstBuilder(font, None)
    for suffix in sorted(SUFFIXES, key=len, reverse=True):
        glyphs = [{cmap[ord(c)]} for c in suffix]
        ordn.rules.append(otl.ChainContextualRule([digits], glyphs, [word], [None] * len(glyphs)))
        ordn.rules.append(otl.ChainContextualRule([digits], glyphs, [], [[raise_]] * len(glyphs)))
    no = [{cmap[ord(c)]} for c in "No."]
    spaces = {cmap[cp] for cp in (0x20, 0xA0)}
    ordn.rules.append(otl.ChainContextualRule([word], no, [], [None] * 3))
    for after in ([digits], [spaces, digits]):
        ordn.rules.append(otl.ChainContextualRule([], no, after, [[numero], None, None]))
    return ordn.build()
