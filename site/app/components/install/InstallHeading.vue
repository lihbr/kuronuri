<script setup lang="ts">
// A heading in a bar: in English on the left, in Japanese on the right
const { as = "h3" } = defineProps<{ ja: string; as?: "h2" | "h3" }>()
</script>

<template>
	<component
		:is="as"
		class="flex justify-between gap-2.5 p-1.25 dark font-bold leading-none uppercase"
	>
		<span><slot /></span>
		<span lang="ja">{{ ja }}</span>
	</component>
</template>
