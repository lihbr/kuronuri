#!/usr/bin/env python3
"""Checks for the fonts in dist/.

- OTS, the sanitizer browsers run on web fonts, accepts every font and slice.
- With `tnum`, all digits have the same advance, next to Latin and Japanese.
- `calt` turns -> <- <-> -^ ^- => <=> =^ into arrows, also in Japanese
  text, but leaves <= ^= and the ^-^ ^=^ =^.^= =^_^= emoticons as typed,
  and `ss01` swaps in the alt arrows.
- The vertical metrics are Redaction's, so the baseline sits where it does
  in Redaction for the same line height.
- In pixel variants, every point, advance and component offset is on the grid.
- All kana are present, and every glyph of src/glyphs, but no Hangul,
  Bopomofo or Latin ligatures from Noto Serif JP.
- The glyphs drawn from Redaction's are made of them: fullwidth forms are
  Redaction's glyph centred in the em; Roman numerals, ‼ and ⑴ are as wide
  as what they are made of, set with kerning; enclosed numbers and letters
  are centred on the em box.
- Every outline drawn by hand (glyphs/drawn) loads, is used, and has no
  self-intersections: enclosed content has the pieces and counters of
  Redaction's glyph; 〒 stands upright, as tall as T, its two bars and stem
  as thick as T's (Italic's measured across its slant), in two pieces; the
  owner's arrow head is that of Regular's → as built, in one piece.
- No two superscript letters (ª º, those `ordn` raises, the c of ℅) are
  drawn alike, but on 100, where they are three cells high: there c and e
  have the same placements, and come out alike.
- dist/web: index.css imports every family, each family CSS lists every
  slice with a unicode-range equal to its cmap, the slices of a style do
  not overlap and cover the whole font, and the Latin-only CSS lists the
  latin and latin-ext slices.
"""

import functools
import io
import re
import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import ots
import pathops
import uharfbuzz as hb
from fontTools.pens.basePen import BasePen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont
from fontTools.ufoLib import UFOReader
from fontTools.unicodedata import script

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import glyphs  # noqa: E402
from family import STYLES, redaction  # noqa: E402
from glyphs import arrows, enclosed, fullwidth, numerals, punctuation  # noqa: E402
from glyphs.shapes import DRAWN, _pieces, drawn, path, runs, slope  # noqa: E402
from pixel import snap, snap_advance  # noqa: E402

DIST = Path(__file__).resolve().parent.parent / "dist"
KANA = [*range(0x3041, 0x3097), *range(0x30A1, 0x30FB)]
DIGITS = "0123456789"
FACE = re.compile(
    r'font-family: "([^"]+)";\s*font-style: (\w+);\s*font-weight: (\d+);'
    r'.*?url\("([^"]+)\?no-inline"\).*?unicode-range: ([^;]+);',
    re.S,
)
STYLE = {("normal", "400"): "Regular", ("italic", "400"): "Italic", ("normal", "700"): "Bold"}
ARROWS = {
    "->": 0x2192,
    "<-": 0x2190,
    "<->": 0x2194,
    "-^": 0x2191,
    "^-": 0x2193,
    "=>": 0x21D2,
    "<=>": 0x21D4,
    "=^": 0x21D1,
}
METRICS = {
    "hhea": ("ascent", "descent", "lineGap"),
    "OS/2": ("sTypoAscender", "sTypoDescender", "sTypoLineGap", "usWinAscent", "usWinDescent"),
}
# Ordinals that raise every superscript letter but c (that of ℅)
SUPERIORS = ["1st", "2nd", "3rd", "4th", "1er", "2e", "1a", "1o"]
# ordn: text, and how much of it stays as typed: ordinal suffixes after
# digits are raised, but not other letters, nor suffixes before letters or digits
ORDINALS = {"2nd": "2", "1er": "1", "3as": "3", "3am": "3am", "2e3": "2e3", "1stuff": "1stuff"}
AS_TYPED = ["^-^", "^=^", "=^.^=", "=^_^=", "<=", "^=", "a<=b"]


