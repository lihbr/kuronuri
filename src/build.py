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

usage: build.py [--variants base,10,...] [--styles Regular,Italic,Bold] [--web-only]
"""

import argparse
import hashlib
import io
import json
import os
import shutil
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

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
    SELECTORS,
    SOURCES,
    STYLES,
    VERSION,
    family_name,
    log,
    ps_name,
    redaction,
    slug,
    subset_options,
    variants,
)

NOTO_VF = SOURCES / "noto-serif-jp" / "NotoSerifJP[wght].ttf"


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


def noto(weight):
    """Noto Serif JP at `weight`, for the Japanese only: without what Redaction
    covers, nor the Latin, Greek and Cyrillic letters and combining accents
    Redaction lacks (Noto's design would not match it), nor Latin ligatures
    (ﬀ), Hangul and Bopomofo. Rebuilt on every run so the pixel cache below
    never sees a stale instance. The glyphs drawn in glyphs/ are cut out at
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
    return path


def noto_pixel(path, grid):
    """The Noto instance at `path` pixelated on `grid`, cached under a hash of
    the instance and of pixel.py."""
    key = hashlib.sha1(path.read_bytes() + Path(pixel.__file__).read_bytes()).hexdigest()[:8]
    out = CACHE / f"{path.stem}-px{grid}-{key}.ttf"
    if not out.exists():
        log(f"pixelating {path.stem} on a {grid}-unit grid")
        for stale in CACHE.glob(f"{path.stem}-px{grid}-*.ttf"):
            stale.unlink()
        pixel.pixelate_font(TTFont(path), grid).save(out)
    return out


def font_version():
    """OpenType versions are <major>.<3 digits>: semver 1.2.3 becomes 1.203,
    the rule Geist uses."""
    major, minor, patch = (int(n) for n in VERSION.split("-")[0].split("."))
    return f"{major}.{minor * 100 + patch:03d}"


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


def assemble(task):
    grid, style, noto_src = task
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
    layout.share_features(font["GSUB"].table, {"tnum", "frac", "numr", "sups"})
    for tag in ("GSUB", "GPOS"):
        layout.sort_features(font[tag].table)  # the merge appends to them
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
    the size of the Latin slices it would load). glyphs.json tells which
    characters are Redaction's, as they are, and which are drawn from them
    (glyphs/): the rest is Noto Serif JP's."""
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
    origins = {
        "redaction": sorted(set(redaction(None, "Regular").getBestCmap()) - set(glyphs.CODEPOINTS)),
        "drawn": sorted(glyphs.CODEPOINTS),
    }
    (out / "glyphs.json").write_text(
        json.dumps({k: "".join(map(chr, cps)) for k, cps in origins.items()}, ensure_ascii=False)
    )
    log(f"writing {len(tasks)} web slices")
    with ProcessPoolExecutor() as ex:
        list(ex.map(web.write_slice, tasks, chunksize=8))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--variants", default="base," + ",".join(map(str, GRIDS)))
    ap.add_argument("--styles", default=",".join(STYLES))
    ap.add_argument("--web-only", action="store_true", help="only redo dist/web from dist/ttf")
    args = ap.parse_args()
    if not args.web_only:
        grids = variants(args.variants)
        styles = args.styles.split(",")
        draw.draw_all(grids, styles)
        notos = {}
        for weight in sorted({NOTO_WEIGHT[STYLES[s]["weight"]] for s in styles}):
            path = noto(weight)
            for grid in grids:
                notos[weight, grid] = path if grid is None else noto_pixel(path, grid)
        tasks = [(g, s, notos[NOTO_WEIGHT[STYLES[s]["weight"]], g]) for g in grids for s in styles]
        (DIST / "ttf").mkdir(parents=True, exist_ok=True)
        (DIST / "woff2").mkdir(exist_ok=True)
        # Each assembly takes about 1.5 GB of memory.
        with ProcessPoolExecutor(4) as ex:
            for ps in ex.map(assemble, tasks):
                log(ps)
    build_web()


if __name__ == "__main__":
    main()
