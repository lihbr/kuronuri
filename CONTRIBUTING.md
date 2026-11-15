# contributing

kuronuri is maintained by [lihbr](https://lihbr.com). ask for help by [opening an issue](https://github.com/lihbr/kuronuri/issues/new), or request a review by opening a pull request

## setup

- node, and pnpm
- python 3.14

## architecture

glyphs come from four tiers:

1. **redaction:** mckl's glyphs and pixel fonts, as they are, downloaded into `.cache/sources/` by `pnpm venv`
2. **noto serif jp:** the kana and kanji, 500 merged into regular and italic and 800 into bold, the weights whose stems match. on 50 to 100, where pixels make them darker, the outlines of the kanji and kana in regular and italic are 400, in the spacing of 500; bold's stay 800. [`src/pixel.py`](./src/pixel.py) pixelates them for the pixelated variants, 10 to 100
3. **drawn by code:** what redaction lacks, drawn from its glyphs in [`src/glyphs`](./src/glyphs), a module per group, each explained in its docstring. components keep mckl's pixels, the rest are pixelated where in a cell they fall best
4. **drawn by hand:** where code loses mckl's carving or pixels read as another glyph, in [`src/glyphs/drawn`](./src/glyphs/drawn): outlines in a ufo per style, in redaction's units, and cells in `cells.txt`, `arrows.txt`, `maths.txt`, `greek.txt` and `figures.txt`, and the kanji and kana of regular and italic a phase turns into another character or breaks, on 100 (and 上 on 50), in `japanese.txt`, `#` ink and `.` air, top row first. `pnpm unit` checks the fonts match them fraction ⅐, 

the scripts:

- [`src/draw.py`](./src/draw.py) draws tiers 3 and 4 into redaction, into `.cache/drawn`
- [`src/review.py`](./src/review.py) draws, then writes `.tmp/review` for `/review` (`pnpm dev`): changes since approved, before and after, text set as the build sets it, merged with noto serif jp (a few minutes once `src/` changes, cached), next to the same text before, and the pixelated japanese in text next to the latin. `--approve` makes them the reference, in `.cache/approved`. `--before <dir>` copies built fonts to compare with, say a checkout's `dist/ttf`, kept with where and when they came from until `--before` is given again: text not approved yet and the japanese are compared with them. glyphs in `.tmp/watch.txt` get their own tab, its format is in `review.py`
- [`src/score.py`](./src/score.py) scores drawn glyphs against mckl's (¹ ² ³, ¼ ⅗, ™), and superscript letters against approved, into `.tmp/score`
- [`src/build.py`](./src/build.py) merges noto serif jp, pixelates it, and writes `dist/ttf` and `dist/woff2`. [`src/web.py`](./src/web.py) slices them into `dist/web`, the npm package
- [`test/check.py`](./test/check.py) checks every font and slice in `dist/`. `--pictures` keeps the cells of the greek letters as they are now (`test/greek-cells.json`), once looked at: a cell lost or gained fails
- [`site`](./site) is [kuronuri.lihbr.com](https://kuronuri.lihbr.com), a nuxt app using `dist/web` through the workspace

## develop

```sh
# clone and prepare the project
git clone git@github.com:lihbr/kuronuri.git
cd kuronuri
pnpm install

# install python dependencies and download source fonts
pnpm venv

# draw the glyphs of src/glyphs for /review
pnpm review
# compare text and the japanese with fonts built before a change
pnpm review --before ../kuronuri/dist/ttf
# approve changes
pnpm review --approve

# build dist/, ~15 min, ~4 once cached
pnpm build
# build only a few fonts
pnpm build --variants 0,35 --styles Regular
# redo only dist/web
pnpm build --web-only

# start kuronuri.lihbr.com on localhost:3000, with /review
pnpm dev

# lint changes
pnpm lint
# format changes
pnpm format
# run unit tests
pnpm unit
```

## publish

```sh
# bump the version and push a tag, ci publishes to npm and github
pnpm release
```
