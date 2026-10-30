/** `defaults`, then what was saved in local storage under `key`, saved there on every change */
export function useStoredSettings<T extends object>(key: string, defaults: T): T {
	const settings = reactive(structuredClone(defaults)) as T
	onMounted(() => {
		Object.assign(settings, JSON.parse(localStorage.getItem(key) ?? "{}"))
		watch(settings, () => localStorage.setItem(key, JSON.stringify(settings)), { deep: true })
	})
	return settings
}
