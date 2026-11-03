<script setup lang="ts">
// A page of glyphs: a sticky header, and glyphs `size` pixels big in --size. The header wraps: its
// height is --header, for what sticks under it. --line is the colour of lines, opaque
defineProps<{ size: number; dark: boolean }>()

// Tools, not the marketing page: text at a fixed size, not fluid with the viewport (index.css)
useHead({ htmlAttrs: { style: "font-size: 16px" } })

const header = useTemplateRef("header")
const height = ref(0)
const observer = import.meta.client
	? new ResizeObserver(([entry]) => (height.value = entry!.borderBoxSize[0]!.blockSize))
	: undefined
watch(header, (element, previous) => {
	if (previous) observer?.unobserve(previous)
	if (element) observer?.observe(element)
})
onBeforeUnmount(() => observer?.disconnect())
</script>

<template>
	<div
		class="min-h-lvh"
		:class="dark ? 'dark' : 'bg-paper'"
		:style="{
			'--size': `${size}px`,
			'--header': `${height}px`,
			'--line': dark
				? 'color-mix(in srgb, var(--color-paper) 20%, var(--color-ink))'
				: 'color-mix(in srgb, var(--color-ink) 20%, var(--color-paper))',
		}"
	>
		<header
			ref="header"
			class="sticky top-0 z-10 flex flex-wrap items-center gap-x-6 gap-y-2 px-5 py-3 bg-inherit border-b border-current"
		>
			<slot name="header" />
		</header>
		<main class="px-5 pb-12 bg-inherit">
			<slot />
		</main>
	</div>
</template>
