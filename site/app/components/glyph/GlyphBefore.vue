<script setup lang="ts">
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

.before {
	@apply whitespace-pre-wrap break-words opacity-60;
	font-size: var(--size);
	line-height: 1.3;
}
</style>
