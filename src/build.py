#!/usr/bin/env python3
"""Build the Kuronuri font family into dist/.

Kuronuri (黒塗り, "blacked out") = Redaction (Latin, by MCKL) + Noto Serif JP
(Japanese, by Adobe and Google). The numbered variants follow Redaction 10 to
100: every glyph sits on a pixel grid of that many units per 1000-unit em.
Their Latin glyphs come from MCKL's pixel fonts, their Japanese glyphs are
pixelated from Noto Serif JP (pixel.py).

- dist/ttf, dist/woff2: the full fonts, Redaction with the glyphs drawn by
  draw.py merged with Noto Serif JP
- dist/web: the npm package, a CSS file per family and its unicode-range
  slices (web.py)
- site/: what the site needs from the fonts, versioned, so it deploys
  without building them

usage: build.py [--variants 0,10,...] [--styles Regular,Italic,Bold] [--web-only]
"""

import argparse
import functools
import hashlib
import inspect
import io
import json
import math
import os
import shutil
import statistics
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import fontTools
from fontTools import subset
from fontTools.merge import Merger
from fontTools.merge import Options as MergeOptions
from fontTools.misc.timeTools import epoch_diff
from fontTools.otlLib.maxContextCalc import maxCtxFont
from fontTools.ttLib import TTFont, newTable
from fontTools.unicodedata import script
from fontTools.varLib import instancer

sys.path.insert(0, str(Path(__file__).resolve().parent))
import draw  # noqa: E402
import family  # noqa: E402
import glyphs  # noqa: E402
import layout  # noqa: E402
import pixel  # noqa: E402
import web  # noqa: E402
from family import (  # noqa: E402
    CACHE,
    DIST,
    FAMILY_JA,
    GRIDS,
    NOTO_WEIGHT,
    ROOT,
    SELECTORS,
    SOURCES,
    STYLES,
    VERSION,
    family_name,
    log,
    noto_weight,
    ps_name,
    redaction,
    slug,
    subset_options,
    variants,
)
from glyphs import shapes  # noqa: E402
from glyphs.shapes import drawn_cells  # noqa: E402

NOTO_VF = SOURCES / "noto-serif-jp" / "NotoSerifJP[wght].ttf"

SITE = ROOT / "site"
# The site's title, drawn in Bold in every family
TITLE = "黒塗りフォント"


NAMES = {
    0: "Copyright 2026 lihbr (Kuronuri). "
    "Copyright 2019 MCKL Inc. (Redaction). "
    "Copyright 2017-2024 Adobe (http://www.adobe.com/) (Noto Serif JP).",
    8: "lihbr",
    9: "lihbr (Kuronuri); Jeremy Mickel / Forest Young (Redaction); "
    "Ryoko Nishizuka (Noto Serif JP kana & ideographs)",
    10: "Kuronuri (黒塗り, blacked out) is Redaction with Japanese support, and more: "
    "Latin from Redaction by MCKL, kana and kanji from Noto Serif JP. Numbered variants "
    "put every glyph on a pixel grid of that many units per em, like Redaction "
    "10 to 100.",
    11: "https://lihbr.com",
    13: "This Font Software is licensed under the SIL Open Font License, Version 1.1. "
    "This license is available with a FAQ at: https://openfontlicense.org",
    14: "https://openfontlicense.org",
}


@functools.cache
def noto(weight):
    """Noto Serif JP at `weight`, for the Japanese only: without what Redaction
    covers, nor the Latin, Greek and Cyrillic letters and combining accents
    Redaction lacks (Noto's design would not match it), nor Latin ligatures
    (ﬀ), Hangul and Bopomofo. Rebuilt on every run (once) so the pixel cache
    below never sees a stale instance. The glyphs drawn in glyphs/ are cut out at
    the merge, so drawing more does not pixelate Noto again."""
    log(f"instancing Noto Serif JP {weight}")
    font = instancer.instantiateVariableFont(
        TTFont(NOTO_VF), {"wght": weight}, updateFontNames=False
    )
    latin = set(redaction(None, "Regular").getBestCmap())
    unicodes = {
        c
        for c in font.getBestCmap()
        if c >= 0x20
        and c not in latin
        and not (c < 0x2000 and script(c) in ("Latn", "Grek", "Cyrl"))
        and not 0x300 <= c <= 0x36F
        and not 0xFB00 <= c <= 0xFB4F
        and script(c) not in ("Hang", "Bopo")
    }
    unicodes |= SELECTORS
    s = subset.Subsetter(subset_options())
    s.populate(unicodes=unicodes)
    s.subset(font)
    CACHE.mkdir(exist_ok=True)
    path = CACHE / f"noto-{weight}.ttf"
    font.recalcTimestamp = False  # same bytes every run, for the cache key
    font.save(path)
    path.with_suffix(".json").write_text(json.dumps({"inputs": instancing(weight)}))
    return path


