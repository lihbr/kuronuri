<script setup lang="ts">
// A line every two columns, in the middle of their gutter: 1 on 4 columns, 2 on 6, 4 on 10.
const LINES = [
	"left-1/2 md:hidden",
	"left-1/3 max-md:hidden lg:left-1/5",
	"left-2/3 max-md:hidden lg:left-2/5",
	"left-3/5 max-lg:hidden",
	"left-4/5 max-lg:hidden",
]
</script>

<template>
	<div aria-hidden="true" class="absolute inset-0 -z-10 pointer-events-none">
		<div
			v-for="line in LINES"
			:key="line"
			:class="line"
			class="absolute inset-y-0 w-px bg-ink/50"
		/>
	</div>
</template>
