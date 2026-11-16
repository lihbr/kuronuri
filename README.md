# kuronuri 黒塗り

![kuronuri specimen: 黒塗り set large, going from smooth to pixelated; the seven families, 0 to 100, in regular, italic, and bold; hiragana, katakana, kanji, latin letters, figures, and signs; and the pangram “Caviardez vos aveux, juge kafkaïen : que le noir masque whisky, complots et biffures.”](./.github/specimen--light.png#gh-light-mode-only)
![kuronuri specimen: 黒塗り set large, going from smooth to pixelated; the seven families, 0 to 100, in regular, italic, and bold; hiragana, katakana, kanji, latin letters, figures, and signs; and the pangram “Caviardez vos aveux, juge kafkaïen : que le noir masque whisky, complots et biffures.”](./.github/specimen--dark.png#gh-dark-mode-only)

> 日本語の情報は[こちら](https://kuronuri.lihbr.com)をご覧ください。

[kuronuri](https://kuronuri.lihbr.com) (黒塗り, "blacked out") is a font family created by [lihbr](https://lihbr.com). it extends [redaction](https://www.redaction.us), by [mckl](https://www.mckltype.com), and draws kana and kanji using [noto serif jp](https://fonts.google.com/noto/specimen/Noto+Serif+JP) as a base. like redaction, it comes in seven families, from smooth to pixelated: kuronuri 0, 10, 20, 35, 50, 70, and 100.

kuronuri also comes with new glyphs drawn in redaction's style, including fractions (⅐), arrows (→), enclosed characters (🆞), and more. font-feature settings were also added for tabular figures `tnum`, fractions `frac`, superscripts `sups`, subscripts `subs`, ordinals `ordn`, full widths `fwid`, half widths `hwid`, contextual alternates `calt`, and alternate arrows `ss01`.

## install インストール

### desktop デスクトップ

download the [latest release](https://github.com/lihbr/kuronuri/releases/latest) and install the fonts on your system.<br>
7 families, regular, italic, and bold, as ttf and woff2.

### web ウェブ

```sh
npm install @lihbr/kuronuri
```

```css
/* css, -0, -10, -20, -35, -50, -70, -100 */
@import "@lihbr/kuronuri/kuronuri-35.css";

/* latin only */
@import "@lihbr/kuronuri/kuronuri-35-latin.css";

body {
	font-family: "kuronuri 35", serif;
}
```

fonts are split into woff2 slices so browsers only download what a page uses.<br>
package is laid out like a [fontsource](https://fontsource.org) one.

## miscellaneous その他

[contributing.md](./CONTRIBUTING.md)

[redaction](https://www.redaction.us), © 2019 mckl inc., by jeremy mickel and forest young<br>
[noto serif jp](https://github.com/notofonts/noto-cjk), © 2017-2024 adobe, © 2012 google inc.

fonts are [ofl](./OFL.txt)<br>
code is [mit](./LICENSE)