def instancing(weight):
    """A hash of what the Noto instance at `weight` is made of: the variable
    font, its weight, what noto() keeps of it (its code, Redaction's
    characters, the subsetter's options in family.py, the variation
    selectors) and the fontTools that instances it."""
    key = hashlib.sha1(NOTO_VF.read_bytes())
    key.update(f"{weight} {fontTools.version} {sorted(SELECTORS)}".encode())
    key.update(inspect.getsource(noto).encode())
    key.update(Path(family.__file__).read_bytes())
    key.update(repr(sorted(redaction(None, "Regular").getBestCmap())).encode())
    return key.hexdigest()


def instance(weight, fresh=True):
    """The path of noto(weight): instanced again unless not `fresh` and the
    instance was made of what it would be made of now (instancing, recorded
    beside it)."""
    path, record = CACHE / f"noto-{weight}.ttf", CACHE / f"noto-{weight}.json"
    made = json.loads(record.read_text()).get("inputs") if record.exists() else None
    if fresh or not path.exists() or made != instancing(weight):
        return noto(weight)
    return path


def noto_light(weight, light, fresh=True):
    """Noto Serif JP at `weight`, as noto() makes it, with its kanji and
    kana drawn at `light` (lighten). Returns its path. `fresh` as instance()."""
    font = lighten(TTFont(instance(weight, fresh)), TTFont(instance(light, fresh)))
    path = CACHE / f"noto-{weight}-{light}.ttf"
    font.recalcTimestamp = False  # same bytes every run, for the cache key
    font.save(path)
    return path


def lighten(font, lighter):
    """`font`, a Noto Serif JP instance, with the outlines of its kanji and
    kana (pixel.phased_glyphs) taken from `lighter`, another instance of the
    same glyphs, centred in the advances of `font`, their vertical origins
    kept. Every advance, vertical metric, GPOS value and every other glyph
    stays that of `font`, so lighter kanji change ink, not spacing."""
    glyf, hmtx, vmtx = font["glyf"], font["hmtx"], font["vmtx"]
    for name in pixel.phased_glyphs(font):
        old, new = glyf[name], lighter["glyf"][name]
        if old.numberOfContours <= 0 or new.numberOfContours <= 0:
            continue
        old.recalcBounds(glyf)
        dx = round((hmtx[name][0] - lighter["hmtx"][name][0]) / 2)
        new.coordinates.translate((dx, 0))
        new.recalcBounds(lighter["glyf"])
        vadv, tsb = vmtx[name]
        hmtx[name] = (hmtx[name][0], new.xMin)
        vmtx[name] = (vadv, old.yMax + tsb - new.yMax)
        glyf[name] = new
    return font


def notos(grids, styles, fresh=True):
    """{(Noto weight, grid): path} of the Noto Serif JP the fonts of `grids`
    and `styles` merge, by the weight of their kanji and kana
    (family.noto_weight), pixelated on their grid: noto(), or noto_light()
    where the kanji and kana are lighter. Instanced again unless not `fresh`
    (instance())."""
    out, made = {}, {}
    for weight in sorted({STYLES[s]["weight"] for s in styles}):
        for grid in grids:
            base, kanji = NOTO_WEIGHT[weight], noto_weight(weight, grid)
            if kanji not in made:
                made[kanji] = (
                    instance(base, fresh) if kanji == base else noto_light(base, kanji, fresh)
                )
            if grid is None:
                out[kanji, grid] = made[kanji]
            else:
                stands = instance(base, fresh) if kanji != base else None
                out[kanji, grid] = noto_pixel(made[kanji], grid, stands, pinned(weight, grid))
    return out


