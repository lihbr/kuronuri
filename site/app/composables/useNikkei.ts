import type { Day } from "~~/server/api/nikkei.get"

const STORAGE_KEY = "kuronuri:nikkei"

export function useNikkei(): ComputedRef<Day[]> {
	const { data: built } = useFetch("/api/nikkei")
	const fresh = ref<Day[]>()

	function isUsable(candidate: unknown): candidate is Day[] {
		return (
			!!built.value &&
			Array.isArray(candidate) &&
			candidate.length === built.value.length &&
			((candidate.at(-1) as Day | undefined)?.date ?? "") >= built.value.at(-1)!.date
		)
	}

	onMounted(async () => {
		const today = new Date().toLocaleDateString("sv", { timeZone: "Asia/Tokyo" })
		try {
			const cached = JSON.parse(localStorage.getItem(STORAGE_KEY) ?? "null")
			if (cached?.date === today && isUsable(cached.days)) {
				fresh.value = cached.days
				return
			}
			const days = await $fetch<Day[]>("/api/nikkei")
			if (!isUsable(days)) return
			fresh.value = days
			localStorage.setItem(STORAGE_KEY, JSON.stringify({ date: today, days }))
		} catch {
			// noop, use built data
		}
	})

	return computed(() => fresh.value ?? built.value ?? [])
}
