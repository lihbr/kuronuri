<script setup lang="ts">
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