def pinned(weight, grid):
    """{code point: cells} of the kanji and kana drawn by hand on `grid`
    (glyphs/drawn/japanese.txt) for the styles of Redaction's `weight`,
    which share their Noto Serif JP: alike in each, or none."""
    out = {}
    for (g, style, char), cells in drawn_cells(pixel.JAPANESE).items():
        if g == grid and STYLES[style]["weight"] == weight:
            if (out.setdefault(ord(char), cells).at, out[ord(char)]) != (cells.at, cells):
                raise ValueError(f"{char} is drawn otherwise in styles that share Noto on {grid}")
    for style, spec in STYLES.items():
        if spec["weight"] == weight:
            mine = {c for (g, s, c) in drawn_cells(pixel.JAPANESE) if g == grid and s == style}
            if mine != {chr(cp) for cp in out}:
                raise ValueError(f"{style} on {grid} lacks a glyph of japanese.txt its Noto has")
    return out


def noto_pixel(path, grid, stands=None, cells=None):
    """The Noto instance at `path` pixelated on `grid`, its kanji and kana
    placed by phase on the rows of those of the instance at `stands`
    (pixel.pixelate_font), but those drawn by hand, `cells` ({code point:
    cells}), cached under a hash of the instances, the cells and pixel.py."""
    source = path.read_bytes() + (stands.read_bytes() if stands else b"")
    source += repr(sorted((cp, list(c), c.at) for cp, c in (cells or {}).items())).encode()
    key = hashlib.sha1(source + Path(pixel.__file__).read_bytes()).hexdigest()[:8]
    out = CACHE / f"{path.stem}-px{grid}-{key}.ttf"
    if not out.exists():
        log(f"pixelating {path.stem} on a {grid}-unit grid")
        for stale in CACHE.glob(f"{path.stem}-px{grid}-*.ttf"):
            stale.unlink()
        reference = TTFont(stands) if stands else None
        pixel.pixelate_font(
            TTFont(path), grid, phased=True, stands=reference, pinned=cells, log=log
        ).save(out)
    return out


def font_version():
    """OpenType versions are <major>.<3 digits>: semver 1.2.3 becomes 1.203,
    the rule Geist uses."""
    major, minor, patch = (int(n) for n in VERSION.split("-")[0].split("."))
    return f"{major}.{minor * 100 + patch:03d}"


# Redaction Italic's straight stems, its slant measured on them; and what
# its caret offset is measured on
STEMS = "EHIL"
SPACED = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


@functools.cache
def slant():
    """Redaction Italic's slant, which its fonts do not declare (an italic
    angle of 0, an upright caret): its angle in degrees, measured on the
    left stems of STEMS, from a quarter to three quarters of their height,
    clear of serifs, rounded to a tenth; and how far the caret, slanted so
    from the start of a glyph on the baseline, is moved to fall midway
    between glyphs, as their side bearings along the slant are (SPACED).
    Measured smooth, for every variant: the pixel ones are of it."""
    font = redaction(None, "Italic")
    slopes = []
    for c in STEMS:
        p = shapes.path(font, c)
        top = p.bounds[3]
        (a, b), (c0, c1) = shapes.runs(p, y=top / 4)[0], shapes.runs(p, y=top * 3 / 4)[0]
        slopes.append(((c0 + c1) - (a + b)) / 2 / (top / 2))
    angle = round(math.degrees(math.atan(statistics.median(slopes))), 1)
    run = math.tan(math.radians(angle))
    hmtx, cmap, offsets = font["hmtx"], font.getBestCmap(), []
    for c in SPACED:
        x0, _, x1, _ = shapes.path(font, c, (1, 0, -run, 1, 0, 0)).bounds  # unslanted
        offsets.append((x0 - (hmtx[cmap[ord(c)]][0] - x1)) / 2)
    return angle, round(statistics.median(offsets))


