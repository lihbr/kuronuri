"""Double punctuation drawn from Redaction's own: ‼ ⁇ ⁈ ⁉.

Each is Redaction's ! and ? as typed, kerning included (components), as the
Roman numerals are, so in the numbered variants they keep MCKL's pixels.
"""

from .shapes import add, shaper, typed

# code point: the marks it is made of
SOURCES = {0x203C: "!!", 0x2047: "??", 0x2048: "?!", 0x2049: "!?"}
CODEPOINTS = {cp: f"uni{cp:04X}" for cp in SOURCES}
ALTERNATES = []
SAMPLES = ["‼ ⁇ ⁈ ⁉", "Quoi‼ Où⁇ Vraiment⁈ Non⁉", "!! ?? ?! !?"]


def add_glyphs(font, smooth, grid=None):
    s = shaper(font)
    glyphs = {CODEPOINTS[cp]: typed(font, s, marks, grid) for cp, marks in SOURCES.items()}
    add(font, glyphs, CODEPOINTS)
