"""Put glyphs on an N-unit pixel grid, the way Redaction 10 to 100 do.

FreeType renders each glyph anti-aliased, which gives the exact area of each
grid cell that the outline covers. A cell is filled when the outline covers
half of it. A dropout pass then puts back thin strokes (Mincho hairlines)
that fall between cells. Filled cells are traced back into rectilinear
TrueType contours.

On the coarse grids, from PHASED, where a cell is about as thick as a stem,
where a glyph falls in a cell decides what it looks like: an 85-unit stem
fills one 70-unit cell, or two. There, the kanji and kana of Noto Serif JP
lightened in Regular and Italic (family.light; build.py asks,
pixelate_font; which ones, phased_glyphs) are also tried
at PHASES spots across a cell and as many up and down, as the glyphs drawn
in glyphs/ are (shapes.phased), with a dropout pass that puts each thin
stroke back in one row or column (_thin). Of the spots that keep the top
and bottom rows where the glyph stood (the same glyph of another font,
`stands`, unshifted: Noto Serif JP at the weight it had before it was
lightened) and its ink within its advance, the one closest to the outline
is kept: the cells it adds and loses summed, a counter of the outline it
closes (the bar of 日) or a piece it loses or splits (a ring of ぺ, a dot
of べ) costing as much as several cells (_structure). Failing any spot, it
keeps the rows it takes lightened, if they are within those (a hairline
end a row short), or else the glyph of `stands` is kept, as it stood. No two kanji or kana drawn
differently come out within APART cells of each other, or failing that the
same, where a spot keeps them apart (_distinct): a spot that draws one
worse only for the few of WORSE, logged. On FOLLOW, the vertical forms of
the kanji and kana take the cells of the glyph they stand for (_follow), so
read alike across and down. Other glyphs, punctuation and brackets, every
glyph on the finer grids, and Bold's kanji and kana, are placed as they
stand, as before any of this.

build.py caches pixelated fonts under a hash of this file.
"""

import hashlib
import io
import unicodedata
from concurrent.futures import ProcessPoolExecutor

import freetype
import numpy as np
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib.tables import otTables as ot
from fontTools.ttLib.tables._g_l_y_f import Glyph
from fontTools.ttLib.tables.otTraverse import dfs_base_table
from fontTools.unicodedata import block, script

PPEM = 400  # rendering size: a cell of N units is 0.4 N pixels wide
VERT_ORIGIN = 880  # top of the ideographic em box, the vertical origin
FILL = 0.5  # a cell is filled when the outline covers this much of it
STROKE = 0.5  # a stroke fills this much of a cell column or row...
MIN_STROKE = 0.15  # ...and is this thick, in cells, to be put back by the dropout pass
PHASED = 70  # grids this coarse or coarser try kanji and kana at PHASES spots...
PHASES = 4  # ...across and up a cell, and keep the one closest to the outline...
COUNTER = 4  # ...where a counter of the outline closed costs as many cells as this...
PIECE = 2  # ...and a piece lost, or one too many, as many as this
APART = 3  # kanji and kana come out this many cells apart, or at least unlike, where they can
# Kanji that take a spot drawing them worse (a stroke end or a piece more)
# where every other comes out the same as another kanji, a variant of
# theirs (_distinct): the build logs each
WORSE = "熙閶"
FOLLOW = 100  # grids this coarse: vertical forms of kana take the cells of their horizontal ones
BLOCK = 4  # pixels at PPEM: the outline's counters and pieces are read in blocks this size
READ = ("Hani", "Hira", "Kana")  # scripts of the kanji and kana: no two of them come out alike
# Blocks whose glyphs stand where they do in the em for what they mean
# (punctuation, brackets, marks, width forms): never phased
PLACED = {
    "CJK Symbols and Punctuation",
    "Halfwidth and Fullwidth Forms",
    "Vertical Forms",
    "CJK Compatibility Forms",
    "Small Form Variants",
}
RADICALS = {"Kangxi Radicals", "CJK Radicals Supplement"}  # drawn as kanji are, symbols
# Kanji and kana drawn by hand on a grid, in glyphs/drawn (build.pinned): on
# 100, where a placement reads as another character (書 as 昔, 間 as 問) or
# breaks a stroke (土's foot)
JAPANESE = "japanese.txt"
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


