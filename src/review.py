#!/usr/bin/env python3
"""Review the glyphs drawn by draw.py, in every variant and style.

Draws the fonts, then writes .tmp/review, what the site's /review page shows
(`pnpm dev`, in development only): review.json, for each module of glyphs/
a grid of its glyphs (and of Redaction's it draws anew on some grids,
`REDRAWN`) and text to edit, with the features in its `FEATURES` on and
switches for the others, `kern` and the text's language; and the fonts:
- fonts/, the drawn fonts, for the grids, and fonts/approved/, the approved
  ones, without features: they may predate the glyphs features need;
- fonts/text/, for the text: each drawn font merged with Noto Serif JP as
  the build merges them (build.merged), so text shapes there as in the
  built fonts, every feature, width forms and Japanese included. Only that
  is equivalent: features make glyphs of Noto's (fwid turns a space into
  U+3000), and classes of every letter (ordn ends at a kanji) do not see
  Noto's from another font. Cached in .cache/review, by what makes them
  (text_key): a few minutes once src/ changes, seconds otherwise;
- fonts/before/, the same text in the fonts before: those approved last,
  merged so (.cache/approved/text), or, for those not approved yet, a copy
  of the built fonts of the directory `--before` names, say a checkout's
  dist/ttf, taken when it is given (.cache/approved/before, with where
  from, when and their hashes in before.json, which the page shows): a
  later build there does not change it. It is kept until --before is given
  again: the noto tab compares with it too. A font with neither is reported.

Glyphs whose outline or advance changed since the fonts were last approved
are listed as changed, and those the approved fonts lack as new. --approve
makes the current fonts the reference (.cache/approved); the first review
approves them. Each module of each font, and its changed glyphs, has a
revision, a hash of its glyphs and, for a module with `FEATURES`, of its
samples as they shape (with them on, across and down), so the page can
tell which ones were reviewed before they changed.

.tmp/watch.txt lists glyphs to look at closely, by style: the page shows them
apart, approved, now and over each other, with text to set them in.

The Japanese, Noto Serif JP as build.py merges it, pixelated by pixel.py, is
reviewed in its own tab, noto: in text next to the Latin, before, now, over
each other, and at grade 0 for reference; vertically too; and the characters
that changed, listed. Before is the built fonts of a directory named with
--before (say a checkout's dist/ttf, built before the change): they are
copied into .cache/approved/before, with where they came from, when, and
their hashes (before.json), shown on the page: the snapshot of fonts/before/
above. Only --before makes or replaces that reference, never a review, an
approval or a build; without one, the noto tab says so and compares
nothing. A character changed if anything of it
set alone does: its outline, advances, vertical alternate and origin,
variation sequences, or palt and vpal (_signature). The page loads the
Japanese cut down to kana, punctuation, the most common kanji (Google's most
frequent slices, web.py), the text of JAPANESE and VERTICAL and the
characters of .tmp/watch.txt; it marks others of its text as not compared:
add them to .tmp/watch.txt.

usage: review.py [--approve] [--before DIR] [--variants 0,10,...]
                 [--styles Regular,Italic,Bold]
"""

import argparse
import hashlib
import io
import json
import shutil
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import fontTools
import uharfbuzz as hb
from fontTools import subset
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._c_m_a_p import cmap_format_12

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build  # noqa: E402
import draw  # noqa: E402
import glyphs  # noqa: E402
import layout  # noqa: E402
import web  # noqa: E402
from family import (  # noqa: E402
    CACHE,
    GRIDS,
    ROOT,
    STYLES,
    family_name,
    log,
    noto_weight,
    ps_name,
    subset_options,
    variants,
)

