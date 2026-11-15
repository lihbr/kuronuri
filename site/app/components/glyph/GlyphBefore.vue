<script setup lang="ts">
// Text as it was set before, under the text to edit, as big as it: spacing and features, which
// glyphs alone do not show. Its style and lang go to the text, not to its caption
defineOptions({ inheritAttrs: false })
defineProps<{ text: string; label: string }>()
</script>

<template>
	<figure class="mt-1">
		<div v-bind="$attrs" class="before">{{ text }}</div>
		<figcaption class="text-sm opacity-60">{{ label }}</figcaption>
	</figure>
</template>

<style scoped>
@reference "~/assets/css/index.css";

/* As GlyphText sets it, faded */
.before {
	@apply whitespace-pre-wrap break-words opacity-60;
	font-size: var(--size);
	line-height: 1.3;
}
</style>