@functools.cache
def hb_font(path):
    ttf = TTFont(path)
    ttf.flavor = None  # HarfBuzz cannot read WOFF2
    data = io.BytesIO()
    ttf.save(data)
    return hb.Font(hb.Face(hb.Blob(data.getvalue())))


def shape(path, text, features=None, language=None, direction=None):
    """Glyph ids and advances of `text` shaped with HarfBuzz."""
    font = hb_font(path)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    if language:
        buf.language = language
    if direction:
        buf.direction = direction
    hb.shape(font, buf, features or {})
    return [i.codepoint for i in buf.glyph_infos], [p.x_advance for p in buf.glyph_positions]


def tabular(path, text, language=None):
    """Whether the digits in `text` all have the same advance with `tnum`."""
    advances = shape(path, text, {"tnum": True}, language)[1]
    return len({a for a, c in zip(advances, text) if c.isdigit()}) == 1


def sanitize(path):
    res = ots.sanitize(str(path), capture_output=True)
    if res.returncode:
        return [f"{path.name}: OTS: {res.stderr.decode().strip().splitlines()[-1]}"]
    return []


def check_font(path):
    problems = sanitize(path)
    if path.suffix != ".ttf":
        return problems
    if not tabular(path, DIGITS) or not tabular(path, f"価格{DIGITS}円", "ja"):
        problems.append(f"{path.name}: tnum is not tabular")
    font = TTFont(path)
    cmap = font.getBestCmap()
    gid = {cp: font.getGlyphID(name) for cp, name in cmap.items()}
    for text, cp in ARROWS.items():
        if (
            shape(path, text)[0] != [gid[cp]]
            or shape(path, f"東{text}京", None, "ja")[0][1] != gid[cp]
        ):
            problems.append(f"{path.name}: {text} does not turn into {chr(cp)}")
        alt = shape(path, chr(cp), {"ss01": True})[0]
        if alt == [gid[cp]] or shape(path, text, {"ss01": True})[0] != alt:
            problems.append(f"{path.name}: ss01 does not swap in the alt {chr(cp)}")
    for text in AS_TYPED:
        if len(shape(path, text)[0]) != len(text):
            problems.append(f"{path.name}: {text} is not left as typed")
    # Figure features: frac, subs, ordn
    figures = [("1/2", "frac", 0xBD), ("1/10", "frac", 0x2152), ("2", "subs", 0x2082)]
    for text, features, cp in figures:
        if shape(path, text, {features: True})[0] != [gid[cp]]:
            problems.append(f"{path.name}: {features} does not turn {text} into {chr(cp)}")
    for text, kept in ORDINALS.items():
        ordn = shape(path, text, {"ordn": True})[0]
        raised = [len(ordn) != len(text) or g != gid[ord(c)] for g, c in zip(ordn, text)]
        if raised != [i >= len(kept) for i in range(len(text))]:
            problems.append(f"{path.name}: ordn raises other than {text[len(kept) :]} in {text}")
    for text, expected in (("1a", "1ª"), ("No. 5", "№ 5")):
        if shape(path, text, {"ordn": True})[0] != [gid[ord(c)] for c in expected]:
            problems.append(f"{path.name}: ordn does not turn {text} into {expected}")
    # Drawn punctuation turns in vertical Japanese text, as Noto Serif JP's does
    for c in "，．：＝":
        if shape(path, f"日{c}", direction="ttb")[0][1] == gid[ord(c)]:
            problems.append(f"{path.name}: {c} does not turn in vertical text")
    m = re.match(r"Kuronuri(\d*)-(\w+)", path.stem)
    source = redaction(int(m.group(1)) if m.group(1) else None, m.group(2))
    for tag, attrs in METRICS.items():
        for attr in attrs:
            if getattr(font[tag], attr) != getattr(source[tag], attr):
                problems.append(f"{path.name}: {tag} {attr} is not Redaction's")
    if m := re.match(r"Kuronuri(\d+)-", path.name):
        grid = int(m.group(1))
        glyf, hmtx = font["glyf"], font["hmtx"]
        off = 0
        for name in font.getGlyphOrder():
            g = glyf[name]
            if hmtx[name][0] % grid:
                off += 1
            elif g.isComposite():
                off += any(c.x % grid or c.y % grid for c in g.components)
            elif g.numberOfContours > 0:
                off += any(x % grid or y % grid for x, y in g.coordinates)
        if off:
            problems.append(f"{path.name}: {off} glyphs off the {grid}-unit grid")
    if missing := [chr(c) for c in KANA if c not in cmap]:
        problems.append(f"{path.name}: missing kana {''.join(missing)}")
    if missing := [chr(c) for c in glyphs.CODEPOINTS if c not in cmap]:
        problems.append(f"{path.name}: missing drawn glyphs {''.join(missing)}")
    # Redaction has ﬁ and ﬂ, Noto Serif JP the other Latin ligatures.
    ligatures = set(range(0xFB00, 0xFB50)) - {0xFB01, 0xFB02}
    if trimmed := [chr(c) for c in cmap if script(c) in ("Hang", "Bopo") or c in ligatures]:
        problems.append(f"{path.name}: {len(trimmed)} Hangul, Bopomofo or ligatures")
    problems += check_drawn(path, font)
    return problems


