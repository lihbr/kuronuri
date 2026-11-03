export const STYLES = {
	Regular: { fontWeight: 400, fontStyle: "normal" },
	Italic: { fontWeight: 400, fontStyle: "italic" },
	Bold: { fontWeight: 700, fontStyle: "normal" },
} as const
export type Style = keyof typeof STYLES

export const VARIANTS = ["0", "10", "20", "35", "50", "70", "100"]

export const FONTS = ["font-0", "font-10", "font-20", "font-35", "font-50", "font-70", "font-100"]

export const familyOf = (variant: string): string => `Kuronuri ${variant}`

/**
 * A glyph in a GlyphGrid, its advance shaded: on the review page, in flamingo when new and in navy
 * when changed; on the glyphs page, in flamingo when it is Redaction's as it is, in navy when drawn
 * from them (src/glyphs); in grey otherwise (Noto Serif JP's, unchanged)
 */
export type GridGlyph = {
	character: string
	caption: string
	title?: string
	mark?: "new" | "changed"
	origin?: "redaction" | "drawn"
}

export const codePoint = (character: string): string =>
	character.codePointAt(0)!.toString(16).toUpperCase().padStart(4, "0")
