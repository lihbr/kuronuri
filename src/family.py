"""What the family is made of, shared by draw.py, build.py and review.py: its
variants and styles, their names, and the sources."""

import hashlib
import json
import os
import time
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / ".cache"
SOURCES = CACHE / "sources"
DIST = ROOT / "dist"

FAMILY = "Kuronuri"
FAMILY_JA = "黒塗り"  # shown by apps in a Japanese locale
VERSION = json.loads((ROOT / "package.json").read_text())["version"]
GRIDS = [10, 20, 35, 50, 70, 100]
# The styles Redaction has (there is no Bold Italic).
STYLES = {
    "Regular": dict(weight=400, italic=False),
    "Italic": dict(weight=400, italic=True),
    "Bold": dict(weight=700, italic=False),
}
# Noto Serif JP weight paired with each Redaction weight, matched on stem width:
# its metrics, punctuation and symbols on every grid...
NOTO_WEIGHT = {400: 500, 700: 800}
# ...and its kanji and kana in Regular and Italic but on the coarse grids,
# from pixel.PHASED, where they are lighter (light): there each of Noto's
# hairlines fills a whole cell, and a kanji, with many more strokes than a
# letter, comes out darker than the Latin beside it; lighter, its stems take
# a cell less on 50, where dense kanji close their counters first. Bold's
# stay 800, as dark as the Latin bold beside them: 700, they no longer read
# bold.
NOTO_LIGHT = {400: 400}
# Variation selectors: a kanji followed by one asks for a variant of it (葛 and
# U+E0100), what Noto Serif JP's cmap 14 maps. Subsetting keeps a variation
# sequence only when its selector is asked for too.
SELECTORS = {*range(0xFE00, 0xFE10), *range(0xE0100, 0xE01F0)}


def light(weight, grid):
    """Whether the kanji and kana set with Redaction's `weight` on `grid`
    (None, smooth) are lightened (NOTO_LIGHT), and so placed by phase, drawn
    by hand where phasing loses them, and followed by their vertical forms
    (pixel.pixelate_font, build.notos): the one place it is decided. If
    not, they are Noto Serif JP of NOTO_WEIGHT, pixelated as they stand."""
    from pixel import PHASED

    return weight in NOTO_LIGHT and grid is not None and grid >= PHASED


def noto_weight(weight, grid):
    """The Noto Serif JP weight of the kanji and kana set with Redaction's
    `weight` on `grid` (light), for the build (build.notos) and the signs
    drawn of Noto's kanji (glyphs/japanese.py)."""
    return (NOTO_LIGHT if light(weight, grid) else NOTO_WEIGHT)[weight]


def log(*args):
    print(time.strftime("%H:%M:%S"), *args, flush=True)


def family_name(grid, family=FAMILY):
    return f"{family} {0 if grid is None else grid}"


def ps_name(grid, style):
    return f"{family_name(grid).replace(' ', '')}-{style}"


def slug(grid):
    return family_name(grid).lower().replace(" ", "-")


def variants(arg):
    """Grids from a --variants argument: "0,10,..."; 0, smooth, is None."""
    return [int(v) or None for v in arg.split(",")]


def subset_options():
    o = subset.Options()
    o.layout_features = ["*"]
    o.layout_scripts = ["*"]
    o.hinting = False
    o.name_IDs = ["*"]
    o.name_languages = ["*"]
    o.notdef_outline = True
    o.glyph_names = True
    o.drop_tables = [t for t in o.drop_tables if t != "BASE"] + ["STAT", "DSIG"]
    return o


def redaction(grid, style):
    """MCKL's webfonts (TrueType outlines, unlike the OTFs in the same zip)."""
    name = "Redaction" if grid is None else f"Redaction_{grid}"
    return TTFont(SOURCES / "redaction" / "webfonts" / f"{name}-{style}.woff2")


def noto_glyphs(weight, text):
    """Noto Serif JP at `weight`, smooth, cut down to `text`: for glyphs drawn
    with some of its own (㋀ is 1 and 月). Cached, it takes seconds."""
    from fontTools.varLib import instancer

    source = SOURCES / "noto-serif-jp" / "NotoSerifJP[wght].ttf"
    stat = source.stat()  # a new source makes a new file
    chars = "".join(f"{ord(c):x}" for c in sorted(set(text)))
    if len(chars) > 64:  # too long a file name: hashed
        chars = hashlib.sha1(chars.encode()).hexdigest()[:16]
    key = f"{chars}-{stat.st_size}-{stat.st_mtime_ns}"
    path = CACHE / f"noto-{weight}-{key}.ttf"
    if not path.exists():
        font = TTFont(source)
        s = subset.Subsetter(subset.Options())
        s.populate(text=text)
        s.subset(font)
        font = instancer.instantiateVariableFont(font, {"wght": weight}, updateFontNames=False)
        CACHE.mkdir(exist_ok=True)
        # Drawn in parallel, every worker wants it: written aside, then moved
        # in whole, so none reads it half written
        part = path.with_name(f"{path.name}.{os.getpid()}")
        font.save(part)
        part.replace(path)
    return TTFont(path)