def check_drawn(path, font):
    """The glyphs drawn from Redaction's are made of them, where they should be."""
    m = re.match(r"Kuronuri(\d+)-", path.name)
    g = int(m.group(1)) if m else 1
    em = snap_advance(1000, g)
    cmap, hmtx, gs = font.getBestCmap(), font["hmtx"], font.getGlyphSet()

    def bounds(cp):
        pen = BoundsPen(gs)
        gs[cmap[cp]].draw(pen)
        return tuple(round(v, 3) for v in pen.bounds)

    problems = []
    for cp, c in fullwidth.SOURCES.items():
        dx = snap((em - hmtx[cmap[ord(c)]][0]) / 2, g)
        x0, y0, x1, y1 = bounds(ord(c))
        moved = tuple(round(v, 3) for v in (x0 + dx, y0, x1 + dx, y1))
        if hmtx[cmap[cp]][0] != em or bounds(cp) != moved:
            problems.append(f"{path.name}: {chr(cp)} is not {c} centred in the em")
    for cp, letters in (numerals.SOURCES | punctuation.SOURCES | enclosed.TYPED).items():
        if [hmtx[cmap[cp]][0]] != [snap(sum(shape(path, letters, {"liga": False})[1]), g)]:
            problems.append(f"{path.name}: {chr(cp)} is not as wide as {letters}")
    # Raised ones (🅪) are as high as ™, not centred up and down
    raised = {
        cp for kind, contents, _, _ in enclosed.ENCLOSURES if kind == "raised" for cp in contents
    }
    for cp in enclosed.ENCLOSED:
        x0, y0, x1, y1 = bounds(cp)
        if (
            hmtx[cmap[cp]][0] != em
            or abs(x0 + x1 - em) > g
            or (cp not in raised and abs(y0 + y1 - 2 * enclosed.CENTRE) > 2 * g)
            or (g > 1 and (x0 < g or x1 > em - g))
        ):
            problems.append(f"{path.name}: {chr(cp)} is not centred in the em box")
    if g != 100:
        order, glyf = font.getGlyphOrder(), font["glyf"]
        letters = {"c": glyf[cmap[0x2105]].components[0].glyphName}
        for text in SUPERIORS:
            for c, i in zip(text[1:], shape(path, text, {"ordn": True})[0][1:]):
                letters[c] = order[i]
        drawn = defaultdict(list)
        for c, name in sorted(letters.items()):
            coords, ends, _ = glyf[name].getCoordinates(glyf)
            x0, y0 = min(x for x, _ in coords), min(y for _, y in coords)
            drawn[tuple((x - x0, y - y0) for x, y in coords), tuple(ends)].append(c)
        for alike in (cs for cs in drawn.values() if len(cs) > 1):
            problems.append(f"{path.name}: superscript {' '.join(alike)} are drawn alike")
    return problems


