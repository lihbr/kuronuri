<script setup lang="ts">
// The glyphs drawn in src/glyphs, in development only (nuxt.config.ts), from what `pnpm review`
// writes to temp/review: the drawn fonts, with the built ones behind them for everything else, and
// what changed since they were approved

type Font = {
	name: string
	grid: number | null
	style: string
	family: string
	weight: number
	italic: boolean
	characters: Record<string, string>
	changed: string[]
	watch: string[] // in watch.txt, to look at closely
	new: string[]
	revisions: Record<string, string> // module, "changed" or "watch": hash of its glyphs
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

const family = (font: Font, approved = false) => `review ${font.name}${approved ? " approved" : ""}`
const face = (font: Font, approved = false) => `@font-face {
	font-family: "${family(font, approved)}";
	src: url("/_review/fonts/${approved ? "approved/" : ""}${font.name}.ttf?v=${review.value?.version}");
	font-weight: ${font.weight};
	font-style: ${font.italic ? "italic" : "normal"};
}`
useHead({
	title: "Review",
	style: [
		{
			key: "review-fonts",
			innerHTML: computed(() =>
				(review.value?.fonts ?? []).flatMap((font) => [face(font), face(font, true)]).join("\n"),
			),
		},
	],
})
const set = (font: Font, approved = false) => ({
	fontFamily: `"${family(font, approved)}", "${font.family}", serif`,
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
const features = computed(() =>
	[...(module.value?.features ?? []), ...(settings.ss01 ? ["ss01"] : [])]
		.map((tag) => `"${tag}"`)
		.join(", "),
)
</script>

<template>
	<GlyphLayout :size="settings.size" :dark="settings.dark">
		<template #header>
			<h1 class="font-bold">Kuronuri review</h1>
			<GlyphRange v-model="settings.size" />
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
				<GlyphToggle v-model="settings.dark">dark</GlyphToggle>
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
					>: the glyphs of watch.txt, changed or not, and text to try them in</template
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
							<span class="glyph text-flamingo" :style="set(font, true)">{{
								font.characters[name]
							}}</span>
							<span class="glyph" :style="set(font)">{{ font.characters[name] }}</span>
							<!-- In one grid cell, on one baseline: absolutely, the second would hang from the
							top of the box, which the page's font sets, not the glyph's -->
							<span class="glyph inline-grid items-baseline *:[grid-area:1/1]">
								<span class="text-flamingo" :style="set(font, true)">{{
									font.characters[name]
								}}</span>
								<span class="opacity-60" :style="set(font)">{{ font.characters[name] }}</span>
							</span>
						</div>
						<figcaption>{{ caption(font, name) }}</figcaption>
					</figure>
				</div>
				<GlyphText
					v-if="tab === 'watch' && !isReviewed(tab, font)"
					:model-value="settings.texts.watch ?? review.watch"
					class="mt-3"
					:style="set(font)"
					@update:model-value="settings.texts.watch = $event ?? ''"
				/>
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
						:style="[set(font), features && { fontFeatureSettings: features }]"
						@update:model-value="settings.texts[module.name] = $event ?? ''"
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

/* Full bleed, out of the padding of main */
.font {
	@apply -mx-5 px-5 border-b border-current/20 bg-inherit;
}

.font:first-of-type {
	@apply border-t;
}
</style>