APPROVED = CACHE / "approved"
SNAPSHOT = APPROVED / "before"  # the built fonts --before names: text before, and the noto tab's
RECORD = APPROVED / "before.json"  # where they come from, when, and their hashes
LEGACY = APPROVED / "before.txt"  # the directory, as review.py kept it before
INK = SNAPSHOT / "reference.json"  # the record, as the noto tab kept it before
TEXT = CACHE / "review"
OUT = ROOT / ".tmp" / "review"
WATCH = ROOT / ".tmp" / "watch.txt"
PUA = 0xF0000  # review fonts map glyphs without a code point (alternates) from here
# The text of the noto tab, the Japanese: the colour of running text next to
# Latin, a line of each, dense kanji whose counters the grid closes first,
# pairs a lost stroke turns into one another, and kana
JAPANESE = [
    "黒塗りは Redaction の日本語版。政府は報告書の一部を黒塗りにして公開し、議論を呼んだ。",
    "The government published the report with parts blacked out, and it was argued about.",
    "鬱驚響警鷹髪議機曜麗襲魔 書重車東 間問聞開",
    "書昔 間問 聞冊 車巾 主全 亜 報告書 きぎ さざ テデ",
    "日目 土士 未末 大太犬 己已巳 千干 人入 刀力 王玉 白百 右石 問間 杮柿",
    "あいうえお かきくけこ ぁぃぅぇぉっゃゅょ べぺ ぶぷ",
    "アイウエオ カキクケコ ァィゥェォッャュョ ベペ ブプ",
]
# ...and set vertically: brackets, punctuation, small kana and the long vowel mark
VERTICAL = "「黒塗り」は、東京の書体。ーっゃ（例）『議事録』【報告】〈一部〉"
FREQUENT = 105  # Google's slices from this one up are the noto tab's kanji, about 600


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


def revision(now, names, shaped=""):
    """A hash of the glyphs `names` of `now`, an outlines(), and of how
    samples `shaped` (shaping()): what the page keeps when they are
    reviewed, until it changes."""
    return hashlib.sha1(repr([now.get(n) for n in names]).encode() + shaped.encode()).hexdigest()


def shaping(path, samples, features):
    """A hash of `samples` shaped in the font at `path` with `features` on,
    across and down: the outline and position of every glyph, which their
    ids are not (a glyph added before them moves them)."""
    font = TTFont(path)
    gs, order = font.getGlyphSet(), font.getGlyphOrder()
    face = hb.Font(hb.Face(hb.Blob(Path(path).read_bytes())))
    drawn, key = {}, hashlib.sha1()
    for text in samples:
        for direction in (None, "ttb"):
            buf = hb.Buffer()
            buf.add_str(text)
            buf.guess_segment_properties()
            if direction:
                buf.direction = direction
            hb.shape(face, buf, dict.fromkeys(features, True))
            for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
                if info.codepoint not in drawn:
                    pen = DecomposingRecordingPen(gs)
                    gs[order[info.codepoint]].draw(pen)
                    drawn[info.codepoint] = hashlib.sha1(repr(pen.value).encode()).hexdigest()
                position = (pos.x_advance, pos.y_advance, pos.x_offset, pos.y_offset)
                key.update(f"{drawn[info.codepoint]} {position} ".encode())
            key.update(b"\n")
    return key.hexdigest()


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


def japanese_characters(watched, text):
    """The characters the Japanese review fonts keep: kana, punctuation and
    fullwidth forms, the most frequent kanji, JAPANESE, VERTICAL, and those
    of .tmp/watch.txt. Glyphs drawn in glyphs/ are left out, as from the
    build."""
    cps = {*range(0x3000, 0x3100), *range(0x31F0, 0x3200), *range(0xFF00, 0xFFF0)}
    for sl in web.SLICES:
        if sl["name"].isdigit() and int(sl["name"]) >= FREQUENT:
            cps |= {c for a, b in sl["ranges"] for c in range(a, b + 1)}
    cps |= {ord(c) for c in "".join([*JAPANESE, VERTICAL, *watched.values(), text])}
    return cps - set(glyphs.CODEPOINTS)


def japanese(sources, grids, styles, record):
    """{(grid, style): (now, before)}: the paths of Noto Serif JP as the
    build merges it, pixelated by pixel.py (`sources`, build.notos), and of
    the built font of the reference (`record`, snapshot()), or None."""
    out = {}
    for style in styles:
        for grid in grids:
            now = sources[noto_weight(STYLES[style]["weight"], grid), grid]
            ps = ps_name(grid, style)
            before = record and ps in record["fonts"] and SNAPSHOT / f"{ps}.ttf"
            out[grid, style] = now, before or None
    return out


def japanese_font(src, dst, cps):
    """`src` cut down to `cps`, as WOFF2 at `dst`; returns {character: its
    _signature} of what it keeps, to tell which changed. The reference, a
    built font, has Redaction too: the review fonts set it."""
    font = TTFont(src)
    s = subset.Subsetter(subset_options())
    s.populate(unicodes=cps)
    s.subset(font)
    data = io.BytesIO()
    font.save(data)
    shaper = hb.Font(hb.Face(hb.Blob(data.getvalue())))
    sequences = {}  # base code point: its variation selectors
    for table in font["cmap"].tables:
        if table.format == 14:
            for selector, pairs in table.uvsDict.items():
                for base, _ in pairs:
                    sequences.setdefault(base, []).append(selector)
    drawn = {}  # glyph id: its outline
    out = {}
    for cp in sorted(font.getBestCmap()):
        out[chr(cp)] = _signature(shaper, font, drawn, cp, sorted(sequences.get(cp, [])))
    font.flavor = "woff2"
    font.save(dst)
    return out