class _Flat(BasePen):
    """The edges of an outline, its curves cut in STEPS lines, per contour."""

    STEPS = 8

    def __init__(self):
        super().__init__(None)
        self.contours = []

    def _moveTo(self, pt):
        self.contours.append([pt])

    def _lineTo(self, pt):
        self.contours[-1].append(pt)

    def _qCurveToOne(self, a, b):
        p0 = self._getCurrentPoint()
        for i in range(1, self.STEPS + 1):
            t = i / self.STEPS
            self.contours[-1].append(
                tuple((1 - t) ** 2 * p0[k] + 2 * (1 - t) * t * a[k] + t * t * b[k] for k in (0, 1))
            )

    def _curveToOne(self, a, b, c):
        p0 = self._getCurrentPoint()
        for i in range(1, self.STEPS + 1):
            t, u = i / self.STEPS, 1 - i / self.STEPS
            w = (u**3, 3 * u * u * t, 3 * u * t * t, t**3)
            pts = (p0, a, b, c)
            self.contours[-1].append(tuple(sum(wi * q[k] for wi, q in zip(w, pts)) for k in (0, 1)))


def crossings(p):
    """How many pairs of edges of path `p` cross, but those that meet."""
    flat = _Flat()
    p.draw(flat)
    edges = np.array(
        [(*a, *b) for c in flat.contours for a, b in zip(c, c[1:] + c[:1]) if a != b], float
    )
    x0, y0, x1, y1 = edges.T

    def side(px, py, ax, ay, bx, by):
        return (bx - ax) * (py[:, None] - ay) - (by - ay) * (px[:, None] - ax)

    d1 = side(x0, y0, x0[None], y0[None], x1[None], y1[None]).T
    d2 = side(x1, y1, x0[None], y0[None], x1[None], y1[None]).T
    d3, d4 = d1.T, d2.T
    crossed = (d1 * d2 < 0) & (d3 * d4 < 0)
    return int(np.triu(crossed, 1).sum())


def check_hand():
    """Every outline drawn by hand (shapes.drawn) loads, is used, and does not
    cross itself: enclosed content (enclosed.by_hand) is content of an
    enclosure, made heavier so, with the pieces and counters of Redaction's
    glyph, and slanted content drawn for another style than Italic's (Bold's
    🄬) is used there, of Italic's glyph; 〒 is fullwidth's (check_postal);
    the owner's arrow head is arrows' (check_arrows)."""
    problems = []
    used = {c for _, contents, _, _ in enclosed.ENCLOSURES for t in contents.values() for c in t}
    slanted = {
        c for _, contents, _, s in enclosed.ENCLOSURES if s for t in contents.values() for c in t
    }
    postal = chr(fullwidth.POSTAL)
    italic = redaction(None, "Italic")
    for style in STYLES:
        ufo = DRAWN / f"{style}.ufo"
        every, hand = drawn(style), enclosed.by_hand(style)
        theirs = enclosed.by_hand(style, True)
        if ufo.exists() and len(UFOReader(ufo).getGlyphSet()) != len(every) + len(
            drawn(style, True)
        ):
            problems.append(f"{ufo.name}: not every glyph loads, with a code point")
        font = redaction(None, style)
        for c, (p, amount) in theirs.items():
            plan = (0, enclosed._limit("Italic", c), 0)
            q, route = enclosed._heavy(italic, c, plan, enclosed._of(c), style)
            k = (q.bounds[3] - q.bounds[1]) / (p.bounds[3] - p.bounds[1])
            if style == "Italic" or c not in slanted or route != "drawn":
                problems.append(f"{ufo.name}: slanted {c} is not used")
            elif abs(abs(q.area) - abs(p.area) * k * k) > 1:
                problems.append(f"{ufo.name}: slanted {c} is not the one drawn for it")
            if not amount > 0 or _pieces(p) != _pieces(path(italic, c)):
                problems.append(f"{ufo.name}: slanted {c} is not Redaction's made heavier")
            if crossed := crossings(p):
                problems.append(f"{ufo.name}: slanted {c} crosses itself ({crossed})")
        for c in sorted(set(every) - set(hand) - {postal} - set(arrows.SOURCES)):
            problems.append(f"{ufo.name}: {c} is not used")
        for c, (p, amount) in hand.items():
            plan = (0, enclosed._limit(style, c), 0)
            if c not in used or enclosed._heavy(font, c, plan, enclosed._of(c))[1] != "drawn":
                problems.append(f"{ufo.name}: {c} is not used")
            if not amount > 0 or _pieces(p) != _pieces(path(font, c)):
                problems.append(f"{ufo.name}: {c} is not Redaction's made heavier")
        for c, (p, _) in every.items():
            if c in arrows.SOURCES:  # as SVGs are filled, by their winding: → twists at its notch
                p = pathops.simplify(p, clockwise=True)
            if crossed := crossings(p):
                problems.append(f"{ufo.name}: {c} crosses itself ({crossed})")
        if postal in every:
            problems += [f"{ufo.name}: 〒 {p}" for p in check_postal(font, every[postal][0])]
        if any(c in every for c in arrows.SOURCES):
            problems += [f"{ufo.name}: {p}" for p in check_arrows(font, every)]
    return problems


