# kuronuri 黒塗り

[![release][release-src]][release-href]
[![license][license-src]][license-href]

[redaction](https://www.redaction.us), with japanese support, and more

kuronuri (黒塗り, "blacked out") pairs the latin of redaction by mckl with the kana and kanji of [noto serif jp](https://fonts.google.com/noto/specimen/Noto+Serif+JP). like redaction, it comes in pixelated variants: kuronuri 10, 20, 35, 50, 70 and 100, where the number is the size of a pixel in a 1000-unit em.

## web

```sh
npm install kuronuri
```

import the css of the families you use:

```js
import "kuronuri/kuronuri-35.css"
// or, for pages without japanese
import "kuronuri/kuronuri-35-latin.css"
```

```css
body {
	font-family: "Kuronuri 35", serif;
}
```

the fonts are split into woff2 slices, each with a `unicode-range`, the way google fonts serves japanese: browsers only download the slices a page uses. a paragraph of japanese and english takes 16 slices, 230 KB for kuronuri, 112 KB for kuronuri 35. the css of a family is 90 KB gzipped, its latin-only css under 1 KB.

the package is laid out like a [fontsource](https://fontsource.org) one: `kuronuri.css` to `kuronuri-100.css`, their `-latin.css`, `index.css` importing every family, and the fonts in `files/`. with [nuxt fonts](https://fonts.nuxt.com), use the `npm` provider:

```ts
export default defineNuxtConfig({
	modules: ["@nuxt/fonts"],
	fonts: {
		families: [
			{ name: "Kuronuri 35", provider: "npm", providerOptions: { npm: { package: "kuronuri" } } },
		],
	},
})
```

## desktop

download `kuronuri-<version>.zip` from the [releases](https://github.com/lihbr/kuronuri/releases), it has the ttf and woff2 files.

| family       | pixel | woff2  | ttf     |
| ------------ | ----- | ------ | ------- |
| kuronuri     |       | 3.1 MB | 8.0 MB  |
| kuronuri 10  | 10    | 2.3 MB | 16.7 MB |
| kuronuri 20  | 20    | 1.7 MB | 9.6 MB  |
| kuronuri 35  | 35    | 1.3 MB | 6.6 MB  |
| kuronuri 50  | 50    | 1.1 MB | 5.3 MB  |
| kuronuri 70  | 70    | 0.9 MB | 4.4 MB  |
| kuronuri 100 | 100   | 0.6 MB | 3.3 MB  |

## features

- regular, italic and bold, like redaction. japanese stays upright in italic
- the japanese of noto serif jp: kana, 13,736 kanji, punctuation, vertical forms and variation sequences. no cyrillic, greek, vietnamese, korean or bopomofo, they would not match redaction
- fullwidth letters, digits, signs and punctuation drawn from redaction's, for japanese text, also in vertical text: ２０２６年, ＮＨＫ, 本当！？, １，０００, and 〒, and small forms: ﹖﹗﹙﹚
- roman numerals, and enclosed numbers, letters and words drawn from redaction's: Ⅻ ⅻ ① ㊿ ❶ ⓵ ㉈ Ⓐ 🄰 🅰 🆒 🅪 ⑴ ⒈, latin squares: ㎏ ㎑ ㍱, and dates and hours: ㋀ ㏠ ㍘
- fractions and figures: ⅓ ⅝ ⅒ ⁴ ₂ ª º №, as features too: `font-variant-numeric: diagonal-fractions` (frac) or `ordinal` (ordn), `font-variant-position: super` (sups) or `sub` (subs), and `numr`, `dnom`, `sinf`
- ordinals: `font-variant-numeric: ordinal` raises the suffixes of 1st 2nd 3rd 4th, 1er 1re 2e 2nde and 1a 2o 3as, and turns `No. 5` into № 5. a suffix followed by a letter or digit stays as typed: 3am, 2e3
- ʁ, for french in phonetic notation: \\libʁ\\, < > ± ÷ ‰, ‼ ⁇ ⁈ ⁉, ₩ ₫ ℃ ℉ ℡ ℻
- tabular figures, also in japanese text: `font-variant-numeric: tabular-nums`
- arrows: ← ↑ → ↓ ↔ ↕ ↖ ↗ ↘ ↙ ⇐ ⇑ ⇒ ⇓ ⇔ ⇕ ⇖ ⇗ ⇘ ⇙ ⇄ ⇅ ↹ ⇌ ⤴ ⇨ ⮕. `->` `<-` `<->` `-^` `^-` `=>` `<=>` `=^` turn into arrows, to type them as is: `font-variant-ligatures: no-contextual`
- alt arrows, with smaller heads: `font-feature-settings: "ss01"`
- maths: ≤ ≥ ≠ ≡ ≈ ≅ ≪ ≲ ∓ ∈ ∉ ∋ ⊂ ⊆ ∩ ∪ ∧ ∨ ∀ ∃ ∅ ∞ ∝ √ ∠ ⊥ ∥ ⊕ ⊗ ∴ ⋯ ∆ ∇, without the greek and integrals (∑ ∏ ∂ ∫), which stay noto's

## how it's made

- **kuronuri:** noto serif jp 500 is merged into redaction regular, and 800 into bold, the weights with the closest stems.
- **pixelated variants:** the latin is mckl's redaction 10 to 100. the japanese is pixelated on the same grid by [`src/pixel.py`](./src/pixel.py): a cell becomes a pixel when the outline covers half of it, then thin strokes that fall between cells are put back. advances, vertical origins and kerning are snapped to the grid too.
- **drawn glyphs:** [`src/glyphs`](./src/glyphs) draws what redaction lacks from redaction's own glyphs, into redaction, before the merge ([`src/draw.py`](./src/draw.py)). smooth drawings are pixelated for the numbered variants, glyphs made of redaction's keep mckl's pixels.
  - [`arrows.py`](./src/glyphs/arrows.py): the stroke and axis of redaction's minus, double arrows as far apart as its equals sign, and the slant of its plus. pairs (⇄), harpoons (⇌), block (⇨) and curved (⤴) arrows are made of the same strokes and heads.
  - [`letters.py`](./src/glyphs/letters.py): ʁ is redaction's `R` upside down, shrunk to the x-height, emboldened first so its stems match the lowercase.
  - [`signs.py`](./src/glyphs/signs.py): `<` `>` span the plus with the stroke of the minus, `±` and `÷` are made of the plus, minus and period, `‰` of the percent sign and its ring again.
  - [`maths.py`](./src/glyphs/maths.py): line work in the square of the plus, on the axis of the minus: bars as thick as the minus and the stem of the plus, other strokes as those of `<`. relations stack `<`, the bars of the equals sign and a tilde of the same strokes, sets and logic turn round, the dots are its period and ⋯ its ellipsis, ∀ ∃ ∆ ∇ are as tall as capitals.
  - [`symbols.py`](./src/glyphs/symbols.py): ₩ is its `W` crossed by the bars of its equals sign, ₫ its `đ` over a rule, ℃ ℉ its ° and letter as typed, ℡ ℻ its capitals as small caps, as tall as its z, made heavier as its bold is of its regular so their stems match its n, and pixelated where in a cell they fall best, as the superscripts.
  - [`punctuation.py`](./src/glyphs/punctuation.py): ‼ ⁇ ⁈ ⁉ are redaction's ! and ? set with its kerning, as wide as typed.
  - [`figures.py`](./src/glyphs/figures.py): superscripts are its digits shrunk to the size of its ¹, made heavier first as its bold is of its regular (past bold for bold), so they keep their hairlines and carving, and pixelated where in a cell their counters come out as drawn (35 to 70), subscripts and denominators the same lower, fractions are laid out as its ½. its `frac`, `sups` and `numr` do every figure, `subs`, `sinf` and `dnom` are added.
  - [`ordinals.py`](./src/glyphs/ordinals.py): ª º and the letters of ordinals (and of ℀ ℅) are its own shrunk as the superscripts, their x-height at the top of its ¹, their stems as its ¹'s: its bold thinned for regular; for italic and bold, made heavier as its bold is of its regular where their outlines match, else grown across only, their tips kept pointed, their tapering strokes grown as much as they are thick, and their carving cut again (bold's s, which runs into itself blended, by as much ink as blending would add), as big as emboldened, spaced as their own letters shrunk, as its ¹ ² ³ are of 1 2 3. pixelated where in a cell their counters come out (35 to 70), and their carving (10, 20), no two alike. № is its N and º, and `ordn` is added.
  - [`fullwidth.py`](./src/glyphs/fullwidth.py): redaction's glyphs centred in the em, and 〒 from its T. ， ． ： ＝ － sit where noto's do, and turn in vertical text as noto's do, through its `vert`; other punctuation that turns stays noto's.
  - [`small.py`](./src/glyphs/small.py): small forms are redaction's glyphs seven tenths as big, centred in the em.
  - [`japanese.py`](./src/glyphs/japanese.py): ㋀ ㏠ ㍘ are redaction's figures and noto's kanji (月 日 点), condensed side by side in the em as noto's are, emboldened sideways so their stems stay.
  - [`numerals.py`](./src/glyphs/numerals.py): roman numerals are redaction's letters set with its kerning, as wide as typed.
  - [`enclosed.py`](./src/glyphs/enclosed.py): rings, discs and squares as thin as redaction's minus, where noto's ring is, around its glyphs shrunk like ʁ, the same size across a family, and latin squares (㎏) without a square. content is made heavier as its bold is of its regular, till the stems of its n, i or 1 are those of its n at the size it is drawn (smaller than ⑳, as heavy as it), no further than its bold is of its regular past its own style (1.2 times in bold), shrunk back as tall as its own, so it keeps its hairlines and carving; a glyph whose outlines do not match its regular's and bold's (italic's lowercase, w q) is drawn as before, alone, grown sideways, a quarter as much up and down, as much as its own n, i or 1 takes to be as heavy as blended, its serifs and hairlines nearly as thin, its dots scaled, redaction's carving cut back in where it moves out cleanly (italic b c g i j l p q t); those that do not carve cleanly (the rest of italic's lowercase, w q r; bold s q w) emboldened all round and uncarved, as before; glyphs as near as typed where their ink comes nearest, any way, figures as far apart as they look on average; as big in every style as typed in its bold, upright, or smaller where a style's own is wider (italic's m), shrunk only past 0.9 of the room inside, and a glyph alone where nearer its enclosure than ¾ of its stroke: its figures nearer, narrowed, then shrunk, centred off it (⓾). pixelated apart from their enclosure where in a cell they fall best (10 to 70), blended less where their pixels would lose a piece or a counter and stop losing it (35 to 70), words with it; on 70, lowercase is blended and placed as like its smooth drawing as its pixels come, and italic's e h f and bold's z are as before, which read as other letters blended, as are a few others on 35 to 70 (㉊ ⑪ ➌ ㏇ ➐ 🆀 …). on 100, content is its bold shrunk in regular, emboldened in italic and bold. ⑴ ⒈ are redaction's glyphs as typed.
- **web:** [`src/web.py`](./src/web.py) slices the fonts along google's character groups ([`src/data/google-jp-slices.json`](./src/data/google-jp-slices.json)). the slices leave out `aalt`, `nlck`, `hist` and `dlig`, which pull in hundreds of rarely used glyphs. their urls end in `?no-inline`, so vite doesn't inline the smallest ones into the css.

## development

```sh
# needs node, pnpm, and python 3.14
pnpm install
pnpm venv                                       # python dependencies in .venv
pnpm sources                                    # downloads redaction and noto serif jp
pnpm review                                     # draws the glyphs of src/glyphs for localhost:3000/review (pnpm dev): seconds
pnpm review --approve                           # what changed since approved is framed, before and after, this approves it
pnpm score                                      # scores drawn glyphs against redaction's own (¹ ² ³, ¼ ⅗, ™), and superscript letters against approved, to temp/score: seconds
pnpm build                                      # dist/ (the npm package is dist/web): ~15 min, ~4 once cached
pnpm build --variants base,35 --styles Regular  # only a few fonts
pnpm build:web                                  # only redoes dist/web
pnpm test                                       # checks every font and slice
pnpm dev                                        # kuronuri.lihbr.com on localhost:3000, from dist/web, and /review
pnpm lint                                       # or pnpm format
pnpm release                                    # bumps the version and pushes a tag, ci publishes to npm and github
```

## credits

- [redaction](https://www.redaction.us), © 2019 mckl inc., by jeremy mickel and forest young
- [noto serif jp](https://github.com/notofonts/noto-cjk), © 2017-2024 adobe, © 2012 google inc.

fonts are [ofl](./OFL.txt), code is [mit](./LICENSE)

<!-- Badges -->

[release-src]: https://img.shields.io/github/v/release/lihbr/kuronuri?style=flat-square&colorA=000000&colorB=e84311
[release-href]: https://github.com/lihbr/kuronuri/releases
[license-src]: https://img.shields.io/badge/license-OFL--1.1-000000?style=flat-square&labelColor=000000&color=e84311
[license-href]: https://github.com/lihbr/kuronuri/blob/master/OFL.txt