SHAPINGS = [("ltr", {}), ("ltr", {"palt": True}), ("ttb", {}), ("ttb", {"vpal": True})]


def _signature(shaper, font, drawn, cp, selectors):
    """What a character looks like, set alone: for it and each of its
    variation sequences, horizontally and vertically, with and without
    palt and vpal, the outlines it is set in, where, and their advances."""
    out = []
    for text in [chr(cp), *(chr(cp) + chr(v) for v in selectors)]:
        for direction, features in SHAPINGS:
            buf = hb.Buffer()
            buf.add_str(text)
            buf.guess_segment_properties()
            buf.direction = direction
            hb.shape(shaper, buf, features)
            for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
                gid = info.codepoint
                if gid not in drawn:
                    gs = font.getGlyphSet()
                    pen = DecomposingRecordingPen(gs)
                    gs[font.getGlyphName(gid)].draw(pen)
                    drawn[gid] = tuple(pen.value)
                out.append((drawn[gid], pos.x_advance, pos.y_advance, pos.x_offset, pos.y_offset))
    return tuple(out)


def _digest(path):
    """A hash of the file at `path`."""
    return hashlib.sha1(Path(path).read_bytes()).hexdigest()


def _tables(path):
    """A hash of the font at `path` but when it was saved: head's created
    and modified dates, and the checksums they change. A font drawn again
    the same hashes the same."""
    font, key = TTFont(path, lazy=True), hashlib.sha1()
    for tag in sorted(font.reader.keys()):
        data = bytearray(font.reader[tag])
        if tag == "head":
            data[8:12] = bytes(4)  # checksumAdjustment
            data[20:36] = bytes(16)  # created, modified
        key.update(tag.encode() + len(data).to_bytes(4) + bytes(data))
    return key.hexdigest()


def text_key(grid, style, noto, code):
    """What the text font of `grid` and `style` is made of: the drawn font
    (_tables), the contents of the Noto instance merged with it, which
    build.notos made of the inputs it records (build.instancing), and
    `code`, src/ by path and contents, and the fontTools merging them."""
    key = hashlib.sha1(f"{_tables(draw.path(grid, style))} {_digest(noto)}".encode())
    key.update(code)
    return key.hexdigest()[:8]


def text_fonts(sources, grids, styles):
    """{PostScript name: path} of the drawn fonts merged with Noto Serif JP
    as the build merges them (`sources`, build.notos), cached in TEXT by
    what makes them (text_key)."""
    code = hashlib.sha1(fontTools.version.encode())
    src = ROOT / "src"
    for f in sorted(src.rglob("*")):
        if f.is_file() and "__pycache__" not in f.parts:
            data = f.read_bytes()
            code.update(f"{f.relative_to(src).as_posix()}\0{len(data)}\0".encode() + data)
    tasks, out = [], {}
    for grid in grids:
        for style in styles:
            noto = sources[noto_weight(STYLES[style]["weight"], grid), grid]
            ps = ps_name(grid, style)
            out[ps] = TEXT / f"{ps}-{text_key(grid, style, noto, code.digest())}.ttf"
            if not out[ps].exists():
                tasks.append((grid, style, noto, out[ps]))
    TEXT.mkdir(parents=True, exist_ok=True)
    for f in TEXT.glob("*.ttf"):  # older ones of these fonts
        if f.name.rsplit("-", 1)[0] in out and f not in out.values():
            f.unlink()
    if tasks:
        log(f"merging {len(tasks)} fonts with Noto Serif JP for their text")
        with ProcessPoolExecutor(4) as ex:  # about 1.5 GB each
            list(ex.map(_text_font, tasks))
    else:
        log(f"text fonts cached, {len(out)}")
    return out


def _text_font(task):
    grid, style, noto, dst = task
    build.merged(grid, style, noto).save(dst)