def check_arrows(font, every):
    """The owner's head of → (`every`, the glyphs drawn by hand for `font`, a
    Redaction style) is in one piece, and that of its → as built: within
    it, as tall; only in Regular."""
    problems = []
    if font["name"].getDebugName(2) != "Regular":
        return [f"{c} is drawn in another style than Regular" for c in arrows.SOURCES]
    built = arrows._paths(arrows.Arrows(arrows.Pen(font, font)))
    for c, name in zip(arrows.SOURCES, ("arrowright",)):
        if c not in every:
            problems.append(f"{c} is missing")
            continue
        p = every[c][0]
        if _pieces(p) != (1, 0):
            problems.append(f"{c} is not one piece")
        b = built[name]
        x0, y0, x1, y1 = p.bounds
        bx0, by0, bx1, by1 = b.bounds
        p = p.transform(1, 0, 0, 1, bx1 - x1, 0)  # tips together
        out = abs(pathops.op(p, b, pathops.PathOp.DIFFERENCE).area)
        if out > 1 or abs((y1 - y0) - (by1 - by0)) > 1:  # as tall as its head
            problems.append(f"{c} is not the head of {name} as built")
    return problems


def check_postal(font, p):
    """〒 drawn by hand, `p`, of `font`, a Redaction style, is fullwidth's:
    as drawn in its smooth font, centred; upright, as tall as T, in two
    pieces without counters, its two bars as thick as T's, its stem as T's
    measured across (Italic's slanted)."""
    problems = []
    built = pathops.Path()
    fullwidth._postal(font, font, None, 1000).draw(pathops.PathPen(built), None)
    if round(abs(built.area)) != round(abs(p.area)) or built.bounds[1::2] != p.bounds[1::2]:
        problems.append("is not used")
    t = path(font, "T")
    if p.bounds[1::2] != t.bounds[1::2]:
        problems.append("is not as tall as T")
    if _pieces(p) != (2, 0):
        problems.append("is not two pieces")
    top = t.bounds[3]
    bar = top - max(y for _, y in path_points(t) if y < top)
    x0, _, x1, _ = p.bounds
    bars = [r for r in runs(p, x=x0 + (x1 - x0) / 4) if r[0] > p.bounds[1]]  # not the foot
    if len(bars) != 2 or any(abs(b - a - bar) > 1 for a, b in bars):
        return [*problems, f"bars are not as thick as T's ({bar:.0f})"]
    below = bars[0][0]
    a, b = runs(t, y=below / 2)[0]
    across = (b - a) / (1 + slope(font) ** 2) ** 0.5
    stems = [runs(p, y=below * k) for k in (0.3, 0.7)]
    if any(len(r) != 1 for r in stems) or stems[0] != stems[1]:
        problems.append("does not stand upright")
    elif abs(stems[0][0][1] - stems[0][0][0] - across) > 2:
        problems.append(f"stem is not as thick as T's ({across:.0f})")
    return problems


