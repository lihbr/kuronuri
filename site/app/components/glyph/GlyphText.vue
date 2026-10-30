<script setup lang="ts">
// Text to set glyphs in context, as big as them. Grammarly ignores spellcheck: it has its own off
// switch
const model = defineModel<string>()
</script>

<template>
	<textarea
		v-model="model"
		spellcheck="false"
		data-gramm="false"
		data-gramm_editor="false"
		data-enable-grammarly="false"
		class="text"
	/>
</template>

<style scoped>
@reference "~/assets/css/index.css";

/* As tall as its text: no scrollbar for glyphs reaching past their line */
.text {
	@apply block w-full overflow-hidden resize-none field-sizing-content bg-transparent text-inherit outline-none;
	font-size: var(--size);
	line-height: 1.3;
	font-kerning: normal;
}
</style>