def snapshot(directory):
    """Copy the built fonts of `directory` into SNAPSHOT, the text before
    until approved, and record where they come from, when, and their
    hashes (RECORD)."""
    fonts = sorted(Path(directory).glob("Kuronuri*.ttf"))
    if not fonts:
        sys.exit(f"--before {directory}: no built fonts (Kuronuri*.ttf) there")
    shutil.rmtree(SNAPSHOT, ignore_errors=True)
    SNAPSHOT.mkdir(parents=True)
    hashes = {}
    for f in fonts:
        shutil.copy2(f, SNAPSHOT / f.name)
        hashes[f.stem] = _digest(SNAPSHOT / f.name)
    built = max(f.stat().st_mtime for f in fonts)
    record = {
        "source": str(Path(directory).resolve()),
        "built": time.strftime("%Y-%m-%d %H:%M", time.localtime(built)),
        "taken": time.strftime("%Y-%m-%d %H:%M"),
        "hash": hashlib.sha1(json.dumps(hashes, sort_keys=True).encode()).hexdigest(),
        "fonts": hashes,
    }
    RECORD.write_text(json.dumps(record, indent="\t"))
    LEGACY.unlink(missing_ok=True)
    log(f"text before: {len(fonts)} fonts of {record['source']}, built {record['built']}")
    return record