def path_points(p):
    """The points of path `p`, on and off its curves."""
    return [pt for _, pts in p.segments for pt in pts]


def check_slice(task):
    path, declared = task
    problems = sanitize(path)
    cmap = set(TTFont(path).getBestCmap())
    if cmap != declared:
        problems.append(f"{path.name}: unicode-range differs from cmap")
    if re.search(r"-latin-\d", path.name):
        if not tabular(path, DIGITS):
            problems.append(f"{path.name}: tnum is not tabular")
        arrow, alt = shape(path, "->")[0], shape(path, "->", {"ss01": True})[0]
        if len(arrow) != 1 or len(alt) != 1 or arrow == alt:
            problems.append(f"{path.name}: -> does not turn into an arrow, or its alt")
    return cmap, problems


def parse_range(text):
    cps = set()
    for part in text.split(","):
        a, _, b = part.strip()[2:].partition("-")
        cps.update(range(int(a, 16), int(b or a, 16) + 1))
    return cps


def check_web():
    web = DIST / "web"
    families = sorted(
        p.name for p in web.glob("*.css") if p.name != "index.css" and not p.stem.endswith("-latin")
    )
    problems = []
    if sorted(re.findall(r'@import "\./([^"]+)";', (web / "index.css").read_text())) != families:
        problems.append("index.css does not import every family")
    for css in families:
        latin = (web / css.replace(".css", "-latin.css")).read_text()
        if FACE.findall(latin) != [
            face
            for face in FACE.findall((web / css).read_text())
            if re.search(r"-latin(-ext)?-", face[3])
        ]:
            problems.append(f"{css}: the Latin-only CSS does not list its latin slices")
    faces = [face for css in families for face in FACE.findall((web / css).read_text())]
    if unlisted := set((web / "files").iterdir()) - {web / url for *_, url, _ in faces}:
        problems.append(f"{len(unlisted)} slices missing from the CSS")
    if missing := [url for *_, url, _ in faces if not (web / url).exists()]:
        return problems + [f"the CSS lists missing files: {missing[:3]}"]
    tasks = [(web / url, parse_range(rng)) for *_, url, rng in faces]
    by_font = defaultdict(list)
    with ProcessPoolExecutor() as ex:
        for (family, style, weight, *_), (cmap, probs) in zip(
            faces, ex.map(check_slice, tasks, chunksize=16)
        ):
            problems += probs
            by_font[f"{family.replace(' ', '')}-{STYLE[style, weight]}"].append(cmap)
    for ps, cmaps in by_font.items():
        union = set().union(*cmaps)
        if sum(map(len, cmaps)) != len(union):
            problems.append(f"{ps}: slices overlap")
        if union != set(TTFont(DIST / "ttf" / f"{ps}.ttf").getBestCmap()):
            problems.append(f"{ps}: slices do not cover the font")
    return problems


def main():
    fonts = sorted(DIST.glob("ttf/*.ttf")) + sorted(DIST.glob("woff2/*.woff2"))
    if not fonts:
        sys.exit("no fonts in dist/, run the build first")
    with ProcessPoolExecutor() as ex:
        problems = [p for font in ex.map(check_font, fonts) for p in font]
    problems += check_web()
    problems += check_hand()
    for p in problems:
        print("FAIL", p)
    slices = len(list((DIST / "web" / "files").iterdir()))
    print(f"{len(fonts)} fonts, {slices} slices: {len(problems)} problems")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
