"""OpenType layout: tabular figures and feature registration.

fontTools recomputes every *Count field on save, so only the lists are kept
in sync here.
"""

from fontTools.otlLib import builder as otl
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib.tables import otTables as ot

from pixel import snap

DIGITS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]


def _lang_systems(table):
    for rec in table.ScriptList.ScriptRecord:
        if rec.Script.DefaultLangSys is not None:
            yield rec.Script.DefaultLangSys
        for lrec in rec.Script.LangSysRecord:
            yield lrec.LangSys


def sort_features(table):
    """Sort FeatureList records by tag, as OTS wants, and remap the indices."""
    records = table.FeatureList.FeatureRecord
    order = sorted(range(len(records)), key=lambda i: records[i].FeatureTag)
    remap = {old: new for new, old in enumerate(order)}
    table.FeatureList.FeatureRecord = [records[i] for i in order]
    for ls in _lang_systems(table):
        ls.FeatureIndex = sorted(remap[i] for i in ls.FeatureIndex)
        if ls.ReqFeatureIndex != 0xFFFF:
            ls.ReqFeatureIndex = remap[ls.ReqFeatureIndex]


def share_features(table, feature_tags):
    """Make the given features, as registered for DFLT, apply under every
    script and language system. Digits are script-neutral, so in Japanese
    text HarfBuzz shapes them as kana or hani; without this `tnum` and `frac`
    would only work next to Latin letters."""
    records = table.FeatureList.FeatureRecord
    wanted = set()
    for rec in table.ScriptList.ScriptRecord:
        if rec.ScriptTag == "DFLT" and rec.Script.DefaultLangSys is not None:
            wanted = {
                i
                for i in rec.Script.DefaultLangSys.FeatureIndex
                if records[i].FeatureTag in feature_tags
            }
    for ls in _lang_systems(table):
        ls.FeatureIndex = sorted(set(ls.FeatureIndex) | wanted)


def add_tabular_figures(font, grid=None):
    """Add zero.tf ... nine.tf, the proportional digits centred on the
    advance of the widest one, and a `tnum` feature for every script and
    language system. On a pixel grid, the advance and offsets stay on it."""
    glyf, hmtx, vmtx = font["glyf"], font["hmtx"], font["vmtx"]
    width = snap(max(hmtx[d][0] for d in DIGITS), grid or 10)
    mapping = {}
    for d in DIGITS:
        g = glyf[d]
        ink = (g.xMin, g.xMax) if g.numberOfContours else (0, hmtx[d][0])
        pen = TTGlyphPen(glyf)
        offset = snap((width - ink[1] + ink[0]) / 2 - ink[0], grid or 1)
        pen.addComponent(d, (1, 0, 0, 1, offset, 0))
        tf = glyf[f"{d}.tf"] = pen.glyph()  # also appends the name to the glyph order
        tf.recalcBounds(glyf)
        hmtx[f"{d}.tf"] = (width, tf.xMin)
        vmtx[f"{d}.tf"] = vmtx[d]
        mapping[d] = f"{d}.tf"
    font.setGlyphOrder(glyf.glyphOrder)
    add_feature(
        font["GSUB"].table, "tnum", otl.buildLookup([otl.buildSingleSubstSubtable(mapping)])
    )


def extend_feature(table, tag, lookup):
    """Append `lookup` to the features `tag` there are, or add one: HarfBuzz
    uses only the first feature of a tag in a language system, so a second
    `vert` would never apply."""
    records = [r for r in table.FeatureList.FeatureRecord if r.FeatureTag == tag]
    if not records:
        add_feature(table, tag, lookup)
        return
    table.LookupList.Lookup.append(lookup)
    for rec in records:
        rec.Feature.LookupListIndex.append(len(table.LookupList.Lookup) - 1)


def add_feature(table, tag, lookup, params=None):
    """Append `lookup` and a feature `tag` using it, for every script and
    language system."""
    table.LookupList.Lookup.append(lookup)
    feature = ot.Feature()
    feature.FeatureParams = params
    feature.LookupListIndex = [len(table.LookupList.Lookup) - 1]
    rec = ot.FeatureRecord()
    rec.FeatureTag = tag
    rec.Feature = feature
    table.FeatureList.FeatureRecord.append(rec)
    for ls in _lang_systems(table):
        ls.FeatureIndex.append(len(table.FeatureList.FeatureRecord) - 1)
    sort_features(table)
