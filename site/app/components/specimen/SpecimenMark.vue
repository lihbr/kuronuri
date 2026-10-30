<script setup lang="ts">
defineProps<{ mark: string }>()
</script>

<template>
	<span
		aria-hidden="true"
		class="font-35 opacity-50 transition-opacity group-hover:opacity-100 tabular-nums max-lg:hidden"
		>[{{ mark }}]</span
	>
</template>
