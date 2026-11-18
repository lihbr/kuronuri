// Inlined, so swapping the favicon fetches nothing
const ICONS = import.meta.glob<string>("../assets/icon/*.svg", {
	query: "?raw",
	import: "default",
	eager: true,
})

export function useFavicon(variant: Ref<number>): void {
	const visible = ref(false)
	useHead({
		link: computed(() =>
			visible.value
				? [
						{
							key: "icon",
							rel: "icon",
							type: "image/svg+xml",
							href: `data:image/svg+xml,${encodeURIComponent(ICONS[`../assets/icon/${VARIANTS[variant.value]}.svg`]!)}`,
						},
					]
				: [],
		),
	})

	function onVisibilityChange() {
		visible.value = !document.hidden
	}

	onMounted(() => {
		document.addEventListener("visibilitychange", onVisibilityChange)
		onVisibilityChange()
	})
	onBeforeUnmount(() => {
		document.removeEventListener("visibilitychange", onVisibilityChange)
	})
}
