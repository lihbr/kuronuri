<script setup lang="ts">
const COMMAND = "npm install @lihbr/kuronuri"
const copied = ref(false)
let timeout: ReturnType<typeof setTimeout> | undefined

async function copy() {
	clearTimeout(timeout)
	try {
		await navigator.clipboard.writeText(COMMAND)
		copied.value = true
		timeout = setTimeout(() => (copied.value = false), 1500)
	} catch (error) {
		console.error("Failed to copy text: ", error)
	}
}
</script>

<template>
	<div class="space-y-2.5">
		<h2 lang="ja" class="border-b-[0.15625rem] font-50 font-bold text-[2rem]/tight text-center">
			インストール
		</h2>

		<section class="space-y-2.5">
			<InstallHeading ja="デスクトップ">Desktop</InstallHeading>
			<p>7 families, regular, italic and bold, as ttf and woff2.</p>
			<p lang="ja" class="lowercase">
				全7ファミリー、レギュラー・イタリック・ボールドの3スタイル、TTF・WOFF2 形式で提供。
			</p>
			<div class="py-2.5 border-y border-ink/50">
				<NuxtLink
					to="https://github.com/lihbr/kuronuri/releases/latest"
					target="_blank"
					class="block h-20 pt-4 border-[0.15625rem] font-70 text-center no-underline hover:dark"
				>
					<span lang="ja" class="block font-bold text-[2rem]/tight">ダウンロード</span>
					<span class="block">DOWNLOAD =></span>
				</NuxtLink>
			</div>
		</section>

		<section class="space-y-2.5 font-50">
			<InstallHeading ja="ウェブ">Web</InstallHeading>
			<button class="block w-full text-left cursor-copy" @click="copy">
				<i class="text-ink/50"># {{ copied ? "copied!" : "click to copy" }}</i
				><br />{{ COMMAND }}
			</button>
			<hr class="border-ink/50" />
			<pre
				class="font-50 whitespace-pre-wrap"
			><code class="font-50"><i class="text-ink/50">/* css, -0, -10, -20, -35, -50, -70, -100 */</i>
@import "@lihbr/kuronuri/kuronuri-35.css";

<i class="text-ink/50">/* latin only */</i>
@import "@lihbr/kuronuri/kuronuri-35-latin.css";

body {
	font-family: "kuronuri 35", serif;
}</code></pre>
			<hr class="border-ink/50" />
			<pre
				class="font-50 whitespace-pre-wrap"
			><code class="font-50"><i class="text-ink/50">/* the fonts are split into woff2 slices so browsers only download what a page uses, the package is laid out like a <NuxtLink to="https://fontsource.org" target="_blank">fontsource</NuxtLink> one */</i>

<i lang="ja" class="text-ink/50">/* フォントは woff2 のスライスに分割されているため、ブラウザはページで使われる分だけをダウンロードします。パッケージ構成は <NuxtLink to="https://fontsource.org" target="_blank">fontsource</NuxtLink> に準拠しています */</i></code></pre>
		</section>
	</div>
</template>
