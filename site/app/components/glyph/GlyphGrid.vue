<script setup lang="ts">
import { useWindowVirtualizer } from "@tanstack/vue-virtual"
import type { StyleValue } from "vue"

const props = defineProps<{ glyphs: GridGlyph[]; font: StyleValue; size: number; width?: number }>()

const minimum = computed(() => Math.floor(props.size * (Math.max(props.width ?? 1, 1) + 0.3) + 20))
const PADDING = 14

const grid = useTemplateRef("grid")
const available = ref(0)
const top = ref(0)
const observer = import.meta.client
	? new ResizeObserver(() => {
			if (!grid.value) return
			available.value = grid.value.clientWidth
			top.value = grid.value.getBoundingClientRect().top + window.scrollY
		})
	: undefined
onMounted(() => observer?.observe(document.body))
watch(grid, (element, previous) => {
	if (previous) observer?.unobserve(previous)
	if (element) observer?.observe(element)
})
onBeforeUnmount(() => observer?.disconnect())
const columns = computed(() => Math.max(1, Math.floor((available.value + 1) / (minimum.value - 1))))
const track = computed(() =>
	Math.max(minimum.value - 1, Math.round((available.value + 1) / columns.value)),
)
const cell = computed(() => track.value + 1)

// Wider glyphs (⸻, Ⅷ) span as many cells as they need, so cells stay in columns: measured once
// rendered, and again when fonts load
const spans = reactive(new Map<string, number>())
const key = (glyph: GridGlyph) => glyph.title ?? glyph.caption
watch(
	() => [props.font, props.size],
	() => spans.clear(),
)
const rows = computed(() => {
	const rows: { glyph: GridGlyph; span: number }[][] = []
	let used = columns.value
	for (const glyph of props.glyphs) {
		const span = Math.min(spans.get(key(glyph)) ?? 1, columns.value)
		if (used + span > columns.value) {
			rows.push([])
			used = 0
		}
		rows.at(-1)!.push({ glyph, span })
		used += span
	}
	return rows
})

const virtualizer = useWindowVirtualizer(
	computed(() => ({
		count: rows.value.length,
		estimateSize: () => track.value,
		overscan: 2,
		scrollMargin: top.value,
	})),
)
watch(
	() => [rows.value, track.value],
	() => virtualizer.value.measure(),
)

function measure() {
	for (const element of grid.value?.querySelectorAll<HTMLElement>("[data-key]") ?? []) {
		const glyph = element.querySelector<HTMLElement>(".glyph")!
		const span = Math.ceil((glyph.offsetWidth + PADDING) / track.value)
		if ((spans.get(element.dataset.key!) ?? 1) !== span) spans.set(element.dataset.key!, span)
	}
}
watch(
	() => virtualizer.value.getVirtualItems(),
	() => nextTick(measure),
)
onMounted(() => document.fonts.addEventListener("loadingdone", measure))
onBeforeUnmount(() => document.fonts.removeEventListener("loadingdone", measure))
</script>

<template>
	<div
		ref="grid"
		class="relative -mx-5 overflow-x-clip"
		:style="[font, { height: `${virtualizer.getTotalSize() + 1}px` }]"
	>
		<div
			v-for="row in virtualizer.getVirtualItems()"
			:key="row.key"
			class="absolute -left-px right-0 top-0 grid"
			:style="{
				transform: `translateY(${row.start - virtualizer.options.scrollMargin}px)`,
				gridTemplateColumns: `repeat(${columns}, minmax(0, 1fr))`,
			}"
		>
			<figure
				v-for="{ glyph, span } in rows[row.index]"
				:key="key(glyph)"
				:data-key="key(glyph)"
				:title="glyph.title"
				class="glyph-cell"
				:class="[glyph.mark, glyph.origin]"
				:style="{ height: `${cell}px`, gridColumn: span > 1 ? `span ${span}` : undefined }"
			>
				<div class="flex-1 grid place-items-center">
					<span class="glyph">{{ glyph.character }}</span>
				</div>
				<figcaption>{{ glyph.caption }}</figcaption>
			</figure>
		</div>
	</div>
</template>

<style>
@reference "~/assets/css/index.css";

.glyph-cell {
	@apply flex flex-col items-center min-w-0 pt-1 px-1.5 -mr-px -mb-px border border-(--line);
}

.glyph-cell.new .glyph {
	@apply bg-flamingo/16;
}

.glyph-cell.changed .glyph {
	@apply bg-navy/16;
}

.glyph-cell figcaption {
	@apply font-0 not-italic font-normal text-xs opacity-60;
}

.glyph-cell.redaction .glyph {
	@apply bg-flamingo/16;
}

.glyph-cell.drawn .glyph {
	@apply bg-navy/16;
}

.glyph {
	@apply bg-current/8 whitespace-pre;
	font-size: var(--size);
	line-height: 1.2;
}
</style>
