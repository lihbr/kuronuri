// Nitro imports CSS as text (rollup's raw plugin)
declare module "*.css" {
	const css: string
	export default css
}
