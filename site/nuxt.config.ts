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
		modules: ["@nuxtjs/plausible"],
		plausible: {
			apiHost: "/p7e",
			autoOutboundTracking: true,
		},
		ignore: ["**/pages/glyphs.vue", "**/pages/review.vue"],
		nitro: {
			ignore: ["**/api/glyphs.get.ts"],
			vercel: {
				config: {
					routes: [{ src: "/p7e/(.*)", dest: "https://plausible.io/$1" }],
				},
			},
		},
	},

	vite: {
		plugins: [tailwindcss()],
		server: {
			allowedHosts: [".ts.net"],
		},
	},
})
