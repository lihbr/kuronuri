"""What the family is made of, shared by draw.py, build.py and review.py: its
variants and styles, their names, and the sources."""

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
# Noto Serif JP weight paired with each Redaction weight, matched on stem width.
NOTO_WEIGHT = {400: 500, 700: 800}
# Variation selectors: a kanji followed by one asks for a variant of it (葛 and
# U+E0100), what Noto Serif JP's cmap 14 maps. Subsetting keeps a variation
# sequence only when its selector is asked for too.
SELECTORS = {*range(0xFE00, 0xFE10), *range(0xE0100, 0xE01F0)}


def log(*args):
    print(time.strftime("%H:%M:%S"), *args, flush=True)


def family_name(grid, family=FAMILY):
    return family if grid is None else f"{family} {grid}"


def ps_name(grid, style):
    return f"{family_name(grid).replace(' ', '')}-{style}"


def slug(grid):
    return family_name(grid).lower().replace(" ", "-")


def variants(arg):
    """Grids from a --variants argument: "base,10,..."; base is None."""
    return [None if v == "base" else int(v) for v in arg.split(",")]


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
    key = f"{''.join(f'{ord(c):x}' for c in sorted(set(text)))}-{stat.st_size}-{stat.st_mtime_ns}"
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
