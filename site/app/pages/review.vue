<script setup lang="ts">
// The glyphs drawn in src/glyphs, in development only (nuxt.config.ts), from what `pnpm review`
// writes to .tmp/review: the drawn fonts, with the built ones behind them for everything else, and
// what changed since they were approved. The noto tab sets text in the Japanese src/pixel.py makes
// of Noto Serif JP, cut down to the characters review.py lists, next to the Latin: before (the built
// fonts review.py --before names), now, and at grade 0

type Font = {
	name: string
	grid: number | null
	style: string
	family: string
	weight: number
	italic: boolean
	characters: Record<string, string>
	changed: string[]
	watch: string[] // in .tmp/watch.txt, to look at closely
	new: string[]
	before: "approved" | "built" | null // what its text is compared with: see review.py
	// of its Japanese review font: the characters changed since the reference, how many it keeps, and
	// whether the reference has this font
	noto: { changed: string; count: number; before: boolean }
	revisions: Record<string, string> // module, "changed", "watch" or "noto": hash of its glyphs
}
type Review = {
	version: number
	fonts: Font[]
	modules: {
		name: string
		about: string
		samples: string[]
		features: string[] // on in its text
		glyphs: string[]
		width: number
	}[]
	watch: string // text to set the watched glyphs in
	features: string[] // to turn on and off in the text of a tab, each module's on at first
	// the built fonts text is compared with until approved, copied from source when taken
	reference: { source: string; built: string; taken: string; hash: string } | null
	noto: {
		text: string[] // lines of the text of the noto tab
		vertical: string // set vertically
		kept: string // the characters the Japanese review fonts keep...
		characters: string // ...of all those of Noto Serif JP the fonts have
		// the built fonts before: the same snapshot as reference
		reference: { from: string; at: string; hash: string } | null
	}
}

const PUA = 0xf0000 // review fonts map glyphs without a code point (alternates) from here

const review = ref<Review>()
const missing = ref(false)

// Reloads when `pnpm review` runs again
let poll: ReturnType<typeof setInterval> | undefined
async function load() {
	try {
		const fresh = await $fetch<Review>(`/_review/review.json?t=${Date.now()}`)
		if (fresh.version !== review.value?.version) review.value = fresh
		missing.value = false
	} catch {
		missing.value = true
	}
}

const settings = useStoredSettings("kuronuri:review", {
	size: 48,
	tab: "",
	texts: {} as Record<string, string>, // per tab, the samples until edited
	hidden: [] as string[],
	reviewed: {} as Record<string, string>, // "module font": the revision reviewed
	ss01: false,
	features: {} as Record<string, string[]>, // per tab, those on until changed
	ja: false, // the text in Japanese: its language systems (latn JAN, kana, hani)
	kern: true,
	before: true, // the text in the fonts before too
	dark: false,
})
onMounted(() => {
	load()
	poll = setInterval(load, 1500)
})
onBeforeUnmount(() => clearInterval(poll))

const variant = (font: Font) => String(font.grid ?? 0)
// Style and variant toggles, of the fonts there are, each set in its own font
const styles = computed(
	() => [...new Set(review.value?.fonts.map((font) => font.style))] as Style[],
)
const variants = computed(() => [...new Set(review.value?.fonts.map(variant))])
function toggle(key: string) {
	const i = settings.hidden.indexOf(key)
	if (i === -1) settings.hidden.push(key)
	else settings.hidden.splice(i, 1)
}
const fonts = computed(
	() =>
		review.value?.fonts.filter(
			(font) => !settings.hidden.includes(font.style) && !settings.hidden.includes(variant(font)),
		) ?? [],
)
// Fonts with glyphs to compare, changed or watched
type Compared = "changed" | "watch"
const compared = (key: Compared) => fonts.value.filter((font) => font[key].length)
const count = (key: "changed" | "new" | "watch") =>
	review.value?.fonts.reduce((sum, font) => sum + font[key].length, 0) ?? 0
const tabs = computed(() => [
	...(count("watch") ? ["watch"] : []),
	...(count("changed") ? ["changed"] : []),
	...(review.value?.noto ? ["noto"] : []),
	...(review.value?.modules.map((module) => module.name) ?? []),
])
const tab = computed(() => (tabs.value.includes(settings.tab) ? settings.tab : tabs.value[0]))
const module = computed(() => review.value?.modules.find((module) => module.name === tab.value))

