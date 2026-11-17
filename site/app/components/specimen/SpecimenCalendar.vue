<script setup lang="ts">
const ROWS_BEFORE = 6
const WEEKDAYS = "月火水木金土日"
const months = FONTS.slice(0, 6).map((font, month) => {
	// From 0 on Monday to 6 on Sunday
	const weekday = (new Date(Date.UTC(1999, month, 1)).getUTCDay() + 6) % 7
	return {
		font,
		// ㋀ to ㋅
		label: String.fromCodePoint(0x32c0 + month),
		name: `1999年${month + 1}月`,
		days: new Date(Date.UTC(1999, month + 1, 0)).getUTCDate(),
		before: (7 - weekday) % 7,
	}
})
// Rows are as tall as their line
const rows = (count: number) => ({ paddingTop: `${count * 1.25}em` })

const active = ref<{ month: number; day: number; weekday: number }>()
function onPointerEnter(month: number, day: number) {
	active.value = { month, day, weekday: (day - 1 - months[month]!.before + 7) % 7 }
}
</script>

<template>
	<div
		lang="ja"
		class="grid grid-cols-[repeat(7,auto)] gap-x-1.25 gap-y-2.5 justify-start text-center tabular-nums"
		@pointerleave="active = undefined"
	>
		<span class="pr-1.25 text-right"><SpecimenMark mark="06" /></span>
		<span
			v-for="(month, i) in months"
			:key="month.name"
			:class="[month.font, { 'opacity-50': active && active.month !== i }]"
			class="font-bold transition-opacity"
		>
			{{ month.label }}
		</span>
		<ol aria-hidden="true" class="pr-1.25 font-20 font-bold" :style="rows(ROWS_BEFORE)">
			<li
				v-for="(weekday, i) in WEEKDAYS"
				:key="weekday"
				:class="{ 'opacity-50': active && active.weekday !== i }"
				class="transition-opacity"
			>
				{{ weekday }}
			</li>
		</ol>
		<ol
			v-for="(month, i) in months"
			:key="month.name"
			:aria-label="month.name"
			:class="month.font"
			:style="rows(ROWS_BEFORE - month.before)"
		>
			<li
				v-for="day in month.days"
				:key="day"
				:class="{ 'opacity-50': active && (active.month !== i || active.day !== day) }"
				class="transition-opacity"
				@pointerenter="onPointerEnter(i, day)"
			>
				{{ String(day).padStart(2, "0") }}
			</li>
		</ol>
	</div>
</template>
