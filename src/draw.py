#!/usr/bin/env python3
"""Draw Kuronuri's own glyphs into Redaction, without Noto Serif JP.

Writes .cache/drawn/<font>.ttf: a Redaction style, or one of Redaction 10 to
100, without hinting (it does not survive the merge), with the glyphs of
glyphs/, tabular figures (layout.py) and the vertical metrics the merge
needs. It takes seconds: draw, then review (review.py), then build (build.py,
which draws first).

usage: draw.py [--variants base,10,...] [--styles Regular,Italic,Bold]
"""

import argparse
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from fontTools import subset
from fontTools.fontBuilder import FontBuilder

sys.path.insert(0, str(Path(__file__).resolve().parent))
import glyphs  # noqa: E402
import layout  # noqa: E402
import pixel  # noqa: E402
from family import CACHE, GRIDS, STYLES, log, ps_name, redaction, subset_options, variants  # noqa: E402

DRAWN = CACHE / "drawn"


def path(grid, style):
    return DRAWN / f"{ps_name(grid, style)}.ttf"


def draw(grid, style):
    font = redaction(grid, style)
    font.flavor = None
    s = subset.Subsetter(subset_options())
    s.populate(glyphs=font.getGlyphOrder(), unicodes=font.getBestCmap().keys())
    s.subset(font)
    if grid:
        pixel.snap_outlines(font, grid)
    glyphs.add_glyphs(font, redaction(None, style), grid)
    g = grid or 1
    vadv = pixel.snap_advance(1000, g)
    origin = pixel.snap(pixel.VERT_ORIGIN - (1000 - vadv) / 2, g)
    glyf = font["glyf"]
    fb = FontBuilder(font=font)
    fb.setupVerticalHeader(tableVersion=0x00011000, ascent=500, descent=-500, caretSlopeRun=1)
    fb.setupVerticalMetrics(
        {
            n: (vadv, origin - glyf[n].yMax if glyf[n].numberOfContours else 0)
            for n in font.getGlyphOrder()
        }
    )
    layout.add_tabular_figures(font, grid)
    return font


def _draw(task):
    grid, style = task
    out = path(grid, style)
    draw(grid, style).save(out)
    return out


def draw_all(grids, styles):
    """Draw every style of every grid into .cache/drawn."""
    DRAWN.mkdir(parents=True, exist_ok=True)
    tasks = [(g, s) for g in grids for s in styles]
    with ProcessPoolExecutor() as ex:
        for out in ex.map(_draw, tasks):
            log(f"drew {out.stem}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--variants", default="base," + ",".join(map(str, GRIDS)))
    ap.add_argument("--styles", default=",".join(STYLES))
    args = ap.parse_args()
    draw_all(variants(args.variants), args.styles.split(","))


if __name__ == "__main__":
    main()
