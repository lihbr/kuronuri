<script setup lang="ts">
// Every glyph of Kuronuri, by kind, in one family and style at a time
useHead({ title: "Glyphs" })

const { data } = await useFetch("/api/glyphs")
const kinds = computed(() => data.value?.kinds)
// Where each glyph comes from, in the title of its cell and the shade of its advance
const origins = computed(() => ({
	redaction: new Set(data.value?.origins.redaction),
	drawn: new Set(data.value?.origins.drawn),
}))
const origin = (character: string) =>
	origins.value.redaction.has(character)
		? "Redaction"
		: origins.value.drawn.has(character)
			? "drawn from Redaction"
			: "Noto Serif JP"

// Text to start with, per kind
const SAMPLES: Record<string, string> = {
	latin: "The quick brown fox jumps over the lazy dog  Ça va, l’œuvre ? \\libʁ\\",
	punctuation: "「こんにちは、世界。」  “Hello,” she said — … ‘world’‼",
	maths: "±1 ÷2 <> ≤ ≠ ∞ √ ∑  ⅠⅡⅢⅫ ⅰⅱⅲ  5% 5‰",
	arrows: "a → b ⇒ c ↔ d ⇔ e  ↖↗↘↙ ⇖⇗⇘⇙",
	enclosed: "①②③ ❶❷❸ ⓵⓶⓷ ⒶⒷⒸ 🅰🅱🅲 🆒🆗 ⑴⑵ ⒈⒉",
	shapes: "■□▲△●○◆◇★☆ ♪♫ ✓✗ ┌─┐",
	"japanese symbols": "〒 ㈱ ㍿ ㊗ ㋿ 🈁",
	kana: "いろはにほへと ちりぬるを  イロハニホヘト チリヌルヲ  ｶﾀｶﾅ",
	fullwidth: "２０２６年１０月２２日  ＮＨＫとＪＲ  ＡＢＣ ABC  本当！？",
	kanji: "黒塗り 東京都 大阪府 京都府 漢字 永",
	radicals: "⼝ 口  ⼤ 大  ⽥ 田  ⼈ 人  ⼥ 女",
	other: "№ ℃ ™ Ω  αβγ",
}

const settings = useStoredSettings("kuronuri:glyphs", {
	size: 48,
	style: "Regular" as Style,
	variant: "0",
	kind: "latin",
	texts: {} as Record<string, string>, // per kind, the sample until edited
	ss01: false,
	dark: false,
})
const kind = computed(
	() => kinds.value?.find((kind) => kind.kind === settings.kind) ?? kinds.value?.[0],
)
const font = computed(() => ({
	fontFamily: `"${familyOf(settings.variant)}", Kuronuri, serif`,
	...STYLES[settings.style],
	fontFeatureSettings: settings.ss01 ? '"ss01"' : undefined,
}))
const glyphs = computed(() =>
	[...(kind.value?.characters ?? "")].map((character) => ({
		character,
		caption: codePoint(character),
		title: `U+${codePoint(character)}, ${origin(character)}`,
		origin: origins.value.redaction.has(character)
			? ("redaction" as const)
			: origins.value.drawn.has(character)
				? ("drawn" as const)
				: undefined,
	})),
)
</script>

<template>
	<GlyphLayout :size="settings.size" :dark="settings.dark">
		<template #header>
			<h1 class="font-bold">Kuronuri glyphs</h1>
			<GlyphRange v-model="settings.size" />
			<div class="flex flex-wrap gap-1">
				<GlyphToggle
					v-for="(style, name) in STYLES"
					:key="name"
					v-model="settings.style"
					type="radio"
					name="style"
					:value="name"
					:style="style"
				>
					{{ name }}
				</GlyphToggle>
			</div>
			<div class="flex flex-wrap gap-1">
				<GlyphToggle
					v-for="variant in VARIANTS"
					:key="variant"
					v-model="settings.variant"
					type="radio"
					name="variant"
					:value="variant"
					:style="{ fontFamily: `'${familyOf(variant)}'` }"
				>
					{{ variant }}
				</GlyphToggle>
			</div>
			<div class="flex flex-wrap gap-1">
				<GlyphToggle v-model="settings.ss01">alt arrows (ss01)</GlyphToggle>
				<GlyphToggle v-model="settings.dark">dark</GlyphToggle>
			</div>
			<nav class="flex flex-wrap gap-1 w-full">
				<GlyphToggle
					v-for="{ kind: name, characters } in kinds"
					:key="name"
					:model-value="kind?.kind"
					type="radio"
					name="kind"
					:value="name"
					class="capitalize"
					@update:model-value="settings.kind = name"
				>
					{{ name }} <span class="tabular-nums">{{ [...characters].length }}</span>
				</GlyphToggle>
			</nav>
		</template>

		<template v-if="kind">
			<GlyphText
				:model-value="settings.texts[kind.kind] ?? SAMPLES[kind.kind] ?? ''"
				class="my-4"
				:style="font"
				@update:model-value="settings.texts[kind.kind] = $event ?? ''"
			/>
			<p class="mb-4 opacity-60">
				Glyphs shaded in <span class="bg-flamingo/16 px-1">flamingo</span> are Redaction’s as they
				are, in <span class="bg-navy/16 px-1">navy</span> drawn from them, in
				<span class="bg-current/8 px-1">grey</span> Noto Serif JP’s, pixelated for the numbered
				variants.
			</p>
			<GlyphGrid :glyphs="glyphs" :font="font" :size="settings.size" />
		</template>
	</GlyphLayout>
</template>
