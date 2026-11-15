<script setup lang="ts">
// The size of glyphs, in pixels
const model = defineModel<number>({ required: true })
const { min = 16 } = defineProps<{ min?: number }>()
</script>

<template>
	<label class="flex items-center gap-2">
		size
		<input v-model.number="model" type="range" :min max="240" class="range" />
	</label>
</template>

<style scoped>
@reference "~/assets/css/index.css";

.range {
	@apply appearance-none w-32 h-3 bg-current/20 outline-none;
}

/* Not the site's colours on mouse focus, which hide the handle */
.range:focus {
	@apply text-inherit bg-current/20;
}

.range:focus-visible {
	@apply bg-flamingo;
}

.range::-webkit-slider-thumb {
	@apply appearance-none size-3 bg-current;
}

.range::-moz-range-thumb {
	@apply size-3 bg-current border-0 rounded-none;
}
</style>
