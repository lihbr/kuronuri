"""Squared Latin words of Unicode: units (㎏ ㎍ ㏄ ㎖ ㏀), ㍱ ㋌ ㋍ and the
like, which Japanese text sets an em each.

Set as Japanese signs are (japanese.py, ㋀): Redaction's letters as typed,
kerning included, and μ of letterlike.py, ℓ Ω of Noto Serif JP as tall as
Redaction's (letterlike.add_noto), only scaled: all at the same size, as
tall as Noto Serif JP's are, Redaction's descender to its ascender as
Noto Serif JP's are from its ㎏'s g to its k (TALL), on the baseline, and
narrowed when a word would not fit in the em (BOX), centred in it. Neither
thickened nor thinned, Redaction's carving is its own, scaled. Pixelated
on a grid.
"""

import unicodedata

import pixel
from family import redaction

from .japanese import BOX
from .letterlike import CODEPOINTS as LETTERS
from .letterlike import NOTO
from .shapes import add, content, glyph, path, pixelate_glyphs, shaper, with_letters


def _squared():
    """{code point: text} of the squared Latin words of Unicode (㎏ ㍱ ㋌)
    whose letters Redaction all has, or letterlike.py draws (μ ℓ Ω): as
    decomposed, ∕ as /."""
    letters = set(redaction(None, "Regular").getBestCmap()) | set(LETTERS) | set(NOTO)
    squared = {}
    for cp in [0x3250, *range(0x32CC, 0x32D0), *range(0x3371, 0x33E0), 0x33FF]:
        tag, *parts = unicodedata.decomposition(chr(cp)).split() or [""]
        text = "".join(chr(int(c, 16)) for c in parts).replace("∕", "/")
        if tag == "<square>" and all(ord(c) in letters for c in text):
            squared[cp] = text
    return squared


SQUARED = _squared()
CODEPOINTS = {cp: f"uni{cp:04X}" for cp in SQUARED}
ALTERNATES = []
SAMPLES = [
    "㎏㎎㎍㎛㎜㎝㎞",
    "㎖㎗㎘㎕ ㏄㎤㎥",
    "㎂㎃㎄ ㎌㎊ ㎶㎷㎸ ㎼㎽㎾ ㏀㏁㏂",
    "㎈㎉㎐㎑㎒㎓ ㎳㎲ ㏑㏒ ㍱㍲㍳",
    "５㎏ 3㎍ 2㎖ 10㏀ 100㎞",
]
TALL = (-263, 816)  # Noto Serif JP's ㎏, its g's foot and its k's top, over 1000


def add_glyphs(font, smooth, grid=None):
    source = with_letters(smooth["name"].getDebugName(2))
    em = pixel.snap_advance(1000, grid or 1)
    x0, _, x1, _ = (v * em / 1000 for v in BOX)
    # Redaction's descender to ascender, as tall as Noto Serif JP's
    low, high = path(source, "p").bounds[1], path(source, "l").bounds[3]
    scale = (TALL[1] - TALL[0]) * em / 1000 / (high - low)
    s = shaper(source)
    glyphs = {}
    for cp, text in SQUARED.items():
        word = content(source, s, text)
        a, _, b, _ = word.bounds
        across = min(scale, (x1 - x0) / (b - a))  # narrowed to fit
        p = word.transform(across, 0, 0, scale, em / 2 - (a + b) / 2 * across, 0)
        glyphs[CODEPOINTS[cp]] = glyph(p)
    if grid:
        glyphs = pixelate_glyphs(glyphs, grid)
    add(font, {name: (g, em) for name, g in glyphs.items()}, CODEPOINTS)
