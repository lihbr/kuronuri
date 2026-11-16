<script setup lang="ts">
// The size of glyphs, in pixels, unless another value is labelled in the slot
const model = defineModel<number>({ required: true })
const { min = 16, max = 240 } = defineProps<{ min?: number; max?: number }>()
</script>

<template>
	<label class="flex items-center gap-2">
		<slot>size</slot>
		<input v-model.number="model" type="range" :min :max class="range" />
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