// Reviewed until its glyphs change, as GitHub's viewed files
const isReviewed = (module: string, font: Font) =>
	settings.reviewed[`${module} ${font.name}`] === font.revisions[module]
async function markReviewed(module: string, font: Font, event: Event) {
	const input = event.target as HTMLInputElement
	if (!input.checked) {
		delete settings.reviewed[`${module} ${font.name}`]
		return
	}
	settings.reviewed[`${module} ${font.name}`] = font.revisions[module]!
	// Once collapsed, scrolled back to it if it was scrolled past, to where its title sticks: the
	// next section starts below
	await nextTick()
	const section = input.closest("section")!
	const top =
		section.getBoundingClientRect().top -
		parseFloat(getComputedStyle(section.firstElementChild!).top)
	if (top < 0) window.scrollBy(0, top)
}
const progress = (module: string) => {
	const of = module === "changed" || module === "watch" ? compared(module) : fonts.value
	return `${of.filter((font) => isReviewed(module, font)).length}/${of.length}`
}

// The drawn fonts, for glyphs, now and approved; and, for text, merged with Noto Serif JP as built,
// now and before (review.py)
type Kind = "" | "approved" | "text" | "before"
const family = (font: Font, kind: Kind = "") => `review ${font.name}${kind && ` ${kind}`}`
const face = (font: Font, kind: Kind = "") => `@font-face {
	font-family: "${family(font, kind)}";
	src: url("/_review/fonts/${kind && `${kind}/`}${font.name}.ttf?v=${review.value?.version}");
	font-weight: ${font.weight};
	font-style: ${font.italic ? "italic" : "normal"};
}`
useHead({
	title: "Review",
	style: [
		{
			key: "review-fonts",
			innerHTML: computed(() =>
				(review.value?.fonts ?? [])
					.flatMap((font) => [
						face(font),
						face(font, "approved"),
						face(font, "text"),
						...(font.before ? [face(font, "before")] : []),
					])
					.join("\n"),
			),
		},
	],
})
const set = (font: Font, kind: Kind = "") => ({
	fontFamily: `"${family(font, kind)}", "${font.family}", serif`,
	fontWeight: font.weight,
	fontStyle: font.italic ? "italic" : "normal",
})

const caption = (font: Font, name: string) =>
	font.characters[name]!.codePointAt(0)! < PUA
		? codePoint(font.characters[name]!)
		: name.split(".")[1]!
const glyphs = (font: Font, names: string[]): GridGlyph[] =>
	names
		.filter((name) => name in font.characters)
		.map((name) => ({
			character: font.characters[name]!,
			caption: caption(font, name),
			title: name,
			mark: font.changed.includes(name) ? "changed" : font.new.includes(name) ? "new" : undefined,
		}))
const label = (font: Font) => `Kuronuri ${variant(font)} ${font.style}`

// The noto tab: its Japanese review fonts, now and before, after the drawn font for the Latin
type Japanese = "now" | "before"
const jpFamily = (font: Font, kind: Japanese) => `review jp ${kind} ${font.name}`
const jpFace = (font: Font, kind: Japanese) => `@font-face {
	font-family: "${jpFamily(font, kind)}";
	src: url("/_review/fonts/japanese/${kind === "before" ? "before/" : ""}${font.name}.woff2?v=${review.value?.version}");
	font-weight: ${font.weight};
	font-style: ${font.italic ? "italic" : "normal"};
}`
useHead({
	style: [
		{
			key: "review-japanese",
			innerHTML: computed(() =>
				(review.value?.fonts ?? [])
					.flatMap((font) => [
						jpFace(font, "now"),
						...(font.noto?.before ? [jpFace(font, "before")] : []),
					])
					.join("\n"),
			),
		},
	],
})
// Others than those it keeps fall back to the built fonts, the same in every row
const jpSet = (font: Font, kind: Japanese) => ({
	fontFamily: `"${family(font)}", "${jpFamily(font, kind)}", "${font.family}", serif`,
	fontWeight: font.weight,
	fontStyle: font.italic ? "italic" : "normal",
})
// Grade 0 of its style, for reference: its review fonts, or the built ones
const zero = (font: Font) => {
	const base = review.value?.fonts.find((f) => f.grid === null && f.style === font.style)
	return base
		? jpSet(base, "now")
		: { ...jpSet(font, "now"), fontFamily: `"${familyOf("0")}", serif` }
}
const japaneseText = computed(() => settings.texts.noto ?? review.value?.noto.text.join("\n") ?? "")
const verticalText = computed(() => settings.texts.vertical ?? review.value?.noto.vertical ?? "")
// Characters of the text set in neither Japanese review font, the same before and now
const notCompared = computed(() => {
	const kept = new Set(review.value?.noto.kept)
	const noto = new Set(review.value?.noto.characters)
	return [...new Set(japaneseText.value + verticalText.value)].filter(
		(c) => noto.has(c) && !kept.has(c),
	)
})
// The rows of the noto tab, top to bottom
const jpRows = (font: Font) => [
	{ key: "0", label: "grade 0", style: zero(font) },
	...(font.noto.before
		? [
				{
					key: "before",
					label: "before",
					style: { ...jpSet(font, "before"), color: "var(--color-flamingo)" },
				},
			]
		: []),
	{ key: "now", label: "now", style: jpSet(font, "now") },
]

