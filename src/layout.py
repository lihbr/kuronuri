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
    text HarfBuzz shapes them as kana or hani, and Latin as latn JAN when
    the language is Japanese: language systems Noto Serif JP brings, which
    features added before the merge (Redaction's, the drawn glyphs') do not
    reach. A language system with a feature of the same tag already (Noto
    Serif JP's `kern`) gets the lookups added to it instead: HarfBuzz uses
    only the first feature of a tag in a language system."""
    records = table.FeatureList.FeatureRecord
    shared = [
        i
        for rec in table.ScriptList.ScriptRecord
        if rec.ScriptTag == "DFLT" and rec.Script.DefaultLangSys is not None
        for i in rec.Script.DefaultLangSys.FeatureIndex
        if records[i].FeatureTag in feature_tags
    ]
    for ls in _lang_systems(table):
        for i in shared:
            same = [j for j in ls.FeatureIndex if records[j].FeatureTag == records[i].FeatureTag]
            for j in same:
                feature = records[j].Feature
                feature.LookupListIndex = sorted(
                    set(feature.LookupListIndex) | set(records[i].Feature.LookupListIndex)
                )
            if not same:
                ls.FeatureIndex = sorted({*ls.FeatureIndex, i})


CONTEXTUAL = (ot.ContextSubst, ot.ChainContextSubst, ot.ContextPos, ot.ChainContextPos)


def _nested(lookup):
    """The records of `lookup`, if contextual, that apply other lookups, of
    every subtable, extensions' too."""
    stack = [getattr(st, "ExtSubTable", st) for st in lookup.SubTable]
    stack = [st for st in stack if isinstance(st, CONTEXTUAL)]
    while stack:
        obj = stack.pop()
        if isinstance(obj, (ot.SubstLookupRecord, ot.PosLookupRecord)):
            yield obj
        elif isinstance(obj, list):
            stack.extend(obj)
        elif isinstance(obj, ot.BaseTable) and not isinstance(obj, ot.Coverage):
            stack.extend(v for v in vars(obj).values() if isinstance(v, (list, ot.BaseTable)))


def _remap(table, remap):
    """Point the features and contextual lookups of `table` at the lookups
    {old index: new index}, those dropped (None) at none."""
    for rec in table.FeatureList.FeatureRecord:
        indices = (remap[i] for i in rec.Feature.LookupListIndex)
        rec.Feature.LookupListIndex = [i for i in indices if i is not None]
    for lookup in table.LookupList.Lookup:
        for record in _nested(lookup):
            if remap[record.LookupListIndex] is None:
                raise ValueError(f"a lookup applies lookup {record.LookupListIndex}, removed")
            record.LookupListIndex = remap[record.LookupListIndex]


def insert_lookups(table, lookups, at):
    """Insert `lookups` at index `at` of the lookup list of `table`, a GSUB
    or GPOS: lookups apply in the order of the list, whatever their
    features. Returns their indices."""
    count = len(table.LookupList.Lookup)
    _remap(table, {i: i + len(lookups) if i >= at else i for i in range(count)})
    table.LookupList.Lookup[at:at] = lookups
    return list(range(at, at + len(lookups)))


def remove_lookups(table, indices):
    """Remove the lookups at `indices` from `table`, and from its features."""
    kept = [i for i in range(len(table.LookupList.Lookup)) if i not in set(indices)]
    _remap(table, {old: new for new, old in enumerate(kept)} | {i: None for i in indices})
    table.LookupList.Lookup = [table.LookupList.Lookup[i] for i in kept]


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


def use_lookups(table, tag, lookups):
    """Make the features `tag` there are use `lookups` too, or add one using
    them, for every script and language system. Lookups not in the lookup
    list yet are appended to it, the others are referenced where they are:
    features sharing a lookup apply it once, whichever of them are on."""
    listed = table.LookupList.Lookup
    indices = []
    for lookup in lookups:
        at = next((i for i, other in enumerate(listed) if other is lookup), None)
        if at is None:
            listed.append(lookup)
            at = len(listed) - 1
        indices.append(at)
    records = [r for r in table.FeatureList.FeatureRecord if r.FeatureTag == tag]
    for rec in records:
        rec.Feature.LookupListIndex = sorted({*rec.Feature.LookupListIndex, *indices})
    if not records:
        add_feature(table, tag, None, indices=indices)
    return indices


def add_feature(table, tag, lookup, params=None, at=None, indices=None):
    """Add `lookup`, at the end of the lookup list or at index `at`, and a
    feature `tag` using it, for every script and language system; or, with
    `indices`, a feature using the lookups listed there."""
    if indices is None:
        if at is None:
            table.LookupList.Lookup.append(lookup)
            at = len(table.LookupList.Lookup) - 1
        else:
            insert_lookups(table, [lookup], at)
        indices = [at]
    feature = ot.Feature()
    feature.FeatureParams = params
    feature.LookupListIndex = list(indices)
    rec = ot.FeatureRecord()
    rec.FeatureTag = tag
    rec.Feature = feature
    table.FeatureList.FeatureRecord.append(rec)
    for ls in _lang_systems(table):
        ls.FeatureIndex.append(len(table.FeatureList.FeatureRecord) - 1)
    sort_features(table)
