#!/usr/bin/env python3
"""Review the glyphs drawn by draw.py, in every variant and style.

Draws the fonts, then writes .tmp/review: the fonts, with the features the
build adds, and review.json, what the site's /review page shows (`pnpm dev`,
in development only): for each module of glyphs/, a grid of its glyphs and
text to edit, with the features in its `FEATURES` on, set with the built
fonts behind them for everything else.

Glyphs whose outline or advance changed since the fonts were last approved
are listed as changed, and those the approved fonts lack as new. --approve
makes the current fonts the reference (.cache/approved); the first review
approves them. Each module of each font, and its changed glyphs, has a
revision, a hash of its glyphs, so the page can tell which ones were
reviewed before they changed.

.tmp/watch.txt lists glyphs to look at closely, by style: the page shows them
apart, approved, now and over each other, with text to set them in.

usage: review.py [--approve] [--variants base,10,...] [--styles Regular,Italic,Bold]
"""

import argparse
import hashlib
import json
import shutil
import sys
import time
from pathlib import Path

from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._c_m_a_p import cmap_format_12

sys.path.insert(0, str(Path(__file__).resolve().parent))
import draw  # noqa: E402
import glyphs  # noqa: E402
import layout  # noqa: E402
from family import CACHE, GRIDS, ROOT, STYLES, family_name, log, ps_name, variants  # noqa: E402

APPROVED = CACHE / "approved"
OUT = ROOT / ".tmp" / "review"
WATCH = ROOT / ".tmp" / "watch.txt"
PUA = 0xF0000  # review fonts map glyphs without a code point (alternates) from here


def outlines(font):
    """{glyph name: (advance, decomposed outline)}."""
    gs, hmtx = font.getGlyphSet(), font["hmtx"]
    out = {}
    for name in font.getGlyphOrder():
        pen = DecomposingRecordingPen(gs)
        gs[name].draw(pen)
        out[name] = (hmtx[name][0], tuple(pen.value))
    return out


def changes(now, old):
    """Names of the glyphs of `now` that differ from those of `old`, and of
    those it does not have, both outlines()."""
    return {n for n, v in now.items() if n in old and old[n] != v}, set(now) - set(old)


def alternates(font):
    """{PUA code point: glyph name} for the drawn glyphs without a code
    point (stylistic alternates), so the review can show them."""
    names = [n for m in glyphs.MODULES for n in m.ALTERNATES]
    return {PUA + i: n for i, n in enumerate(names) if n in font.getGlyphOrder()}


def characters(font):
    """{glyph name: character}, alternates included."""
    chars = {}
    for cp, name in sorted({**font.getBestCmap(), **alternates(font)}.items()):
        chars.setdefault(name, chr(cp))
    return chars


def revision(now, names):
    """A hash of the glyphs `names` of `now`, an outlines(): what the page
    keeps when they are reviewed, until it changes."""
    return hashlib.sha1(repr([now.get(n) for n in names]).encode()).hexdigest()


def watch():
    """{style or "*": characters} of .tmp/watch.txt, and its text, if any: lines
    "Style: characters" ("*" for every style) and "text: ...", after #
    comments. Spaces between characters are ignored."""
    styles, text = {}, ""
    lines = WATCH.read_text().splitlines() if WATCH.exists() else []
    for line in lines:
        key, _, value = line.split("#")[0].partition(":")
        if key.strip() == "text":
            text = value.strip()
        elif value.strip():
            styles[key.strip()] = styles.get(key.strip(), "") + "".join(value.split())
    return styles, text


def review_font(src, dst, features=True):
    """Copy a drawn font, with the features the build adds (-> to →) and its
    alternates mapped. Approved fonts may predate the glyphs features need:
    they only show glyphs alone, without them."""
    font = TTFont(src)
    if features:
        glyphs.add_features(font)
        for tag in ("GSUB", "GPOS"):
            layout.sort_features(font[tag].table)
    table = cmap_format_12(12)
    table.platformID, table.platEncID, table.language = 3, 10, 0
    table.cmap = {**font.getBestCmap(), **alternates(font)}
    font["cmap"].tables = [t for t in font["cmap"].tables if t.format == 4] + [table]
    font.save(dst)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--approve", action="store_true", help="approve the drawn fonts")
    ap.add_argument("--variants", default="base," + ",".join(map(str, GRIDS)))
    ap.add_argument("--styles", default=",".join(STYLES))
    args = ap.parse_args()
    grids, styles = variants(args.variants), args.styles.split(",")
    draw.draw_all(grids, styles)
    APPROVED.mkdir(parents=True, exist_ok=True)
    shutil.rmtree(OUT, ignore_errors=True)
    (OUT / "fonts" / "approved").mkdir(parents=True)

    members = {  # module name: its glyph names
        m.__name__.split(".")[-1]: [*m.CODEPOINTS.values(), *m.ALTERNATES] for m in glyphs.MODULES
    }
    drawn = [n for names in members.values() for n in names]
    watched, text = watch()
    fonts, widest = [], {}  # glyph name: widest advance in any font, in em
    for style in styles:
        for grid in grids:
            ps = ps_name(grid, style)
            src, ref = draw.path(grid, style), APPROVED / f"{ps}.ttf"
            if args.approve or not ref.exists():
                shutil.copy(src, ref)
            font = TTFont(src)
            now = outlines(font)
            changed, new = changes(now, outlines(TTFont(ref)))
            review_font(src, OUT / "fonts" / f"{ps}.ttf")
            review_font(ref, OUT / "fonts" / "approved" / f"{ps}.ttf", features=False)
            chars = characters(font)
            changed = [n for n in chars if n in changed]  # in the order of the font
            cmap = font.getBestCmap()
            names = (cmap.get(ord(c)) for c in watched.get("*", "") + watched.get(style, ""))
            watching = list(dict.fromkeys(n for n in names if n in chars))  # in its order
            for n in drawn:
                if n in chars:
                    em = font["hmtx"][n][0] / font["head"].unitsPerEm
                    widest[n] = max(widest.get(n, 0), em)
            fonts.append(
                {
                    "name": ps,
                    "grid": grid,
                    "style": style,
                    "family": family_name(grid),  # of the built fonts, for the rest
                    "weight": STYLES[style]["weight"],
                    "italic": STYLES[style]["italic"],
                    # of the glyphs it shows: drawn, changed or new
                    "characters": {
                        n: c for n, c in chars.items() if n in {*drawn, *changed, *new, *watching}
                    },
                    "changed": changed,
                    "watch": watching,
                    "new": [n for n in chars if n in new],
                    "revisions": {
                        module: revision(now, names)
                        for module, names in {
                            **members,
                            "changed": changed,
                            "watch": watching,
                        }.items()
                    },
                }
            )

    modules = [
        {
            "name": name,
            "about": " ".join(m.__doc__.strip().split("\n\n")[0].split()),
            "samples": m.SAMPLES,
            "features": getattr(m, "FEATURES", []),
            "glyphs": members[name],
            "width": max(widest.get(n, 0) for n in members[name]),
        }
        for m, name in zip(glyphs.MODULES, members)
    ]
    review = {
        "version": int(time.time() * 1000),
        "fonts": fonts,
        "modules": modules,
        "watch": text,
    }
    (OUT / "review.json").write_text(json.dumps(review, ensure_ascii=False, indent="\t"))
    log(
        f"{sum(len(f['changed']) for f in fonts)} glyphs changed, "
        f"{sum(len(f['new']) for f in fonts)} new since approved"
    )
    log("http://localhost:3000/review (pnpm dev)")


if __name__ == "__main__":
    main()