def reference():
    """The record of SNAPSHOT, those of its fonts that are as taken; taken
    first from the directory a LEGACY file names, or recorded from INK, the
    noto tab's record of the same snapshot."""
    if not RECORD.exists() and INK.exists():
        ink = json.loads(INK.read_text())
        fonts = {ps: _digest(SNAPSHOT / f"{ps}.ttf") for ps in ink["fonts"]}
        record = {
            "source": ink["from"],
            "built": ink["at"][:16],  # it kept when taken only
            "taken": ink["at"][:16],
            "hash": ink["hash"],  # kept, so the noto tab's revisions hold
            "fonts": fonts,
        }
        RECORD.write_text(json.dumps(record, indent="\t"))
        INK.unlink()
    if not RECORD.exists() and LEGACY.exists():
        directory = Path(LEGACY.read_text().strip())
        if not directory.is_dir():
            log(f"WARNING: {LEGACY} names {directory}, which is gone: no text before")
            return None
        return snapshot(directory)
    if not RECORD.exists():
        return None
    record = json.loads(RECORD.read_text())
    for ps, digest in list(record["fonts"].items()):
        path = SNAPSHOT / f"{ps}.ttf"
        if not path.exists() or _digest(path) != digest:
            log(f"WARNING: {path} is not as taken from {record['source']}: not used")
            del record["fonts"][ps]
    return record


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--approve", action="store_true", help="approve the drawn fonts")
    ap.add_argument(
        "--before",
        type=Path,
        help="built fonts to compare text and the Japanese with, copied as reference",
    )
    ap.add_argument("--variants", default="0," + ",".join(map(str, GRIDS)))
    ap.add_argument("--styles", default=",".join(STYLES))
    args = ap.parse_args()
    grids, styles = variants(args.variants), args.styles.split(",")
    draw.draw_all(grids, styles)
    APPROVED.mkdir(parents=True, exist_ok=True)
    record = snapshot(args.before) if args.before else reference()
    if record is None:
        log("NO REFERENCE for the Japanese: the noto tab compares nothing.")
        log("Name the built fonts to compare it with: review.py --before DIR (say dist/ttf")
        log("of a checkout built before the change).")
    sources = build.notos(grids, styles, fresh=False)
    text = text_fonts(sources, grids, styles)
    if args.approve:  # the text fonts too; the snapshot stays, the noto tab's reference
        (APPROVED / "text").mkdir(exist_ok=True)
        for ps, path in text.items():
            shutil.copy(path, APPROVED / "text" / f"{ps}.ttf")
    shutil.rmtree(OUT, ignore_errors=True)
    for d in ("approved", "text", "before", "japanese/before"):
        (OUT / "fonts" / d).mkdir(parents=True)

    members = {  # module name: its glyph names, and those of Redaction it redraws
        m.__name__.split(".")[-1]: [
            *m.CODEPOINTS.values(),
            *m.ALTERNATES,
            *getattr(m, "REDRAWN", []),
        ]
        for m in glyphs.MODULES
    }
    drawn = [n for names in members.values() for n in names]
    watched, watch_text = watch()
    notos = japanese(sources, grids, styles, record)
    kept = japanese_characters(watched, watch_text)
    noto_chars = set()  # every character the Japanese of the fonts has
    fonts, widest, missing = [], {}, []  # glyph name: widest advance in any font, in em
    featured = {m.__name__.split(".")[-1]: m for m in glyphs.MODULES if getattr(m, "FEATURES", [])}
    for style in styles:
        for grid in grids:
            ps = ps_name(grid, style)
            src, approved = draw.path(grid, style), APPROVED / f"{ps}.ttf"
            if args.approve or not approved.exists():
                shutil.copy(src, approved)
            font = TTFont(src)
            now = outlines(font)
            changed, new = changes(now, outlines(TTFont(approved)))
            review_font(src, OUT / "fonts" / f"{ps}.ttf")
            review_font(approved, OUT / "fonts" / "approved" / f"{ps}.ttf", features=False)
            shutil.copy(text[ps], OUT / "fonts" / "text" / f"{ps}.ttf")
            before = None
            for kind, path in (
                ("approved", APPROVED / "text" / f"{ps}.ttf"),
                ("built", record and ps in record["fonts"] and SNAPSHOT / f"{ps}.ttf"),
            ):
                if before is None and path and path.exists():
                    shutil.copy(path, OUT / "fonts" / "before" / f"{ps}.ttf")
                    before = kind
            if before is None:
                missing.append(ps)
            chars = characters(font)
            changed = [n for n in chars if n in changed]  # in the order of the font
            cmap = font.getBestCmap()
            names = (cmap.get(ord(c)) for c in watched.get("*", "") + watched.get(style, ""))
            watching = list(dict.fromkeys(n for n in names if n in chars))  # in its order
            now_jp, ref_jp = notos[grid, style]
            every = set(TTFont(now_jp).getBestCmap()) - set(glyphs.CODEPOINTS)
            noto_chars |= every
            jp = japanese_font(now_jp, OUT / "fonts" / "japanese" / f"{ps}.woff2", kept & every)
            jp_ref = {}
            if ref_jp:
                jp_ref = japanese_font(
                    ref_jp, OUT / "fonts" / "japanese" / "before" / f"{ps}.woff2", kept & every
                )
            jp_changed = "".join(c for c, v in jp.items() if ref_jp and jp_ref.get(c) != v)
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
                    "before": before,  # what its text is compared with, if anything
                    # of the glyphs it shows: drawn, changed or new
                    "characters": {
                        n: c for n, c in chars.items() if n in {*drawn, *changed, *new, *watching}
                    },
                    "changed": changed,
                    "watch": watching,
                    "new": [n for n in chars if n in new],
                    # of its Japanese review font: the characters that changed
                    # since the reference, how many it keeps, and whether the
                    # reference has this font
                    "noto": {"changed": jp_changed, "count": len(jp), "before": bool(ref_jp)},
                    "revisions": {
                        **{
                            module: revision(
                                now,
                                names,
                                module in featured
                                and shaping(
                                    text[ps], featured[module].SAMPLES, featured[module].FEATURES
                                )
                                or "",
                            )
                            for module, names in {
                                **members,
                                "changed": changed,
                                "watch": watching,
                            }.items()
                        },
                        "noto": revision(
                            {**jp, "before": record and record["hash"]}, [*jp, "before"]
                        ),
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
        "watch": watch_text,
        # the built fonts text is compared with till approved: where from, when, a hash
        "reference": record and {k: v for k, v in record.items() if k != "fonts"},
        # to turn on and off in the text: those of every script (glyphs.SHARED),
        # but calt, on anyway, and ss01 and kern, which have their own switch
        "features": sorted(glyphs.SHARED["GSUB"] - {"calt", "ss01"}),
        "noto": {
            "text": JAPANESE,
            "vertical": VERTICAL,
            # what the Japanese review fonts keep, of every character of Noto's
            "kept": "".join(map(chr, sorted(kept & noto_chars))),
            "characters": "".join(map(chr, sorted(noto_chars))),
            # the same snapshot as "reference"
            "reference": record
            and {"from": record["source"], "at": record["taken"], "hash": record["hash"]},
        },
    }
    (OUT / "review.json").write_text(json.dumps(review, ensure_ascii=False, indent="\t"))
    if missing:
        log(
            f"WARNING: no text before for {len(missing)} fonts, neither approved nor in a "
            f"--before snapshot: {', '.join(missing)}"
        )
    log(
        f"{sum(len(f['changed']) for f in fonts)} glyphs changed, "
        f"{sum(len(f['new']) for f in fonts)} new since approved, "
        f"{sum(len(f['noto']['changed']) for f in fonts)} Japanese"
        + ("" if record else " (no reference: --before DIR)")
    )
    log("http://localhost:3000/review (pnpm dev)")


if __name__ == "__main__":
    main()