def pixelate_font(font, grid, phased=False, stands=None, pinned=None, log=print):
    """Pixelate every glyph of `font` onto the grid, in place, and return it.

    Advances are rounded to the grid and outlines shifted by half the
    difference, so glyphs stay centred; the same goes for vertical advances
    and origins. GPOS values are snapped too, so glyphs set side by side
    share one continuous grid, as in Redaction N.

    If `phased`, the kanji and kana (phased_glyphs) are placed, on the grids
    from PHASED, as the module docstring says, on the rows the same glyphs of
    `stands`, a font with the same glyph order, take unshifted (or their
    own, if it is None), and come out unlike each
    other (_distinct): where one goes depends on those of `font` that come
    out alike at some spot, so a font cut down to a few glyphs may place
    them otherwise; cut the pixelated font instead. Those no spot keeps
    apart are logged. `pinned`, {code point: cells, top row first, with
    `at`, their bottom left cell}, are kanji and kana drawn by hand on the
    grid, placed so (and every glyph drawn as they are), as they stand.
    The glyphs drawn in glyphs/ are not phased:
    shapes.phased places them itself, and needs them kept where it puts
    them."""
    if PPEM * grid % 1000:
        raise ValueError(f"a {grid}-unit cell is not a whole number of pixels at {PPEM} ppem")
    data = io.BytesIO()
    font.save(data)  # for FreeType
    rows = io.BytesIO()
    if stands is not None:
        if stands.getGlyphOrder() != font.getGlyphOrder():
            raise ValueError("`stands` has other glyphs than `font`")
        stands.save(rows)
    order = font.getGlyphOrder()
    glyf, hmtx, vmtx = font["glyf"], font["hmtx"], font["vmtx"]
    moving = phased_glyphs(font) if phased and grid >= PHASED else set()
    tasks = []
    for gid, n in enumerate(order):
        adv = snap_advance(hmtx[n][0], grid)
        tasks.append((gid, (adv - hmtx[n][0]) / 2, adv // grid, n in moving))
    if len(tasks) < 64:  # a few glyphs (arrows): a process pool costs more than it saves
        _init_worker(data.getvalue(), rows.getvalue(), grid)
        results = [_pixelate_glyph(task) for task in tasks]
    else:
        init = (data.getvalue(), rows.getvalue(), grid)
        with ProcessPoolExecutor(initializer=_init_worker, initargs=init) as ex:
            results = list(ex.map(_pixelate_glyph, tasks, chunksize=64))
    if pinned:
        results = _pin(font, results, moving, pinned)
    if moving:
        read = {}  # glyph name: its lowest code point, of the kanji and kana
        for cp, n in sorted(font.getBestCmap().items()):
            if script(cp) in READ:
                read.setdefault(n, cp)
        results, alike, worse = _distinct(order, results, read)
        for names in alike:
            log(f"on {grid}: {''.join(chr(read[n]) for n in names)} come out alike at every spot")
        for name, lost, others in worse:
            log(
                f"on {grid}: {chr(read[name])} drawn worse ({lost[0]} counters fewer, {lost[1]}"
                f" pieces and {lost[2]} ends more), to differ from"
                f" {''.join(chr(read[n]) for n in others)}"
            )
        if grid >= FOLLOW:
            results = _follow(font, results, moving, grid)
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
        col0, row_top, on = res[1][0][1:4]
        pen = TTGlyphPen(None)
        for pts in res[0] if res[0] is not None else _trace(on):
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


def phased_glyphs(font):
    """Names of the glyphs of `font` placed by phase: those that stand, by
    its cmap, its variation sequences and its GSUB (a vertical form stands
    for what it is substituted for), only for kanji and kana letters
    (general category Lo of the Han, Hiragana and Katakana scripts, and the
    radicals, drawn as kanji are), and not for small kana (kana named
    SMALL: ⼩, KANGXI RADICAL SMALL, is 小's glyph), nor
    for anything of the blocks in PLACED: the CJK Symbols and Punctuation
    block, and width, vertical, compatibility and small forms. Neither for
    the long vowel mark, iteration marks (Lm), nor dakuten and handakuten
    (Sk, Mn). Where those stand in the em is what they mean; the brackets
    of a pair are placed alike, and kept apart, only as they stand."""

    def letter(cp):
        c = chr(cp)
        return (
            script(cp) in READ
            and (unicodedata.category(c) == "Lo" or block(cp) in RADICALS)
            and block(cp) not in PLACED
            and not (script(cp) in ("Hira", "Kana") and "SMALL" in unicodedata.name(c, ""))
        )

    stands = {}  # glyph name: the code points it stands for
    for cp, name in font.getBestCmap().items():
        stands.setdefault(name, set()).add(cp)
    for table in font["cmap"].tables:
        if table.format == 14:
            for sequences in table.uvsDict.values():
                for base, name in sequences:
                    if name is not None:
                        stands.setdefault(name, set()).add(base)
    edges = []  # (glyphs in, glyphs out) of every substitution
    if "GSUB" in font:
        for lookup in font["GSUB"].table.LookupList.Lookup:
            for sub in lookup.SubTable:
                sub = getattr(sub, "ExtSubTable", sub)
                if hasattr(sub, "mapping"):  # single
                    edges += [((a,), (b,)) for a, b in sub.mapping.items()]
                elif hasattr(sub, "alternates"):
                    edges += [((a,), tuple(b)) for a, b in sub.alternates.items()]
                elif hasattr(sub, "ligatures"):
                    for first, ligatures in sub.ligatures.items():
                        edges += [((first, *lig.Component), (lig.LigGlyph,)) for lig in ligatures]
    for _ in range(8):  # a few rounds reach what substitutions of substitutions make
        grew = False
        for ins, outs in edges:
            cps = set().union(*(stands.get(n, set()) for n in ins))
            for n in outs:
                if not cps <= stands.setdefault(n, set()):
                    stands[n] |= cps
                    grew = True
        if not grew:
            break
    return {n for n, cps in stands.items() if cps and all(letter(cp) for cp in cps)}


_face, _stands, _cell, _phases = None, None, None, None


def _init_worker(data, rows, grid):
    global _face, _stands, _cell, _phases
    _face = freetype.Face(io.BytesIO(data))
    _face.set_char_size(PPEM * 64, PPEM * 64, 72, 72)
    _stands = None
    if rows:
        _stands = freetype.Face(io.BytesIO(rows))
        _stands.set_char_size(PPEM * 64, PPEM * 64, 72, 72)
    _cell = PPEM * grid // 1000
    _phases = phases(grid)


def phases(grid):
    """Shifts, in pixels at PPEM, across and up, a glyph is tried at on
    `grid`: across, from none to half a cell back and a quarter on, PHASES
    spots a cell apart; up, half a cell down to half a cell up, as its rows
    are kept (_pixelate_glyph), and half a cell up does not come out as
    half down, a row higher. Whole pixels: the cells of the grids from
    PHASED are a multiple of PHASES pixels wide."""
    if grid < PHASED:
        return [(0, 0)]
    cell = PPEM * grid // 1000
    across = sorted(range(-(PHASES // 2), PHASES - PHASES // 2), key=abs)
    up = sorted(range(-(PHASES // 2), PHASES // 2 + 1), key=abs)
    return [(cell * i // PHASES, cell * j // PHASES) for i in across for j in up]


def _pin(font, results, moving, pinned):
    """`results` with the glyphs of `pinned` ({code point: cells}) and every
    glyph rendered as they are, of `moving`, placed as they are drawn."""
    order, cmap = font.getGlyphOrder(), font.getBestCmap()
    drawings = {}
    for cp, rows in pinned.items():
        name = cmap.get(cp)
        if name not in moving:
            raise ValueError(f"{chr(cp)} is drawn by hand, but not placed by phase")
        if rows.at is None:
            raise ValueError(f"{chr(cp)} is drawn by hand without its bottom left cell")
        on = np.array([[c == "#" for c in row] for row in rows], bool)
        x, y = rows.at
        drawings[results[order.index(name)][2]] = (0.0, x, y + len(rows), on)
    return [
        (None, [drawings[res[2]]], res[2]) if res and name in moving and res[2] in drawings else res
        for name, res in zip(order, results)
    ]


def _distinct(order, results, read):
    """(`results`, alike, worse): `results`, what _pixelate_glyph returns for each glyph of `order`,
    each with its placement chosen: its best, but for the kanji and kana
    (`read`, {name: its lowest code point}), which come out unlike each
    other where they can. Glyphs rendered the same (a compatibility
    ideograph drawn as its unified one) are one, and stay alike; those
    placed as they stand hold their cells first. Then, of every placement of
    every other, from the closest to its outline (ties: lowest code point
    first), each takes its own if no other's cells are within APART of
    them, wherever they are (cropped alike, cell for cell); those left, if
    no other's are the same. A placement but the best is taken only if it
    draws the glyph no worse (_no_worse): never a stray cell or a broken
    stroke to keep two apart, which a reader sees more than the cells they
    share. Only the kanji of WORSE, left, then take one that draws them
    worse, the least worse first (_worse), if it keeps them from coming out
    the same; each is returned, with those it differs from. Those left
    take their best, and those their best leaves alike are returned. A cell
    pattern goes to the one it draws best, whatever the order of the
    glyphs. Other glyphs are left be: a dash need not differ from 一, nor ┍
    from ┝, where every bar is a row of cells. Glyphs drawn by hand (_pin)
    are placed as they stand, and hold their cells first."""
    units = {}  # rendering: the names of the kanji and kana rendered so
    for name, res in zip(order, results):
        if res is not None and name in read:
            units.setdefault(res[2], []).append(name)
    by_name = dict(zip(order, results))
    taken, chosen, queue = _Taken(), {}, []
    for drawing, names in units.items():
        placements = by_name[names[0]][1]
        if len(placements) == 1:  # placed as it stands
            taken.add(placements[0][3], drawing)
            chosen[drawing] = 0
            continue
        cp = min(read[n] for n in names)
        queue += [(p[0], cp, k, drawing) for k, p in enumerate(placements)]
    queue.sort()
    sound = [q for q in queue if q[2] == 0 or _no_worse(by_name[units[q[3]][0]][1], q[2])]
    for apart in (APART, 1):
        for _, _, k, drawing in sound:
            on = by_name[units[drawing][0]][1][k][3]
            if drawing not in chosen and not taken.near(on, drawing, apart):
                taken.add(on, drawing)
                chosen[drawing] = k
    # Last, the few of WORSE take a spot that draws them worse, the least
    # worse first: counters lost, then pieces, then stroke ends added
    allowed = {ord(c) for c in WORSE}
    last = []
    for score, cp, k, drawing in queue:
        if drawing in chosen or cp not in allowed:
            continue
        placements = by_name[units[drawing][0]][1]
        lost = _worse(placements, k)
        last.append((lost, score, cp, k, drawing))
    worse = []
    for lost, _, _, k, drawing in sorted(last):
        placements = by_name[units[drawing][0]][1]
        if drawing in chosen or taken.near(placements[k][3], drawing, 1):
            continue
        others = taken.near(placements[0][3], drawing, 1)
        taken.add(placements[k][3], drawing)
        chosen[drawing] = k
        name = min(units[drawing], key=read.get)
        worse.append(
            (name, lost, sorted({min(units[o], key=read.get) for o in others}, key=read.get))
        )
    alike = {}
    for drawing, names in units.items():
        if drawing not in chosen:
            chosen[drawing] = 0
            on = by_name[names[0]][1][0][3]
            if others := taken.near(on, drawing, 1):
                key = min(others)
                alike.setdefault(key, set(units[key])).update(names)
    out = []
    for name, res in zip(order, results):
        if res is not None and name in read:
            k = chosen[res[2]]
            res = (res[0] if k == 0 else None, [res[1][k]], res[2])
        out.append(res)
    return out, [sorted(names, key=read.get) for names in alike.values()], worse


def _worse(placements, k):
    """How much worse placement `k` of `placements` draws its glyph than the
    best, the first: (counters fewer, pieces more, stroke ends more), none
    below 0."""
    best, mine = (_form(placements[i][3]) for i in (0, k))
    return max(0, best[0] - mine[0]), max(0, mine[1] - best[1]), max(0, mine[2] - best[2])


def _follow(font, results, moving, grid):
    """`results` with the vertical forms of `moving` (GSUB vert and vrt2,
    one glyph for one) placed as the glyph they are substituted for, when it
    is of `moving` too: its cells, shifted by whole cells as far as Noto
    Serif JP moves the vertical form (a few units: none). Its own placement
    may draw it otherwise (き with a loose cell where ゛ goes), and a reader
    sees one letter across and down."""
    order = font.getGlyphOrder()
    index = {n: i for i, n in enumerate(order)}
    glyf = font["glyf"]
    pairs = {}
    if "GSUB" in font:
        table = font["GSUB"].table
        lookups = {
            i
            for record in table.FeatureList.FeatureRecord
            if record.FeatureTag in ("vert", "vrt2")
            for i in record.Feature.LookupListIndex
        }
        for i in sorted(lookups):
            for sub in table.LookupList.Lookup[i].SubTable:
                sub = getattr(sub, "ExtSubTable", sub)
                for a, b in getattr(sub, "mapping", {}).items():
                    if a != b and a in moving and b in moving:
                        pairs.setdefault(b, a)
    out = list(results)
    for vert, horizontal in sorted(pairs.items()):
        res, was = results[index[horizontal]], results[index[vert]]
        if res is None or was is None:
            continue
        g, h = glyf[vert], glyf[horizontal]
        g.recalcBounds(glyf)
        h.recalcBounds(glyf)
        dx = round((g.xMin + g.xMax - h.xMin - h.xMax) / 2 / grid)
        dy = round((g.yMin + g.yMax - h.yMin - h.yMax) / 2 / grid)
        score, col0, row_top, on = res[1][0]
        out[index[vert]] = (None, [(score, col0 + dx, row_top + dy, on)], was[2])
    return out


def _no_worse(placements, k):
    """Whether placement `k` of `placements` draws its glyph no worse than
    the best, the first: no counter fewer, no piece more, no stroke end
    more (a stray cell, a kink in a stem, a bar broken under it)."""
    (best, mine) = (_form(placements[i][3]) for i in (0, k))
    return mine[0] >= best[0] and mine[1] <= best[1] and mine[2] <= best[2]


def _form(on):
    """(counters, pieces, ends) of cells: counters closed side to side,
    pieces side by side, and cells with one filled cell beside them or
    none."""
    padded = np.zeros((on.shape[0] + 2, on.shape[1] + 2), np.int8)
    padded[1:-1, 1:-1] = on
    beside = padded[:-2, 1:-1] + padded[2:, 1:-1] + padded[1:-1, :-2] + padded[1:-1, 2:]
    return (
        len(_counters(on, corners=True)),
        len(_regions(on, diagonal=False)),
        int((on & (beside <= 1)).sum()),
    )


class _Taken:
    """Cell patterns taken, cropped, by their shape: which are near one."""

    def __init__(self):
        self.shapes = {}  # shape: [patterns, flat, a row each, room for more; how many; owners]

    def add(self, on, owner):
        crop = _crop(on)
        entry = self.shapes.setdefault(crop.shape, [np.zeros((8, crop.size), bool), 0, []])
        if entry[1] == len(entry[0]):
            entry[0] = np.concatenate([entry[0], np.zeros_like(entry[0])])
        entry[0][entry[1]] = crop.ravel()
        entry[1] += 1
        entry[2].append(owner)

    def near(self, on, owner, apart):
        """The owners of patterns taken fewer than `apart` cells from `on`,
        but `owner`."""
        crop = _crop(on)
        if crop.shape not in self.shapes:
            return set()
        patterns, count, owners = self.shapes[crop.shape]
        off = (patterns[:count] != crop.ravel()).sum(axis=1)
        return {owners[i] for i in np.nonzero(off < apart)[0]} - {owner}


def _crop(on):
    """Cells without the rows and columns of air around them."""
    rows, cols = np.nonzero(on.any(axis=1))[0], np.nonzero(on.any(axis=0))[0]
    return on[rows[0] : rows[-1] + 1, cols[0] : cols[-1] + 1]


def _looks(on):
    """What cells look like, wherever they are: cropped, hashable."""
    crop = _crop(on)
    return crop.shape, crop.tobytes()


def _extent(on, col0, row_top):
    """(first column, last column, top row, bottom row) of the filled cells,
    on the grid: rows counted down from row_top."""
    rows, cols = np.nonzero(on.any(axis=1))[0], np.nonzero(on.any(axis=0))[0]
    return tuple(
        int(v) for v in (col0 + cols[0], col0 + cols[-1], row_top - rows[0], row_top - rows[-1])
    )


def _pixelate_glyph(task):
    """(gid, dx, columns, phased) -> (contours, placements, rendering), or
    None for an empty glyph: placements, (score, col0, row_top, cells), best
    first, each unlike the others, the contours of the best, and a key of
    the outline as rendered, alike for glyphs drawn alike. The outline is
    shifted right by dx font units first, to centre it in its advance,
    `columns` cells.

    Unless `phased`, the glyph is placed as it stands: one placement, the
    unshifted one. If phased, also at each spot of _phases, each kept if its
    top and bottom rows are those the glyph of _stands takes unshifted, and
    its ink stays within its advance (or where it stands unshifted, if
    wider): a glyph never moves up or down on the line, nor into its
    neighbour. If no spot keeps its rows (a hairline atop it, lighter, falls
    a row lower), the spots that keep the rows it takes unshifted, if those
    are within them: a row short, never off them. Failing those, it is the
    glyph of _stands, unshifted: as it stood. With no _stands, its own rows
    unshifted are kept."""
    gid, dx, columns, phased = task
    rendered = _render(_face, gid, dx)
    if rendered is None:
        return None
    px, left, top = rendered
    drawing = hashlib.sha1(repr((px.shape, left, top)).encode() + px.tobytes()).hexdigest()
    fine, col0, row_top = _to_cells(px, left, top, _cell)
    on, error = _quantize(fine, _cell)
    if not on.any():
        return None
    if not phased:
        return _trace(on), [(error, col0, row_top, on)], drawing
    outline = _structure(px, _cell)
    first, last, *own = _extent(on, col0, row_top)
    first, last, own = min(first, 0), max(last, columns - 1), tuple(own)
    stood, before = own, None
    if _stands is not None and (was := _render(_stands, gid, dx)) is not None:
        was_fine, *at = _to_cells(*was, _cell)
        was_on, was_error = _quantize(was_fine, _cell)
        if was_on.any():
            stood = tuple(_extent(was_on, *at)[2:])
            before = (was_error, *at, was_on)
    tried = [(error + _lost(outline, on), len(_phases), col0, row_top, on, own)]
    for k, (x, y) in enumerate(_phases):
        fine, c0, r0 = _to_cells(px, left + x, top + y, _cell)
        cells, error = _quantize(fine, _cell, whole=True)
        if not cells.any():
            continue
        a, b, *rows = _extent(cells, c0, r0)
        if first <= a and b <= last and tuple(rows) in (stood, own):
            tried.append((error + _lost(outline, cells), k, c0, r0, cells, tuple(rows)))
    # Where it stood, if any spot puts it there; else where it stands
    # lightened, if within those rows (a hairline end, lighter, a row short
    # of where it stood); else as it stood
    kept = [t for t in tried if t[5] == stood]
    if not kept and stood[1] <= own[1] <= own[0] <= stood[0]:
        kept = [t for t in tried if t[5] == own]
    tried = kept
    if not tried:
        return _trace(before[3]), [before], drawing
    placements, seen = [], set()
    for score, _, c0, r0, cells, _ in sorted(tried, key=lambda t: t[:2]):
        if _looks(cells) not in seen:
            seen.add(_looks(cells))
            placements.append((score, c0, r0, cells))
    return _trace(placements[0][3]), placements, drawing


def _render(face, gid, dx):
    """(coverage, left, top) of glyph `gid` of `face` rendered at PPEM,
    shifted right by dx font units, or None if it is empty."""
    shift = int(round(dx * PPEM * 64 / 1000))
    face.set_transform(freetype.Matrix(0x10000, 0, 0, 0x10000), freetype.Vector(shift, 0))
    face.load_glyph(gid, LOAD_FLAGS)
    g = face.glyph
    bm = g.bitmap
    if bm.rows == 0 or bm.width == 0:
        return None
    px = np.frombuffer(bytes(bm.buffer), dtype=np.uint8).reshape(bm.rows, bm.pitch)
    return px[:, : bm.width].astype(np.float32) / 255.0, g.bitmap_left, g.bitmap_top


def _structure(px, cell):
    """(counters, pieces) of an outline rendered `px`, read in BLOCK-pixel
    blocks, half covered: counters as big as half a cell (`cell` pixels
    wide), pieces as big as a quarter."""
    rows, cols = -(-px.shape[0] // BLOCK), -(-px.shape[1] // BLOCK)
    padded = np.zeros((rows * BLOCK, cols * BLOCK), np.float32)
    padded[: px.shape[0], : px.shape[1]] = px
    ink = padded.reshape(rows, BLOCK, cols, BLOCK).mean(axis=(1, 3)) >= FILL
    area = (cell / BLOCK) ** 2
    return (
        sum(s >= area / 2 for s in _counters(ink)),
        sum(s >= area / 4 for s in _regions(ink, diagonal=True)),
    )


def _lost(outline, on):
    """What `on`, cells, loses of the structure of an outline, (counters,
    pieces) of _structure, in cells: COUNTER for each counter it closes,
    PIECE for each piece it loses or adds. A counter of cells is closed
    side to side: one shut only where cells meet at a corner is open, so a
    checkerboard does not pass for a bar."""
    counters, pieces = outline
    mine = len(_counters(on, corners=True))
    return COUNTER * max(0, counters - mine) + PIECE * abs(
        pieces - len(_regions(on, diagonal=True))
    )


def _counters(ink, corners=False):
    """Sizes of the counters of `ink`: regions of air, side by side (or, if
    `corners`, corner to corner too), that do not reach its edge."""
    air = np.ones((ink.shape[0] + 2, ink.shape[1] + 2), bool)
    air[1:-1, 1:-1] = ~ink
    return _regions(air, diagonal=corners)[1:]  # the first, from the corner, is outside


def _regions(mask, diagonal):
    """Sizes of the regions of `mask`, cells side by side or, if `diagonal`,
    corner to corner: that of its first cell (row-major) first."""
    rows, starts, stops = _runs(mask)
    parent = list(range(len(rows)))

    def root(k):
        while parent[k] != k:
            parent[k] = k = parent[parent[k]]
        return k

    reach = 1 if diagonal else 0
    above, i = [], 0  # runs of the row before
    for row in range(mask.shape[0]):
        here = []
        while i < len(rows) and rows[i] == row:
            here.append(i)
            i += 1
        for k in here:
            for m in above:
                if starts[m] < stops[k] + reach and starts[k] < stops[m] + reach:
                    parent[root(m)] = root(k)
        above = here
    sizes = {}
    for k in range(len(rows)):
        r = root(k)
        sizes[r] = sizes.get(r, 0) + int(stops[k] - starts[k])
    if not sizes:
        return []
    first = root(0)
    return [sizes[first], *(v for r, v in sizes.items() if r != first)]


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


def _quantize(fine, S, whole=False):
    """Turn a cell-aligned coverage bitmap into a boolean cell grid, and how
    far it is from the outline: the ink it adds and loses, in cells. If
    `whole`, the dropout pass puts each thin stroke back in one row or
    column (_thin) rather than cell by cell. Either way a cell put back is
    left out where it touches a filled cell across its stroke: a stroke
    crowded by another comes back in part, or not at all."""
    R, C = fine.shape[0] // S, fine.shape[1] // S
    blocks = fine.reshape(R, S, C, S)
    cover = blocks.mean(axis=(1, 3))
    on = cover >= FILL
    # Horizontal strokes: runs along the fine rows of each cell column...
    across = _thin(blocks.mean(axis=3).reshape(R * S, C).T >= STROKE, on.T, S, whole)
    # ...vertical strokes: runs along the fine columns of each cell row.
    down = _thin(blocks.mean(axis=1).reshape(R, C * S) >= STROKE, on, S, whole)
    restore = [(i, j, True) for j, i in across] + [(i, j, False) for i, j in down]
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
    on = live[1:-1, 1:-1]
    return on, float(np.abs(on - cover).sum())


def _thin(mask, on, S, whole):
    """Cells to put back for the thin strokes of `mask`, fine runs along each
    line of cells (a column of them for a horizontal stroke), where `on`,
    the cells by line, has none: [(line, cell)], each in the cell of the
    middle of its run.

    If `whole`, the runs of a stroke, overlapping from line to line or across
    filled cells (a stem it crosses), go in one cell along the line, the one
    most of the stroke is in of those it touches least filled cells beside:
    Mincho horizontals rise to the right, and cell by cell they step from one
    row to the next, where a stacked stroke keeps every other cell (書). It
    picks the row or column; _quantize may still leave out cells of it that
    touch another stroke, so a stroke is not always put back whole. A stroke
    that rises more than a cell along its length (the ノ atop 千) is a slant,
    not a horizontal: put back cell by cell, as it runs."""
    lines, starts, stops = _runs(mask)
    min_len = max(1, int(round(MIN_STROKE * S)))
    runs = [
        (j, a, b)
        for j, a, b in zip(lines.tolist(), starts.tolist(), stops.tolist())
        if b - a >= min_len and not on[j, a // S : (b - 1) // S + 1].any()
    ]
    if not whole:
        return [(j, (a + b) // 2 // S) for j, a, b in runs]
    group = list(range(len(runs)))

    def root(k):
        while group[k] != k:
            group[k] = k = group[group[k]]
        return k

    by_line = {}
    for k, (j, _, _) in enumerate(runs):
        by_line.setdefault(j, []).append(k)
    for k, (j, a, b) in enumerate(runs):
        for jj in range(j + 1, len(on)):
            near = [m for m in by_line.get(jj, ()) if runs[m][1] < b and a < runs[m][2]]
            for m in near:
                group[root(m)] = root(k)
            if near or not on[jj, a // S : (b - 1) // S + 1].any():
                break
    strokes = {}
    for k in range(len(runs)):
        strokes.setdefault(root(k), []).append(runs[k])
    # Longest first, each kept off the cells beside those placed before it: a
    # frame (国) keeps its row, and what is crowded against it moves
    taken = on.copy()
    out = []
    for stroke in sorted(strokes.values(), key=lambda st: -len({j for j, _, _ in st})):
        middles = [a + b for _, a, b in stroke]  # twice the middle of each run
        if max(middles) - min(middles) > 2 * S:
            out += [(j, (a + b) // 2 // S) for j, a, b in stroke]
            continue
        weight = {}
        for _, a, b in stroke:
            for i in range(a // S, (b - 1) // S + 1):
                weight[i] = weight.get(i, 0) + min(b, (i + 1) * S) - max(a, i * S)
        cells = sorted({j for j, _, _ in stroke})

        def beside(j, i):
            return sum(taken[j, k] for k in (i - 1, i + 1) if 0 <= k < taken.shape[1])

        def crowded(i, cells=cells, weight=weight):
            return sum(beside(j, i) for j in cells), -weight[i]

        best = min(weight, key=crowded)
        for j in cells:
            out.append((j, best))
            if not beside(j, best):
                taken[j, best] = True
    return out


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
