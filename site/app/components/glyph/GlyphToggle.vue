<script setup lang="ts" generic="T">
// A checkbox, or a radio of `value`, shown by its label only: black when on, flamingo when focused
const model = defineModel<T>()
defineProps<{ type?: "checkbox" | "radio"; value?: T; name?: string }>()
</script>

<template>
	<label class="glyph-toggle">
		<input v-model="model" :type="type ?? 'checkbox'" :value :name class="sr-only" />
		<slot />
	</label>
</template>

<style>
@reference "~/assets/css/index.css";

.glyph-toggle {
	@apply px-1 cursor-pointer select-none lowercase;
}

.glyph-toggle:has(:checked) {
	@apply bg-black text-white;
}

.dark .glyph-toggle:has(:checked) {
	@apply bg-white text-black;
}

.glyph-toggle:has(:focus-visible) {
	@apply bg-flamingo text-white;
}
</style>
