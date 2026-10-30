"""Roman numerals drawn from Redaction's letters: Ⅻ is X, I and I.

Each is made of Redaction's own glyphs (components), set as they would be
typed, kerning included, so in the numbered variants they keep MCKL's
pixels. They are as wide as the letters, not squeezed into an em as
Japanese fonts do: that would distort the letters.
"""

from .shapes import add, shaper, typed

UPPER = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]
# code point: the letters it is made of
SOURCES = {0x2160 + i: s for i, s in enumerate(UPPER)} | {
    0x2170 + i: s.lower() for i, s in enumerate(UPPER)
}
CODEPOINTS = {cp: f"uni{cp:04X}" for cp in SOURCES}
ALTERNATES = []
SAMPLES = ["ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩⅪⅫ", "ⅰⅱⅲⅳⅴⅵⅶⅷⅸⅹⅺⅻ", "Ⅻ XII ⅻ xii", "第Ⅲ章", "Louis ⅩⅣ"]


def add_glyphs(font, smooth, grid=None):
    s = shaper(font)
    glyphs = {CODEPOINTS[cp]: typed(font, s, letters, grid) for cp, letters in SOURCES.items()}
    add(font, glyphs, CODEPOINTS)
