import { fileURLToPath } from "node:url"

import tailwindcss from "@tailwindcss/vite"

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
	compatibilityDate: "2026-10-18",
	future: {
		compatibilityVersion: 5,
	},
	devtools: { enabled: false },

	app: {
		head: {
			templateParams: {
				separator: "-",
			},
			link: [
				{ key: "favicon", rel: "icon", type: "image/x-icon", href: "/favicon.ico", sizes: "32x32" },
				{ key: "icon", rel: "icon", type: "image/svg+xml", href: "/icon.svg" },
				{ rel: "apple-touch-icon", href: "/apple-touch-icon.png" },
			],
		},
	},

	modules: ["@nuxtjs/seo"],

	site: {
		url: "https://kuronuri.lihbr.com",
		name: "Kuronuri 黒塗り",
		description:
			"黒塗り (kuronuri) is a typeface extending Redaction (a typeface originally created for The Redaction exhibition at MoMA PS1), with Japanese support, and more",
		defaultLocale: "en",
		indexable: true,
	},

	sitemap: false,

	seo: {
		fallbackTitle: false,
		meta: {
			ogImage: {
				url: "https://images.prismic.io/lihbr/W0YEiqNmn3o7rj6n_og.jpg?auto=format,compress",
				width: 1200,
				height: 630,
				alt: "黒塗りフォント, set white on black from smooth to pixelated, above “kuronuri font, redaction, with japanese support, and more.”",
			},
		},
	},

	ogImage: false,
	skewProtection: false,
	aiReady: false,
	linkChecker: false,

	css: ["~/assets/css/index.css"],

	$development: {
		nitro: {
			publicAssets: [
				{ dir: fileURLToPath(new URL("../.tmp/review", import.meta.url)), baseURL: "/_review" },
			],
		},
	},

	$production: {
		ignore: ["**/pages/glyphs.vue", "**/pages/review.vue"],
		nitro: {
			ignore: ["**/api/glyphs.get.ts"],
		},
	},

	// Vercel bills each file a visitor fetches, so the page loads one script, hints no others, and
	// skips the app manifest. Two imports stay lazy: every family in full, which would block the
	// render, and Nuxt's error pages, whose styles would be inlined in every page
	experimental: {
		appManifest: false,
	},

	hooks: {
		"build:manifest"(manifest) {
			for (const resource of Object.values(manifest)) {
				resource.prefetch = false
			}
		},
	},

	vite: {
		plugins: [tailwindcss()],
		$client: {
			build: {
				rolldownOptions: {
					output: {
						codeSplitting: {
							groups: [
								{
									name: "app",
									test: (id) => !/\/dist\/web\/|\/components\/error-\d+\.vue/.test(id),
								},
							],
						},
					},
				},
			},
		},
		server: {
			allowedHosts: [".ts.net"],
		},
	},
})
