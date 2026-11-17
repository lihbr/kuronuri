<script setup lang="ts">
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

.text {
	@apply block w-full overflow-hidden resize-none field-sizing-content bg-transparent text-inherit outline-none;
	font-size: var(--size);
	line-height: 1.3;
	font-kerning: normal;
}
</style>
