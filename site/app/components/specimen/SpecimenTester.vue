<script setup lang="ts">
const style = ref<Style>("Regular")

const GRADES = VARIANTS.map(Number)
const position = ref(35)
const variant = computed(() => {
	const nearest = GRADES.reduce((a, b) =>
		Math.abs(b - position.value) < Math.abs(a - position.value) ? b : a,
	)
	return GRADES.indexOf(nearest)
})
const settle = () => (position.value = GRADES[variant.value]!)
const STEPS: Record<string, number> = { ArrowRight: 1, ArrowUp: 1, ArrowLeft: -1, ArrowDown: -1 }
function step(event: KeyboardEvent) {
	const by = STEPS[event.key]
	if (!by) return
	event.preventDefault()
	position.value = GRADES[Math.min(Math.max(variant.value + by, 0), GRADES.length - 1)]!
}
</script>

<template>
	<div class="group">
		<SpecimenNote mark="07">
			{{ VARIANTS[variant] }} {{ style.toLowerCase() }}, 52px<br />editable
		</SpecimenNote>
		<SpecimenMark mark="07" class="block mb-2.5" />
		<div class="flex flex-wrap items-center gap-2.5 mb-5 lowercase">
			<div role="radiogroup" aria-label="Style" class="flex">
				<GlyphToggle
					v-for="(styleCss, name) in STYLES"
					:key="name"
					v-model="style"
					type="radio"
					name="style"
					:value="name"
					:style="styleCss"
				>
					{{ name }}
				</GlyphToggle>
			</div>
			<GlyphRange
				v-model="position"
				:min="0"
				:max="100"
				@change="settle"
				@keydown="step"
				class="bg-white"
			>
				<span class="sr-only">pixel size</span>
			</GlyphRange>
		</div>
		<p
			contenteditable="plaintext-only"
			spellcheck="false"
			aria-label="Type to try Kuronuri"
			:class="FONTS[variant]"
			:style="STYLES[style]"
			class="text-4xl/tight lg:text-[3.25rem]/tight bg-white focus-visible:bg-white focus-visible:text-black focus:outline-none"
			v-text="
				'黒塗り: painted or lacquered black; blacked out, as words are in a redacted document.'
			"
		/>
	</div>
</template>
