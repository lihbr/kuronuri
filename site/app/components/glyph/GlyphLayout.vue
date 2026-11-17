<script setup lang="ts">
defineProps<{ size: number; dark: boolean }>()

// Text doesn't need to be fluid.
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
		:class="dark ? 'dark' : 'bg-white'"
		:style="{
			'--size': `${size}px`,
			'--header': `${height}px`,
			'--line': dark
				? 'color-mix(in srgb, var(--color-white) 20%, var(--color-black))'
				: 'color-mix(in srgb, var(--color-black) 20%, var(--color-white))',
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