def set_metadata(font, grid, style):
    st = STYLES[style]
    bold, italic = st["weight"] == 700, st["italic"]
    ps = ps_name(grid, style)
    name = font["name"]
    name.names = [n for n in name.names if n.nameID > 255]  # feature names
    for nid, val in {
        **NAMES,
        1: family_name(grid),
        2: style,
        3: f"{VERSION};NONE;{ps}",
        4: family_name(grid) if style == "Regular" else f"{family_name(grid)} {style}",
        5: f"Version {font_version()}; {VERSION}",
        6: ps,
    }.items():
        name.setName(val, nid, 3, 1, 0x409)
    fam_ja = family_name(grid, FAMILY_JA)
    for nid, val in {
        1: fam_ja,
        2: style,
        4: fam_ja if style == "Regular" else f"{fam_ja} {style}",
    }.items():
        name.setName(val, nid, 3, 1, 0x411)

    os2 = font["OS/2"]
    os2.version = 4
    os2.usWeightClass = st["weight"]
    os2.fsSelection = (0x20 if bold else 0) | (0x01 if italic else 0) or 0x40
    os2.fsType = 0
    os2.achVendID = "NONE"
    os2.recalcUnicodeRanges(font)
    os2.recalcCodePageRanges(font)
    os2.recalcAvgCharWidth(font)
    cps = font.getBestCmap().keys()
    os2.usFirstCharIndex, os2.usLastCharIndex = min(cps), min(max(cps), 0xFFFF)
    os2.usMaxContext = maxCtxFont(font)

    head = font["head"]
    head.fontRevision = float(font_version())
    head.macStyle = (1 if bold else 0) | (2 if italic else 0)
    head.flags = 0b11
    stamp = int(os.environ.get("SOURCE_DATE_EPOCH", time.time()))
    head.created = head.modified = stamp - epoch_diff
    font.recalcTimestamp = False

    font["post"].formatType = 3.0  # no glyph names, as in Noto: saves space
    if italic:  # the Latin slants, the Japanese stands upright
        angle, offset = slant()
        font["post"].italicAngle = -angle
        hhea = font["hhea"]
        hhea.caretSlopeRise = head.unitsPerEm
        hhea.caretSlopeRun = round(head.unitsPerEm * math.tan(math.radians(angle)))
        hhea.caretOffset = offset
    font["gasp"] = gasp = newTable("gasp")
    gasp.version = 1
    gasp.gaspRange = {0xFFFF: 0x000F}


def without_drawn(path):
    """The Noto at `path` without the characters drawn in glyphs/, which
    would otherwise be in the merge twice, its variation sequences kept."""
    font = TTFont(path)
    s = subset.Subsetter(subset_options())
    s.populate(unicodes=(set(font.getBestCmap()) - set(glyphs.CODEPOINTS)) | SELECTORS)
    s.subset(font)
    buf = io.BytesIO()
    font.save(buf)
    buf.seek(0)
    return buf


METRICS = {
    "hhea": ("ascent", "descent", "lineGap"),
    "OS/2": ("sTypoAscender", "sTypoDescender", "sTypoLineGap", "usWinAscent", "usWinDescent"),
}


def restore_metrics(font, source):
    """Sets the vertical metrics of `font` to those of `source`."""
    for tag, attrs in METRICS.items():
        for attr in attrs:
            setattr(font[tag], attr, getattr(source[tag], attr))


def merged(grid, style, noto_src):
    """The drawn font of `grid` and `style` merged with the Noto at
    `noto_src`, with its features: the built font, but for its metadata,
    which shaping does not read. review.py sets text in it."""
    font = Merger(options=MergeOptions(drop_tables=[])).merge(
        [str(draw.path(grid, style)), without_drawn(noto_src)]
    )
    # The merge keeps the larger of each vertical metric, Noto's 1151 ascent,
    # which moves the baseline down in a line box. Redaction's 900/-300 holds
    # Noto's ideographic em box (-120..880).
    restore_metrics(font, TTFont(draw.path(grid, style)))
    # Noto's BASE gives the ideographic em box (-120..880) for every script.
    font["BASE"] = TTFont(noto_src)["BASE"]
    glyphs.add_features(font)
    for tag in ("GSUB", "GPOS"):
        layout.sort_features(font[tag].table)  # the merge appends to them
    return font