// Features on in the text of the tab: its module's, until toggled
const on = computed(() => settings.features[tab.value ?? ""] ?? module.value?.features ?? [])
function toggleFeature(tag: string) {
	const tags = on.value.includes(tag) ? on.value.filter((t) => t !== tag) : [...on.value, tag]
	settings.features[tab.value ?? ""] = tags
}
const features = computed(() =>
	[
		...on.value.map((tag) => `"${tag}"`),
		...(settings.ss01 ? ['"ss01"'] : []),
		...(settings.kern ? [] : ['"kern" 0']),
	].join(", "),
)
const lang = computed(() => (settings.ja ? "ja" : "en"))
// Text, as it is set now and before, with the features on
const text = (font: Font, kind: "text" | "before" = "text") => [
	set(font, kind),
	{
		fontFeatureSettings: features.value || "normal",
		fontKerning: settings.kern ? "normal" : "none",
	},
]
const before = (font: Font) =>
	font.before === "approved"
		? "before: approved"
		: `before: built ${review.value?.reference?.built}, ${review.value?.reference?.source.split("/").slice(-3).join("/")}, copied ${review.value?.reference?.taken}, ${review.value?.reference?.hash.slice(0, 8)}`
</script>

<template>
	<GlyphLayout :size="settings.size" :dark="settings.dark">
		<template #header>
			<h1 class="font-bold">Kuronuri review</h1>
			<GlyphRange v-model="settings.size" :min="10" />
			<div class="flex flex-wrap gap-1">
				<GlyphToggle
					v-for="style in styles"
					:key="style"
					:model-value="!settings.hidden.includes(style)"
					:style="STYLES[style]"
					@update:model-value="toggle(style)"
				>
					{{ style }}
				</GlyphToggle>
				<GlyphToggle
					v-for="key in variants"
					:key="key"
					:model-value="!settings.hidden.includes(key)"
					:style="{ fontFamily: `'${familyOf(key)}'` }"
					@update:model-value="toggle(key)"
				>
					{{ key }}
				</GlyphToggle>
			</div>
			<div class="flex flex-wrap gap-1">
				<GlyphToggle v-model="settings.ss01">alt arrows (ss01)</GlyphToggle>
				<GlyphToggle v-model="settings.ja">japanese (lang=ja)</GlyphToggle>
				<GlyphToggle v-model="settings.kern">kern</GlyphToggle>
				<GlyphToggle v-model="settings.before">text before</GlyphToggle>
				<GlyphToggle v-model="settings.dark">dark</GlyphToggle>
			</div>
			<div v-if="module || tab === 'watch'" class="flex flex-wrap gap-1">
				<GlyphToggle
					v-for="tag in review?.features"
					:key="tag"
					:model-value="on.includes(tag)"
					@update:model-value="toggleFeature(tag)"
				>
					{{ tag }}
				</GlyphToggle>
			</div>
			<span class="opacity-60">
				{{ count("changed") }} changed, {{ count("new") }} new since approved
			</span>
			<nav class="flex flex-wrap gap-1 w-full">
				<GlyphToggle
					v-for="name in tabs"
					:key="name"
					:model-value="tab"
					type="radio"
					name="tab"
					:value="name"
					class="capitalize"
					@update:model-value="settings.tab = name"
				>
					{{ name }}
					<span class="tabular-nums">{{ progress(name) }}</span>
				</GlyphToggle>
			</nav>
		</template>

		<template v-if="review && (tab === 'changed' || tab === 'watch')">
			<p class="my-4 opacity-60">
				approved in red, now, then over each other<template v-if="tab === 'watch'"
					>: the glyphs of .tmp/watch.txt, changed or not, and text to try them in</template
				>
			</p>
			<section v-for="font in compared(tab as Compared)" :key="font.name" class="font">
				<h3 class="flex items-center gap-2">
					<GlyphToggle
						:model-value="isReviewed(tab, font)"
						@change="markReviewed(tab, font, $event)"
					>
						reviewed
					</GlyphToggle>
					{{ label(font) }}
				</h3>
				<div v-if="!isReviewed(tab, font)" class="flex flex-wrap pr-px pb-px">
					<figure
						v-for="name in font[tab as Compared]"
						:key="name"
						:title="`${name}: approved, now, over each other`"
						class="glyph-cell changed"
					>
						<div class="flex gap-2">
							<span class="glyph text-flamingo" :style="set(font, 'approved')">{{
								font.characters[name]
							}}</span>
							<span class="glyph" :style="set(font)">{{ font.characters[name] }}</span>
							<!-- In one grid cell, on one baseline: absolutely, the second would hang from the
							top of the box, which the page's font sets, not the glyph's -->
							<span class="glyph inline-grid items-baseline *:[grid-area:1/1]">
								<span class="text-flamingo" :style="set(font, 'approved')">{{
									font.characters[name]
								}}</span>
								<span class="opacity-60" :style="set(font)">{{ font.characters[name] }}</span>
							</span>
						</div>
						<figcaption>{{ caption(font, name) }}</figcaption>
					</figure>
				</div>
				<template v-if="tab === 'watch' && !isReviewed(tab, font)">
					<GlyphText
						:model-value="settings.texts.watch ?? review.watch"
						class="mt-3"
						:lang
						:style="text(font)"
						@update:model-value="settings.texts.watch = $event ?? ''"
					/>
					<GlyphBefore
						v-if="settings.before && font.before"
						:text="settings.texts.watch ?? review.watch"
						:label="before(font)"
						:lang
						:style="text(font, 'before')"
					/>
				</template>
			</section>
		</template>

		<template v-else-if="review && tab === 'noto'">
			<p class="my-4 opacity-60">
				The Japanese of src/pixel.py next to the Latin: at grade 0 for reference, before in red,
				now, then over each other, and vertically. The characters that changed come first. The
				review fonts keep kana, punctuation, the most common kanji, the text below and the
				characters of .tmp/watch.txt.
			</p>
			<p v-if="!review.noto.reference" class="my-4 font-bold text-flamingo">
				No reference: nothing is compared. Run <code>pnpm review --before DIR</code>, DIR the
				dist/ttf of a checkout built before the change.
			</p>
			<p v-else class="my-4 opacity-60">
				Before: the built fonts of {{ review.noto.reference.from }}, copied
				{{ review.noto.reference.at }}, {{ review.noto.reference.hash }}.
			</p>
			<p v-if="notCompared.length" class="my-4">
				<span class="font-bold">Not compared</span>, kept by neither review font, the built fonts'
				in every row: <span class="text-flamingo">{{ notCompared.join(" ") }}</span
				>. Add them to .tmp/watch.txt.
			</p>
			<section v-for="font in fonts" :key="font.name" class="font">
				<h3 class="flex items-center gap-2">
					<GlyphToggle
						:model-value="isReviewed('noto', font)"
						@change="markReviewed('noto', font, $event)"
					>
						reviewed
					</GlyphToggle>
					{{ label(font) }}
					<span class="opacity-60">
						<template v-if="font.noto.before">
							{{ [...font.noto.changed].length }} of {{ font.noto.count }} changed
						</template>
						<template v-else>no reference for this font</template>
					</span>
				</h3>
				<div v-if="!isReviewed('noto', font)" class="flex flex-col gap-3">
					<figure v-if="font.noto.changed" class="jp-changed">
						<figcaption class="text-sm opacity-60">
							changed: before, now, over each other
						</figcaption>
						<div class="overlay text-flamingo" :style="jpSet(font, 'before')">
							{{ font.noto.changed }}
						</div>
						<div class="overlay" :style="jpSet(font, 'now')">{{ font.noto.changed }}</div>
						<div class="grid *:[grid-area:1/1]" aria-hidden="true">
							<div class="overlay text-flamingo" :style="jpSet(font, 'before')">
								{{ font.noto.changed }}
							</div>
							<div class="overlay opacity-60" :style="jpSet(font, 'now')">
								{{ font.noto.changed }}
							</div>
						</div>
					</figure>
					<!-- Coloured inline: GlyphText's text-inherit wins over a class -->
					<figure v-for="row in jpRows(font)" :key="row.key">
						<figcaption class="text-sm opacity-60">{{ row.label }}</figcaption>
						<GlyphText
							:model-value="japaneseText"
							lang="ja"
							:style="row.style"
							@update:model-value="settings.texts.noto = $event ?? ''"
						/>
					</figure>
					<!-- Over each other, in one grid cell: both wrap the same, their advances are -->
					<figure v-if="font.noto.before">
						<figcaption class="text-sm opacity-60">before and now, over each other</figcaption>
						<div class="grid *:[grid-area:1/1]" aria-hidden="true" lang="ja">
							<div class="overlay text-flamingo" :style="jpSet(font, 'before')">
								{{ japaneseText }}
							</div>
							<div class="overlay opacity-60" :style="jpSet(font, 'now')">{{ japaneseText }}</div>
						</div>
					</figure>
					<figure>
						<figcaption class="text-sm opacity-60">
							vertically:
							{{
								jpRows(font)
									.map((row) => row.label)
									.join(", ")
							}}
						</figcaption>
						<div class="flex gap-4" lang="ja">
							<div
								v-for="row in jpRows(font)"
								:key="row.key"
								class="overlay vertical"
								:style="row.style"
							>
								{{ verticalText }}
							</div>
						</div>
						<GlyphText
							:model-value="verticalText"
							class="mt-2 text-sm"
							@update:model-value="settings.texts.vertical = $event ?? ''"
						/>
					</figure>
				</div>
			</section>
		</template>

		<template v-else-if="module">
			<p class="my-4 opacity-60">
				{{ module.about }} New glyphs are shaded in
				<span class="bg-flamingo/16 px-1">flamingo</span>, changed ones in
				<span class="bg-navy/16 px-1">navy</span>.
			</p>
			<section v-for="font in fonts" :key="font.name" class="font">
				<h3 class="flex items-center gap-2">
					<GlyphToggle
						:model-value="isReviewed(module.name, font)"
						@change="markReviewed(module.name, font, $event)"
					>
						reviewed
					</GlyphToggle>
					{{ label(font) }}
				</h3>
				<template v-if="!isReviewed(module.name, font)">
					<GlyphGrid
						:glyphs="glyphs(font, module.glyphs)"
						:font="set(font)"
						:size="settings.size"
						:width="module.width"
					/>
					<GlyphText
						:model-value="settings.texts[module.name] ?? module.samples.join('  ')"
						class="mt-3"
						:lang
						:style="text(font)"
						@update:model-value="settings.texts[module.name] = $event ?? ''"
					/>
					<GlyphBefore
						v-if="settings.before && font.before"
						:text="settings.texts[module.name] ?? module.samples.join('  ')"
						:label="before(font)"
						:lang
						:style="text(font, 'before')"
					/>
				</template>
			</section>
		</template>

		<p v-else-if="missing" class="my-4">
			No review yet: run <code>pnpm review</code> at the root of the repository.
		</p>
	</GlyphLayout>
</template>

<style scoped>
@reference "~/assets/css/index.css";

/* Each font's title stays in view until the end of its section, under the header, and has a
border only above what it is the title of: reviewed sections are only a title */
.font h3 {
	@apply sticky top-(--header) z-[5] -mx-5 px-5 py-2 bg-inherit;
}

.font h3:not(:last-child) {
	@apply mb-3 border-b border-current/20;
}

.font:has(h3:not(:last-child)) {
	@apply pb-3;
}

/* Set as GlyphText's text, to wrap as it does */
.overlay {
	@apply whitespace-pre-wrap break-words;
	font-size: var(--size);
	line-height: 1.3;
	font-kerning: normal;
}

/* Vertical text, as tall as a few lines are wide */
.vertical {
	writing-mode: vertical-rl;
	text-orientation: mixed;
	max-height: calc(var(--size) * 12);
}

/* Full bleed, out of the padding of main */
.font {
	@apply -mx-5 px-5 border-b border-current/20 bg-inherit;
}

.font:first-of-type {
	@apply border-t;
}
</style>
