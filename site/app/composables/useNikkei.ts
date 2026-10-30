import type { Day } from "~~/server/api/nikkei.get"

const STORAGE_KEY = "kuronuri:nikkei"

/** The last trading days of the Nikkei 225: built with the site, then refreshed once a day */
export function useNikkei(): ComputedRef<Day[]> {
	const { data: built } = useFetch("/api/nikkei")
	const fresh = ref<Day[]>()

	// Static hosts answer with their HTML fallback, and an older version of the site may have stored
	// fewer days: only take the same number of days as the build, and not older ones
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
			// The built data stays
		}
	})

	return computed(() => fresh.value ?? built.value ?? [])
}
