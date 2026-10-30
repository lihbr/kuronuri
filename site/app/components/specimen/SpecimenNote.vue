<script setup lang="ts">
defineProps<{ mark: string }>()
</script>

<template>
	<p
		class="flex gap-2.5 mb-2.5 font-35 opacity-50 transition-opacity group-hover:opacity-100 lowercase tabular-nums lg:absolute lg:left-0 lg:w-[calc(20%-0.625rem)] lg:justify-end lg:mb-0"
	>
		<span class="lg:order-last">[{{ mark }}]</span>
		<span class="lg:text-right"><slot /></span>
	</p>
</template>
