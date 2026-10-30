"""Put glyphs on an N-unit pixel grid, the way Redaction 10 to 100 do.

FreeType renders each glyph anti-aliased, which gives the exact area of each
grid cell that the outline covers. A cell is filled when the outline covers
half of it. A dropout pass then puts back thin strokes (Mincho hairlines)
that fall between cells. Filled cells are traced back into rectilinear
TrueType contours.

build.py caches pixelated fonts under a hash of this file.
"""

import io
from concurrent.futures import ProcessPoolExecutor

import freetype
import numpy as np
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib.tables import otTables as ot
from fontTools.ttLib.tables._g_l_y_f import Glyph
from fontTools.ttLib.tables.otTraverse import dfs_base_table

PPEM = 400  # rendering size: a cell of N units is 0.4 N pixels wide
VERT_ORIGIN = 880  # top of the ideographic em box, the vertical origin
FILL = 0.5  # a cell is filled when the outline covers this much of it
STROKE = 0.5  # a stroke fills this much of a cell column or row...
MIN_STROKE = 0.15  # ...and is this thick, in cells, to be put back by the dropout pass
LOAD_FLAGS = freetype.FT_LOAD_NO_HINTING | freetype.FT_LOAD_RENDER | freetype.FT_LOAD_NO_BITMAP


def snap(value, grid):
    return int(round(value / grid)) * grid


def snap_advance(advance, grid):
    """Round an advance to the grid. Full-width advances round to an even
    number of pixels, because vertical text centres glyphs on half the
    advance (1000 becomes 980 on the 35 and 70 grids)."""
    return snap(advance, 2 * grid if advance == 1000 else grid)


def snap_outlines(font, grid):
    """Round every point, component offset and advance to the grid.

    MCKL's pixel fonts have a few strays: accents placed one unit off the
    grid, a point at 601 instead of 600, spaces of 518 units. Each one shows
    as a hairline sliver or a pixel column out of step."""
    glyf, hmtx = font["glyf"], font["hmtx"]
    names = font.getGlyphOrder()
    for name in names:
        g = glyf[name]
        if g.isComposite():
            for c in g.components:
                c.x, c.y = snap(c.x, grid), snap(c.y, grid)
        elif g.numberOfContours > 0:
            for i, (x, y) in enumerate(g.coordinates):
                g.coordinates[i] = (snap(x, grid), snap(y, grid))
    # Simple glyphs first: composite bounds come from their components.
    for name in sorted(names, key=lambda n: glyf[n].isComposite()):
        g = glyf[name]
        adv, lsb = hmtx[name]
        if g.numberOfContours:
            g.recalcBounds(glyf)
            lsb = g.xMin
        hmtx[name] = (snap(adv, grid), lsb)


def snap_gpos(font, grid):
    """Round every GPOS adjustment and anchor to the grid, so kerning and
    `palt` never knock a glyph off it."""
    if "GPOS" not in font:
        return
    for path in dfs_base_table(font["GPOS"].table):
        table = path[-1].value
        if isinstance(table, ot.Anchor):
            table.XCoordinate = snap(table.XCoordinate, grid)
            table.YCoordinate = snap(table.YCoordinate, grid)
        for value in vars(table).values():
            for record in value if isinstance(value, list) else [value]:
                if isinstance(record, ot.ValueRecord):
                    for f in ("XPlacement", "YPlacement", "XAdvance", "YAdvance"):
                        if hasattr(record, f):
                            setattr(record, f, snap(getattr(record, f), grid))


