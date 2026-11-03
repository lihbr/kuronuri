<script setup lang="ts">
import latin20 from "kuronuri/files/kuronuri-20-latin-400-normal.woff2?url"
import latin50Italic from "kuronuri/files/kuronuri-50-latin-400-italic.woff2?url"
import title95 from "kuronuri/files/kuronuri-95-700-normal.woff2?url"
import title108 from "kuronuri/files/kuronuri-108-700-normal.woff2?url"
import title119 from "kuronuri/files/kuronuri-119-700-normal.woff2?url"

// The slices of the fonts the hero first paints with
const TITLE = { [title95]: "塗", [title108]: "黒", [title119]: "りフォント" }

// Japanese faces load after the first paint, so the title's characters get their own
const titleFaces = Object.entries(TITLE).map(([href, characters]) => {
	const range = [...characters].map((c) => `U+${c.codePointAt(0)!.toString(16)}`).join(", ")
	return `@font-face { font-family: "Kuronuri"; font-weight: 700; font-display: swap; src: url("${href}") format("woff2"); unicode-range: ${range}; }`
})

useHead({
	link: [...Object.keys(TITLE), latin50Italic, latin20].map((href) => ({
		rel: "preload",
		href,
		as: "font",
		type: "font/woff2",
		crossorigin: "anonymous",
	})),
	style: [{ innerHTML: titleFaces.join("\n") }],
})

const variant = ref(0)
useFavicon(variant)

let touch: MediaQueryList | undefined
let motion: MediaQueryList | undefined
let interval: ReturnType<typeof setInterval> | undefined

function onPointerMove(event: PointerEvent) {
	if (event.pointerType !== "mouse") return
	const index = Math.floor((event.clientX / window.innerWidth) * FONTS.length)
	variant.value = Math.min(Math.max(index, 0), FONTS.length - 1)
}

function cycle() {
	if (touch?.matches && motion?.matches) variant.value = (variant.value + 1) % FONTS.length
}

onMounted(() => {
	touch = window.matchMedia("(hover: none)")
	motion = window.matchMedia("(prefers-reduced-motion: no-preference)")
	window.addEventListener("pointermove", onPointerMove)
	interval = setInterval(cycle, 1000)
})
onBeforeUnmount(() => {
	window.removeEventListener("pointermove", onPointerMove)
	clearInterval(interval)
})
</script>

<template>
	<header class="min-h-svh grid grid-rows-[1fr_auto_1fr]">
		<div
			class="p-2.5 bg-paper max-md:space-y-2.5 md:flex flex-row-reverse flex-wrap justify-between gap-x-5 font-50 italic lowercase"
		>
			<p class="md:text-right">
				<NuxtLink to="https://www.redaction.us" target="_blank">Redaction</NuxtLink>
				© 2019 MCKL Inc., by Jeremy Mickel and Forest Young<br />
				<NuxtLink to="https://fonts.google.com/noto" target="_blank">Noto Serif JP</NuxtLink>
				© 2017-2024 Adobe, © 2012 Google Inc.
			</p>
			<p>
				Kuronuri, created by <NuxtLink to="https://lihbr.com">lihbr</NuxtLink><br />fonts are
				<NuxtLink to="https://github.com/lihbr/kuronuri/blob/HEAD/OFL.txt">OFL</NuxtLink>,
				<NuxtLink to="https://github.com/lihbr/kuronuri">code</NuxtLink> is mit
			</p>
		</div>
		<hgroup class="row-span-2 layout grid-rows-subgrid">
			<div class="col-span-full lg:col-start-3 lg:col-span-6 lg:-mx-2.5 @container dark">
				<h1
					lang="ja"
					:class="FONTS[variant]"
					class="text-center pt-[3cqi] pb-[1cqi] font-bold text-[13.6cqi]/tight whitespace-nowrap overflow-hidden"
				>
					黒塗りフォント
				</h1>
			</div>
			<p
				class="col-start-3 col-span-2 md:col-start-6 md:col-span-1 lg:col-start-8 self-start mt-2.5 font-20 text-xl/tight lowercase"
			>
				Kuronuri Font,
				<NuxtLink to="https://www.redaction.us" target="_blank" class="italic">Redaction</NuxtLink>,
				with japanese support, and more
			</p>
		</hgroup>
	</header>
</template>
