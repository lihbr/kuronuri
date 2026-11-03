"""Glyphs drawn for Kuronuri from Redaction's own, for characters it lacks.

Each module draws a group of glyphs, has a `CODEPOINTS` dict (code point:
glyph name), `ALTERNATES`, the names of drawn glyphs without a code
point, `SAMPLES` to review them in context, and an `add_glyphs(font,
smooth, grid)` that adds them to `font`, a Redaction style or one of
Redaction 10 to 100 on `grid`, drawing from `smooth`, the same style
without a grid. `FEATURES`, if any, are those its samples need on. They run
in the order of `MODULES`: later ones may build on glyphs added by earlier
ones.
"""

from . import (
    arrows,
    enclosed,
    figures,
    fullwidth,
    japanese,
    letterlike,
    letters,
    maths,
    numerals,
    ordinals,
    punctuation,
    signs,
    small,
    squared,
    symbols,
)

MODULES = [
    arrows,
    letters,
    letterlike,
    signs,
    maths,
    symbols,
    punctuation,
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


def add_features(font):
    """Add the features of the modules that have some (calt, ss01) to the
    merged font."""
    for m in MODULES:
        if hasattr(m, "add_features"):
            m.add_features(font)
