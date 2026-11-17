import { defineCachedEventHandler } from "nitropack/runtime"

import snapshot from "../data/nikkei.json"

export type Day = {
	date: string
	open: number
	high: number
	low: number
	close: number
}

type Chart = {
	chart: {
		result: {
			meta: { gmtoffset: number }
			timestamp: number[]
			indicators: { quote: Record<"open" | "high" | "low" | "close", (number | null)[]>[] }
		}[]
	}
}

export default defineCachedEventHandler(
	async (): Promise<Day[]> => {
		try {
			const { chart } = await $fetch<Chart>(
				"https://query1.finance.yahoo.com/v8/finance/chart/%5EN225",
				{
					query: { range: "3mo", interval: "1d" },
					// Yahoo answers 429 without a browser user agent
					headers: { "user-agent": "Mozilla/5.0" },
				},
			)
			const { meta, timestamp, indicators } = chart.result[0]!
			const quote = indicators.quote[0]!
			const days: Day[] = []
			timestamp.forEach((time, i) => {
				const [open, high, low, close] = [
					quote.open[i],
					quote.high[i],
					quote.low[i],
					quote.close[i],
				]
				if (open == null || high == null || low == null || close == null) return
				const date = new Date((time + meta.gmtoffset) * 1000).toISOString().slice(0, 10)
				days.push({ date, open, high, low, close })
			})
			if (days.length < 31) throw new Error("Not enough trading days")

			return days.slice(-31)
		} catch (error) {
			console.warn("Nikkei 225 unavailable, using the snapshot", error)

			return snapshot
		}
	},
	{ maxAge: 60 * 60 },
)
