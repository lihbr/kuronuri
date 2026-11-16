<script setup lang="ts">
const COLUMN = 10
const BODY = 6
const ROWS = 5

const days = useNikkei()

const numbers = new Intl.NumberFormat("en", { minimumFractionDigits: 2, maximumFractionDigits: 2 })
const signed = (value: number) => `${value < 0 ? "−" : "+"}${numbers.format(Math.abs(value))}`

const month = computed(() =>
	days.value.slice(1).map((day, i) => {
		const previous = days.value[i]!.close
		return {
			...day,
			change: signed(day.close - previous),
			percent: `${signed(((day.close - previous) / previous) * 100)}%`,
		}
	}),
)

const candles = computed(() => {
	const low = Math.min(...month.value.map((day) => day.low))
	const high = Math.max(...month.value.map((day) => day.high))
	const padding = (high - low) * 0.06
	const min = low - padding
	const max = high + padding
	const y = (price: number) => ((max - price) / (max - min)) * 100

	return month.value.map((day, i) => {
		const top = y(Math.max(day.open, day.close))
		return {
			x: i * COLUMN,
			high: y(day.high),
			low: y(day.low),
			top,
			// Open and close can be the same
			height: Math.max(y(Math.min(day.open, day.close)) - top, 0.3),
			down: day.close < day.open,
		}
	})
})

const active = ref<number>()
const start = computed(() => Math.max((active.value ?? month.value.length - 1) + 1 - ROWS, 0))

function onPointerMove(event: PointerEvent) {
	const { left, width } = (event.currentTarget as HTMLElement).getBoundingClientRect()
	const count = month.value.length
	active.value = Math.min(
		Math.max(Math.floor(((event.clientX - left) / width) * count), 0),
		count - 1,
	)
}

function onPointerLeave(event: PointerEvent) {
	if (event.pointerType === "mouse") active.value = undefined
}
</script>

<template>
	<figure v-if="month.length" class="group max-md:grid grid-cols-2 gap-x-5 items-end">
		<figcaption lang="ja" class="mb-2.5 font-50 font-bold">日経平均株価</figcaption>
		<div
			class="max-md:col-span-2 max-md:row-start-2 aspect-3/2 border px-2.5 border-black/50 bg-white lg:-mx-2.5"
		>
			<div
				class="h-full cursor-crosshair touch-pan-y"
				@pointermove="onPointerMove"
				@pointerleave="onPointerLeave"
			>
				<svg
					:viewBox="`0 0 ${candles.length * COLUMN} 100`"
					preserveAspectRatio="none"
					class="block size-full overflow-visible"
					role="img"
					:aria-label="`Candlestick chart of the Nikkei 225, from ${month[0]!.date} to ${month.at(-1)!.date}`"
				>
					<rect
						v-if="active !== undefined"
						:x="active * COLUMN"
						:width="COLUMN"
						height="100"
						class="fill-black/5"
					/>
					<g
						v-for="candle in candles"
						:key="candle.x"
						:class="{ 'opacity-50': candle.down }"
						class="fill-black stroke-black"
					>
						<line
							:x1="candle.x + COLUMN / 2"
							:x2="candle.x + COLUMN / 2"
							:y1="candle.high"
							:y2="candle.low"
							vector-effect="non-scaling-stroke"
						/>
						<rect
							:x="candle.x + (COLUMN - BODY) / 2"
							:y="candle.top"
							:width="BODY"
							:height="candle.height"
							stroke="none"
						/>
					</g>
				</svg>
			</div>
		</div>
		<div
			class="max-md:row-start-1 max-md:col-start-2 max-md:justify-self-end max-md:bg-white flex max-lg:flex-col items-start gap-x-2.5 mb-2.5 md:mb-0 md:mt-2.5"
		>
			<SpecimenNote mark="05">50 regular, 12px<br />tabular figures</SpecimenNote>
			<!-- Every day is a row, for columns to fit the widest of the month, the ones not shown flat -->
			<table class="font-50 tabular-nums">
				<tbody>
					<tr
						v-for="(day, i) in month"
						:key="day.date"
						:class="{ 'invisible leading-0': i < start || i >= start + ROWS }"
					>
						<th scope="row" class="sr-only">{{ day.date }}</th>
						<td class="text-right">{{ day.change }}</td>
						<td class="pl-[0.5em] text-right">{{ day.percent }}</td>
						<td class="pl-[0.5em] text-right">{{ numbers.format(day.close) }}</td>
					</tr>
				</tbody>
			</table>
			<SpecimenMark mark="05" />
		</div>
	</figure>
</template>
