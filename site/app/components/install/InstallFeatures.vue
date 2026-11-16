<script setup lang="ts">
type Feature = {
	sample: string
	label: string
	before?: string
	tag?: string
}

const FEATURES: Feature[] = [
	{ sample: "11", label: "tabular figures", tag: "tnum" },
	{ sample: "7/8", label: "fractions", tag: "frac" },
	{ before: "m", sample: "3", label: "superscripts", tag: "sups" },
	{ before: "O", sample: "2", label: "subscripts", tag: "subs" },
	{ sample: "12a", label: "ordinals", tag: "ordn" },
	{ sample: "AB", label: "full widths", tag: "fwid" },
	{ sample: "カナ", label: "half widths", tag: "hwid" },
	{ sample: "-^", label: "arrows", tag: "calt" },
	{ sample: "^-", label: "alternate arrows", tag: "ss01" },
	{ sample: "≤≠∞", label: "mathematical signs" },
	{ sample: "€¥₩", label: "currency signs" },
	{ sample: "℃℡", label: "letterlike symbols" },
	{ sample: "Ⅻ", label: "roman numerals" },
	{ sample: "Åœʁ", label: "latin extended" },
	{ sample: "㍿㋀", label: "japanese squares" },
	{ sample: "①Ⓐ", label: "enclosed" },
	{ sample: "\u{1F19E}\u{1F1A7}", label: "media symbols" },
]

const quoted = (text: string) => `"${text}"`
</script>

<template>
	<div>
		<InstallHeading as="h2" ja="特長">Features</InstallHeading>
		<ul class="mt-2.5 text-xs/normal">
			<li
				v-for="feature in FEATURES"
				:key="feature.label"
				:title="feature.tag && `font-feature-settings: ${quoted(feature.tag)}`"
				class="inline after:text-black/50 not-last:after:content-['_—_']"
			>
				<b
					>{{ feature.before
					}}<span :style="{ fontFeatureSettings: feature.tag && quoted(feature.tag) }">{{
						feature.sample
					}}</span></b
				>{{ " "
				}}<span class="text-black/50">
					{{ feature.label }} <i v-if="feature.tag">{{ feature.tag }}</i>
				</span>
			</li>
		</ul>
	</div>
</template>