def assemble(task):
    grid, style, noto_src = task
    font = merged(grid, style, noto_src)
    set_metadata(font, grid, style)
    ps = ps_name(grid, style)
    font.save(DIST / "ttf" / f"{ps}.ttf")
    font.flavor = "woff2"
    font.save(DIST / "woff2" / f"{ps}.woff2")
    return ps


def build_web():
    """Slice every font in dist/ttf into dist/web, the npm package, laid out
    like a fontsource package: files/ and, per family, a CSS file and a
    Latin-only one for pages without Japanese (the full one is ten times
    the size of the Latin slices it would load)."""
    out = DIST / "web"
    shutil.rmtree(out, ignore_errors=True)
    (out / "files").mkdir(parents=True)
    tasks, families = [], []
    for grid in [None, *GRIDS]:
        faces, latin = [], []
        for style, st in STYLES.items():
            ttf = DIST / "ttf" / f"{ps_name(grid, style)}.ttf"
            if not ttf.exists():
                continue
            css_style = "italic" if st["italic"] else "normal"
            for name, cps in web.plan(TTFont(ttf).getBestCmap()):
                file = f"files/{slug(grid)}-{name}-{st['weight']}-{css_style}.woff2"
                tasks.append((str(ttf), str(out / file), cps))
                face = web.font_face(family_name(grid), css_style, st["weight"], file, cps)
                faces.append(face)
                if name in ("latin", "latin-ext"):
                    latin.append(face)
        if not faces:
            continue
        families.append(f"{slug(grid)}.css")
        (out / families[-1]).write_text("\n".join(faces))
        (out / f"{slug(grid)}-latin.css").write_text("\n".join(latin))
    (out / "index.css").write_text("".join(f'@import "./{f}";\n' for f in families))
    log(f"writing {len(tasks)} web slices")
    with ProcessPoolExecutor() as ex:
        list(ex.map(web.write_slice, tasks, chunksize=8))


def build_site():
    """Write what the site needs from the fonts into site/, versioned so it
    deploys without building them: app/assets/title/, its title as an SVG
    per family, by grid (0 for the base family), to inline and paint without
    the Japanese slices it would need; server/data/glyphs.json, which characters are
    Redaction's, as they are, and which are drawn from them (glyphs/), the
    rest being Noto Serif JP's."""
    title = SITE / "app" / "assets" / "title"
    title.mkdir(parents=True, exist_ok=True)
    for grid in [None, *GRIDS]:
        ttf = DIST / "ttf" / f"{ps_name(grid, 'Bold')}.ttf"
        if ttf.exists():
            (title / f"{grid or 0}.svg").write_text(web.outline(ttf, TITLE))
    origins = {
        "redaction": sorted(set(redaction(None, "Regular").getBestCmap()) - set(glyphs.CODEPOINTS)),
        "drawn": sorted(glyphs.CODEPOINTS),
    }
    data = SITE / "server" / "data"
    data.mkdir(parents=True, exist_ok=True)
    (data / "glyphs.json").write_text(
        json.dumps({k: "".join(map(chr, cps)) for k, cps in origins.items()}, ensure_ascii=False)
        + "\n"
    )


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--variants", default="0," + ",".join(map(str, GRIDS)))
    ap.add_argument("--styles", default=",".join(STYLES))
    ap.add_argument(
        "--web-only", action="store_true", help="only redo dist/web and site/ from dist/ttf"
    )
    args = ap.parse_args()
    if not args.web_only:
        grids = variants(args.variants)
        styles = args.styles.split(",")
        draw.draw_all(grids, styles)
        src = notos(grids, styles)
        tasks = [(g, s, src[noto_weight(STYLES[s]["weight"], g), g]) for g in grids for s in styles]
        (DIST / "ttf").mkdir(parents=True, exist_ok=True)
        (DIST / "woff2").mkdir(exist_ok=True)
        # Each assembly takes about 1.5 GB of memory.
        with ProcessPoolExecutor(4) as ex:
            for ps in ex.map(assemble, tasks):
                log(ps)
    build_web()
    build_site()


if __name__ == "__main__":
    main()