def pixelate_font(font, grid):
    """Pixelate every glyph of `font` onto the grid, in place, and return it.

    Advances are rounded to the grid and outlines shifted by half the
    difference, so glyphs stay centred; the same goes for vertical advances
    and origins. GPOS values are snapped too, so glyphs set side by side
    share one continuous grid, as in Redaction N."""
    if PPEM * grid % 1000:
        raise ValueError(f"a {grid}-unit cell is not a whole number of pixels at {PPEM} ppem")
    data = io.BytesIO()
    font.save(data)  # for FreeType
    order = font.getGlyphOrder()
    glyf, hmtx, vmtx = font["glyf"], font["hmtx"], font["vmtx"]
    tasks = [
        (gid, (snap_advance(hmtx[n][0], grid) - hmtx[n][0]) / 2) for gid, n in enumerate(order)
    ]
    if len(tasks) < 64:  # a few glyphs (arrows): a process pool costs more than it saves
        _init_worker(data.getvalue(), grid)
        results = [_pixelate_glyph(task) for task in tasks]
    else:
        with ProcessPoolExecutor(initializer=_init_worker, initargs=(data.getvalue(), grid)) as ex:
            results = list(ex.map(_pixelate_glyph, tasks, chunksize=64))
    for name, res in zip(order, results):
        old = glyf[name]
        adv = snap_advance(hmtx[name][0], grid)
        old_vadv, tsb = vmtx[name]
        vadv = snap_advance(old_vadv, grid)
        origin = old.yMax + tsb if old.numberOfContours else VERT_ORIGIN
        origin = snap(origin - (old_vadv - vadv) / 2, grid)
        if res is None:
            glyf[name] = Glyph()
            hmtx[name] = (adv, 0)
            vmtx[name] = (vadv, 0)
            continue
        col0, row_top, contours = res
        pen = TTGlyphPen(None)
        for pts in contours:
            pen.moveTo(((col0 + pts[0][0]) * grid, (row_top + pts[0][1]) * grid))
            for x, y in pts[1:]:
                pen.lineTo(((col0 + x) * grid, (row_top + y) * grid))
            pen.closePath()
        g = glyf[name] = pen.glyph()
        g.recalcBounds(glyf)
        hmtx[name] = (adv, g.xMin)
        vmtx[name] = (vadv, origin - g.yMax)
    snap_gpos(font, grid)
    return font


_face, _cell = None, None


def _init_worker(data, grid):
    global _face, _cell
    _face = freetype.Face(io.BytesIO(data))
    _face.set_char_size(PPEM * 64, PPEM * 64, 72, 72)
    _cell = PPEM * grid // 1000


def _pixelate_glyph(task):
    """(gid, dx) -> (col0, row_top, contours), or None for an empty glyph.
    The outline is shifted right by dx font units first."""
    gid, dx = task
    shift = int(round(dx * PPEM * 64 / 1000))
    _face.set_transform(freetype.Matrix(0x10000, 0, 0, 0x10000), freetype.Vector(shift, 0))
    _face.load_glyph(gid, LOAD_FLAGS)
    g = _face.glyph
    bm = g.bitmap
    if bm.rows == 0 or bm.width == 0:
        return None
    px = np.frombuffer(bytes(bm.buffer), dtype=np.uint8).reshape(bm.rows, bm.pitch)
    px = px[:, : bm.width].astype(np.float32) / 255.0
    fine, col0, row_top = _to_cells(px, g.bitmap_left, g.bitmap_top, _cell)
    on = _quantize(fine, _cell)
    if not on.any():
        return None
    return col0, row_top, _trace(on)


