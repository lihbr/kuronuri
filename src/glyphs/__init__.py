"""Glyphs drawn for Kuronuri from Redaction's own, for characters it lacks.

Each module draws a group of glyphs, has a `CODEPOINTS` dict (code point:
glyph name), `ALTERNATES`, the names of drawn glyphs without a code
point, `SAMPLES` to review them in context, and an `add_glyphs(font,
smooth, grid)` that adds them to `font`, a Redaction style or one of
Redaction 10 to 100 on `grid`, drawing from `smooth`, the same style
without a grid. `FEATURES`, if any, are those its samples need on. They run
in the order of `MODULES`: later ones may build on glyphs added by earlier
ones. A module's `finish(font, smooth, grid)`, if any, runs once all have
added theirs.
"""

import layout

from . import (
    arrows,
    enclosed,
    figures,
    fullwidth,
    greek,
    japanese,
    letterlike,
    letters,
    maths,
    mended,
    numerals,
    ordinals,
    punctuation,
    signs,
    small,
    spaces,
    squared,
    symbols,
)

MODULES = [
    arrows,
    letters,
    letterlike,
    signs,
    maths,
    greek,  # after maths: Δ is its ∆
    symbols,
    punctuation,
    spaces,
    mended,  # before fullwidth: ￨ is made of |
    ordinals,  # before figures: ℀ ℅ are made of ª º
    figures,
    fullwidth,
    small,
    numerals,
    enclosed,
    japanese,
    squared,
]
CODEPOINTS = {cp: name for m in MODULES for cp, name in m.CODEPOINTS.items()}


def add_glyphs(font, smooth, grid=None):
    for m in MODULES:
        m.add_glyphs(font, smooth, grid)
    for m in MODULES:  # once every glyph is there: greek sets apart the pairs that meet
        if hasattr(m, "finish"):
            m.finish(font, smooth, grid)


# Features shared by every script and language system (layout.share_features):
# those of Redaction and the drawn glyphs, digits and punctuation being of
# the script of the text around them, and the width forms
SHARED = {
    "GSUB": {"calt", "dnom", "frac", "numr", "ordn", "sinf", "ss01", "subs", "sups", "tnum"}
    | {"fwid", "hwid", "pwid"},
    "GPOS": {"frac", "kern"},
}


def add_features(font):
    """Add the features of the modules that have some (calt, ss01, the width
    forms) to the merged font, and share them and those added before the
    merge with the scripts and language systems Noto Serif JP brings."""
    for m in MODULES:
        if hasattr(m, "add_features"):
            m.add_features(font)
    for tag, features in SHARED.items():
        layout.share_features(font[tag].table, features)
