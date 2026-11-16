import { defineEventHandler } from "nuxt/server"

// Written by the font build (src/build.py)
import origins from "../data/glyphs.json"

// Nitro imports CSS as text
import css from "@lihbr/kuronuri/kuronuri-0.css"

export type Kind = { kind: string; characters: string }
/** Characters that are Redaction's as they are, and drawn from them: the rest is Noto Serif JP's */
export type Origins = { redaction: string; drawn: string }

// Kinds of glyph, by Unicode block: the first whose ranges hold a character has it, the last has
// the rest
const KINDS: [kind: string, ranges: [number, number][]][] = [
	// Basic Latin to IPA and spacing modifiers, combining accents, Latin Extended Additional,
	// superscripts and subscripts, currency, ligatures (ﬁ)
	[
		"latin",
		[
			[0x0000, 0x036f],
			[0x1e00, 0x1eff],
			[0x2070, 0x20cf],
			[0xfb00, 0xfb4f],
		],
	],
	// General, supplemental, CJK, vertical, compatibility and small form punctuation
	[
		"punctuation",
		[
			[0x2000, 0x206f],
			[0x2e00, 0x2e7f],
			[0x3000, 0x303f],
			[0xfe10, 0xfe1f],
			[0xfe30, 0xfe6f],
		],
	],
	// Number forms (⅓ Ⅻ), operators, mathematical symbols
	[
		"maths",
		[
			[0x2150, 0x218f],
			[0x2200, 0x22ff],
			[0x27c0, 0x27ef],
			[0x2980, 0x2aff],
		],
	],
	[
		"arrows",
		[
			[0x2190, 0x21ff],
			[0x27f0, 0x27ff],
			[0x2900, 0x297f],
			[0x2b00, 0x2bff],
		],
	],
	// Enclosed alphanumerics, dingbat numbers (❶), and their supplement
	[
		"enclosed",
		[
			[0x2460, 0x24ff],
			[0x2776, 0x2793],
			[0x1f100, 0x1f1ff],
		],
	],
	// Technical, control pictures, box drawing, blocks, geometric shapes, symbols, dingbats
	[
		"shapes",
		[
			[0x2300, 0x243f],
			[0x2500, 0x27bf],
		],
	],
	// Ideographic description, kanbun, strokes, enclosed and squared CJK (㈱ ㍿)
	[
		"japanese symbols",
		[
			[0x2ff0, 0x2fff],
			[0x3190, 0x319f],
			[0x31c0, 0x31ef],
			[0x3200, 0x33ff],
			[0x1f200, 0x1f2ff],
		],
	],
	// Hiragana, katakana and their extensions, halfwidth katakana
	[
		"kana",
		[
			[0x3040, 0x30ff],
			[0x31f0, 0x31ff],
			[0xff65, 0xff9f],
		],
	],
	["fullwidth", [[0xff00, 0xffef]]],
	// Unified and compatibility ideographs, their extensions
	[
		"kanji",
		[
			[0x3400, 0x4dbf],
			[0x4e00, 0x9fff],
			[0xf900, 0xfaff],
			[0x20000, 0x3ffff],
		],
	],
	// Radicals and Kangxi radicals: the parts kanji are made of, as dictionaries list them
	["radicals", [[0x2e80, 0x2fdf]]],
	// Letterlike symbols (№ ℃), Greek, and the rest
	["other", []],
]

// Every character of Kuronuri, from the unicode-range of its slices (all its fonts have the same),
// by kind, and where they come from
export default defineEventHandler((): { kinds: Kind[]; origins: Origins } => {
	const characters = new Set<number>()
	for (const [, ranges] of css.matchAll(/unicode-range:([^;]+);/g)) {
		for (const range of ranges.split(",")) {
			const [start, end = start] = range.trim().slice(2).split("-")
			for (let c = parseInt(start!, 16); c <= parseInt(end!, 16); c++) {
				// Not control characters, which fonts map to nothing to draw
				if (c >= 0x20 && !(c >= 0x7f && c < 0xa0)) characters.add(c)
			}
		}
	}
	const kinds = KINDS.map(([kind]) => ({ kind, characters: [] as number[] }))
	for (const c of [...characters].sort((a, b) => a - b)) {
		const i = KINDS.findIndex(
			([, ranges], i) =>
				i === KINDS.length - 1 || ranges.some(([start, end]) => start <= c && c <= end),
		)
		kinds[i]!.characters.push(c)
	}
	return {
		kinds: kinds.map(({ kind, characters }) => ({
			kind,
			characters: String.fromCodePoint(...characters),
		})),
		origins,
	}
})