def _to_cells(px, left, top, S):
    """Pad a bitmap to whole S x S cells. Returns (fine, col0, row_top): cell
    column j starts at grid x = col0 + j, cell row i (top-down) spans grid
    y from row_top - i - 1 to row_top - i."""
    rows, cols = px.shape
    col0 = left // S
    col1 = -(-(left + cols) // S)
    row_top = -(-top // S)
    row_bot = (top - rows) // S
    fine = np.zeros(((row_top - row_bot) * S, (col1 - col0) * S), np.float32)
    ox, oy = left - col0 * S, row_top * S - top
    fine[oy : oy + rows, ox : ox + cols] = px
    return fine, col0, row_top


def _runs(mask):
    """Runs of True along the last axis, as (row, start, stop) arrays."""
    m = np.zeros((mask.shape[0], mask.shape[1] + 2), np.int8)
    m[:, 1:-1] = mask
    d = np.diff(m, axis=1)
    r0, s = np.nonzero(d == 1)
    r1, e = np.nonzero(d == -1)
    return r0, s, e  # nonzero scans row-major, so starts and stops pair up


def _quantize(fine, S):
    """Turn a cell-aligned coverage bitmap into a boolean cell grid."""
    R, C = fine.shape[0] // S, fine.shape[1] // S
    blocks = fine.reshape(R, S, C, S)
    on = blocks.mean(axis=(1, 3)) >= FILL
    min_len = max(1, int(round(MIN_STROKE * S)))
    restore = []
    # Horizontal strokes: runs along the fine rows of each cell column.
    col, s, e = _runs(blocks.mean(axis=3).reshape(R * S, C).T >= STROKE)
    for j, a, b in zip(col, s, e):
        if b - a >= min_len and not on[a // S : (b - 1) // S + 1, j].any():
            restore.append(((a + b) // 2 // S, j, True))
    # Vertical strokes: runs along the fine columns of each cell row.
    row, s, e = _runs(blocks.mean(axis=1).reshape(R, C * S) >= STROKE)
    for i, a, b in zip(row, s, e):
        if b - a >= min_len and not on[i, a // S : (b - 1) // S + 1].any():
            restore.append((i, (a + b) // 2 // S, False))
    live = np.zeros((R + 2, C + 2), bool)  # padded, so neighbours always exist
    live[1:-1, 1:-1] = on
    for i, j, horizontal in restore:
        # A pixel touching a filled cell across its stroke would merge
        # stacked strokes (書, 量) into a block: leave it out.
        if horizontal:
            touches = live[i, j + 1] or live[i + 2, j + 1]
        else:
            touches = live[i + 1, j] or live[i + 1, j + 2]
        if not touches:
            live[i + 1, j + 1] = True
    return live[1:-1, 1:-1]


def _trace(on):
    """Trace a boolean cell grid (top-down rows) into closed rectilinear
    contours in grid units: y up, the top edge of row i at y = -i, filled
    region on the right of travel (clockwise outer contours, as TrueType
    expects)."""
    R, C = on.shape
    p = np.zeros((R + 2, C + 2), bool)
    p[1:-1, 1:-1] = on
    core = p[1:-1, 1:-1]
    segs = []  # (x0, y0, x1, y1)
    r, s, e = _runs(core & ~p[:-2, 1:-1])  # top edges, left to right
    segs += [(a, -i, b, -i) for i, a, b in zip(r, s, e)]
    r, s, e = _runs(core & ~p[2:, 1:-1])  # bottom edges, right to left
    segs += [(b, -i - 1, a, -i - 1) for i, a, b in zip(r, s, e)]
    c, s, e = _runs((core & ~p[1:-1, 2:]).T)  # right edges, top to bottom
    segs += [(j + 1, -a, j + 1, -b) for j, a, b in zip(c, s, e)]
    c, s, e = _runs((core & ~p[1:-1, :-2]).T)  # left edges, bottom to top
    segs += [(j, -b, j, -a) for j, a, b in zip(c, s, e)]

    starts = {}
    for k, (x0, y0, _, _) in enumerate(segs):
        starts.setdefault((x0, y0), []).append(k)
    used = [False] * len(segs)
    contours = []
    for k in range(len(segs)):
        pts = []
        while not used[k]:
            used[k] = True
            x0, y0, x1, y1 = segs[k]
            pts.append((int(x0), int(y0)))
            cand = [n for n in starts[(x1, y1)] if not used[n]]
            if not cand:
                break
            # Where cells touch diagonally, take the right turn so they stay
            # separate contours.
            dx, dy = x1 - x0, y1 - y0
            k = min(
                cand,
                key=lambda n, dx=dx, dy=dy: (
                    dx * (segs[n][3] - segs[n][1]) - dy * (segs[n][2] - segs[n][0])
                ),
            )
        if pts:
            contours.append(pts)
    return contours
