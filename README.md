# kuronuri 黒塗り

[![npm version][npm-version-src]][npm-version-href]
[![npm downloads][npm-downloads-src]][npm-downloads-href]
[![license][license-src]][license-href]

[kuronuri](https://kuronuri.lihbr.com) (黒塗り, "blacked out") is a font family created by [lihbr](https://lihbr.com). it extends [redaction](https://www.redaction.us), by [mckl](https://www.mckltype.com), and draws kanas and kanjis using [noto serif jp](https://fonts.google.com/noto/specimen/Noto+Serif+JP) as a base. like redaction, it comes in seven families, from smooth to pixelated: kuronuri 0, 10, 20, 35, 50, 70, and 100.

kuronuri also comes with new glyphs drawn in redaction's style, among them, fractions ⅐, arrows ⇒, enclosed 🆞, and more. font-feature settings were also added for tabular figures, fractions, superscripts, subscripts, ordinals, contextual alternates, and alternate arrows.

## install インストール

### desktop デスクトップ

download the [latest release](https://github.com/lihbr/kuronuri/releases/latest) and install the fonts on your system.

### web ウェブ

```sh
npm install kuronuri
```

```css
/* css, -0, -10, -20, -35, -50, -70, -100 */
@import "kuronuri/kuronuri-35.css";

/* latin only */
@import "kuronuri/kuronuri-35-latin.css";
```

the fonts are split into woff2 slices, and the package is laid out like a [fontsource](https://fontsource.org) one.

## contributing コントリビューション

see [contributing.md](./CONTRIBUTING.md)

## credits クレジット

[redaction](https://www.redaction.us), © 2019 mckl inc., by jeremy mickel and forest young
[noto serif jp](https://github.com/notofonts/noto-cjk), © 2017-2024 adobe, © 2012 google inc.

## licenses ライセンス

fonts are [ofl](./OFL.txt)
code is [mit](./LICENSE)

<!-- Badges -->

[npm-version-src]: https://img.shields.io/npm/v/kuronuri?style=flat-square&colorA=000000&colorB=e84311
[npm-version-href]: https://npmjs.com/package/kuronuri
[npm-downloads-src]: https://img.shields.io/npm/dm/kuronuri?style=flat-square&colorA=000000&colorB=e84311
[npm-downloads-href]: https://npmjs.com/package/kuronuri
[license-src]: https://img.shields.io/badge/license-OFL--1.1-000000?style=flat-square&labelColor=000000&color=e84311
[license-href]: https://github.com/lihbr/kuronuri/blob/master/OFL.txt
