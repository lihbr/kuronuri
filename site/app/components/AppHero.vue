<script setup lang="ts">
import latin20 from "@lihbr/kuronuri/files/kuronuri-20-latin-400-normal.woff2?url"
import latin50Italic from "@lihbr/kuronuri/files/kuronuri-50-latin-400-italic.woff2?url"

const TITLE = import.meta.glob<string>("../assets/title/*.svg", {
	query: "?raw",
	import: "default",
	eager: true,
})
const title = (name: string) => TITLE[`../assets/title/${name}.svg`]

useHead({
	link: [latin50Italic, latin20].map((href) => ({
		rel: "preload",
		href,
		as: "font",
		type: "font/woff2",
		crossorigin: "anonymous",
	})),
})

const variant = ref(0)
useFavicon(variant)

let touch: MediaQueryList | undefined
let motion: MediaQueryList | undefined
let interval: ReturnType<typeof setInterval> | undefined

function onPointerMove(event: PointerEvent) {
	if (event.pointerType !== "mouse") return
	const index = Math.floor((event.clientX / window.innerWidth) * VARIANTS.length)
	variant.value = Math.min(Math.max(index, 0), VARIANTS.length - 1)
}

function cycle() {
	if (touch?.matches && motion?.matches) variant.value = (variant.value + 1) % VARIANTS.length
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
			class="p-2.5 bg-white max-md:space-y-2.5 md:flex flex-row-reverse flex-wrap justify-between gap-x-5 font-50 italic lowercase"
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
				<NuxtLink to="https://github.com/lihbr/kuronuri">code</NuxtLink> is mit<br /><br />
				<NuxtLink to="#install">install ^-</NuxtLink>
			</p>
		</div>
		<hgroup class="row-span-2 layout grid-rows-subgrid">
			<div class="col-span-full lg:col-start-3 lg:col-span-6 lg:-mx-2.5 @container dark">
				<h1 lang="ja" class="pt-[3.34cqi] pb-[1.34cqi] overflow-hidden">
					<span class="sr-only">黒塗りフォント</span>
					<span
						aria-hidden="true"
						class="flex justify-center *:h-[16.32cqi] *:w-auto *:overflow-visible"
						v-html="title(VARIANTS[variant]!)"
					/>
				</h1>
			</div>
			<p
				class="col-start-0 col-span-2 md:col-start-5 md:col-span-1 lg:col-start-7 self-start mt-2.5 font-20 text-xl/tight lowercase"
			>
				Kuronuri Font,
				<NuxtLink to="https://www.redaction.us" target="_blank" class="italic">Redaction</NuxtLink>,
				with japanese support, and more.
			</p>
			<p
				class="col-start-3 col-span-2 md:col-start-6 md:col-span-1 lg:col-start-8 self-start mt-2.5 font-20 text-xl/tight lowercase"
				lang="ja"
			>
				<NuxtLink to="https://www.redaction.us" target="_blank" class="italic">Redaction</NuxtLink>
				を日本語に対応させ、さらに拡張。
			</p>
		</hgroup>
	</header>
</template>
