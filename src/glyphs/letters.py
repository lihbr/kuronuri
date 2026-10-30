"""Letters drawn from Redaction's own, for characters it lacks.

ʁ, the r of French in phonetic notation (\\libʁ\\), is Redaction's R turned
upside down and brought to the x-height. Shrunk alone, a capital is lighter
than the lowercase: the R is emboldened first and set a little wider, so the
stems and hairlines of ʁ match those of n, and it is set between the side
bearings of n, tighter in italic. On a grid, where a stem falls
in a cell decides how many cells it takes: ʁ is shifted within a cell to the
spot where its stems pixelate as thick as those of n.
"""

import copy
import statistics

import pathops

import pixel

from .shapes import add, embolden, glyph, path, pixelate_glyphs, runs, slope

EMBOLDEN = 10  # added to each side of the strokes of R, before shrinking it
WIDEN = 1.12  # width over height scale, for vertical stems as thick as in n
SHIFTS = 8  # spots within a cell tried on a grid
ITALIC = 1 / 6  # of the slant times the x-height: taken off the left in italic, 1.5 times the right
CODEPOINTS = {0x0281: "uni0281"}
ALTERNATES = []
SAMPLES = ["\\libʁ\\", "nʁn RʁR"]


def _inverted_r(smooth, height):
    """ʁ from the R of `smooth`, a Redaction style without a grid, standing
    on the baseline and `height` tall."""
    cap, s = smooth["OS/2"].sCapHeight, slope(smooth)
    # Upright and upside down, then emboldened.
    upside_down = embolden(path(smooth, "R", (1, 0, -s, -1, 0, cap)), EMBOLDEN)
    # Shrunk onto the baseline, and slanted again.
    sy = height / (cap + 2 * EMBOLDEN)
    sx, d = sy * WIDEN, EMBOLDEN
    shrunk = upside_down.transform(sx, 0, s * sy, sy, (sx + s * sy) * d, sy * d)
    return glyph(shrunk)


def _path(g):
    p = pathops.Path()
    g.draw(pathops.PathPen(p), None)
    return p


def _strokes(p, height):
    """The widths of the vertical strokes of `p`, a third of `height` from
    its bottom and top."""
    return [b - a for y in (height / 3, height * 2 / 3) for a, b in runs(p, y=y)]


def add_glyphs(font, smooth, grid=None):
    """Add the letters to `font`: a Redaction style, or one of Redaction 10
    to 100 on `grid`. They are drawn from `smooth`, the same style without a
    grid, to the x-height of `font`, and pixelated on a grid."""
    name = CODEPOINTS[0x0281]
    height = font["glyf"][font.getBestCmap()[ord("z")]].yMax
    g = _inverted_r(smooth, height)
    if grid:
        stem = statistics.mode(_strokes(path(font, "n"), height))
        shifted = {}
        for i in range(SHIFTS):
            shifted[i] = copy.deepcopy(g)
            shifted[i].coordinates.translate((round(i * grid / SHIFTS), 0))
        pixelated = pixelate_glyphs(shifted, grid).values()
        g = min(pixelated, key=lambda c: sum(abs(w - stem) for w in _strokes(_path(c), height)))
    # Between the side bearings of n. In italic, its slanted box leaves more room than it looks:
    # tightened, more on the right, where the leg of R turned over leans out at the top
    cmap, hmtx = font.getBestCmap(), font["hmtx"]
    n_advance, n_left = hmtx[cmap[ord("n")]]
    n_right = n_advance - font["glyf"][cmap[ord("n")]].xMax
    tighten = slope(smooth) * height * ITALIC
    if tighten and grid:  # at least a cell, or it would round away
        tighten = max(tighten, grid)
    left = pixel.snap(n_left - tighten, grid or 1)
    g.coordinates.translate((left - g.xMin, 0))
    g.recalcBounds(font["glyf"])
    width = pixel.snap(g.xMax + n_right - 1.5 * tighten, grid or 1)
    add(font, {name: (g, width)}, CODEPOINTS)
