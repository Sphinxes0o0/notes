import { defineConfig, type DefaultTheme } from 'vitepress'
import fs from 'node:fs'

function parseDocsifySidebar(filePath: string): DefaultTheme.Sidebar {
	if (!fs.existsSync(filePath)) {
		return []
	}
	const content = fs.readFileSync(filePath, 'utf-8')
	const lines = content.split(/\r?\n/)
	const sidebar: DefaultTheme.Sidebar = []
	let currentGroup: DefaultTheme.SidebarItem[] = []
	let currentGroupTitle: string | undefined

	function flushGroup() {
		if (currentGroup.length > 0) {
			sidebar.push({
				text: currentGroupTitle ?? '',
				items: currentGroup,
			})
			currentGroup = []
			currentGroupTitle = undefined
		}
	}

	for (const rawLine of lines) {
		const line = rawLine.trim()
		if (!line) continue
		if (line.startsWith('## ')) {
			flushGroup()
			currentGroupTitle = line.replace(/^##\s+/, '')
			continue
		}
		if (line.startsWith('* ') || line.startsWith('- ')) {
			const match = line.match(/\[(.+?)\]\((.+?)\)/)
			if (match) {
				const [, text, link] = match
				const item: DefaultTheme.SidebarItem = { text, link: normalizeLink(link) }
				if (currentGroupTitle) {
					currentGroup.push(item)
				} else {
					sidebar.push(item)
				}
			}
		}
	}
	flushGroup()
	return sidebar
}

function normalizeLink(link: string): string {
	// VitePress prefers .md paths relative to root starting with /
	if (link.startsWith('http')) return link
	if (link.startsWith('/')) return link
	return `/${link.replace(/\\/g, '/')}`
}

function normalizeBase(input: string): string {
	let b = input || '/'
	if (!b.startsWith('/')) b = '/' + b
	if (!b.endsWith('/')) b = b + '/'
	return b
}

const base = normalizeBase(process.env.DEPLOY_BASE ?? '/')

export default defineConfig({
	title: "Sphinx's Notes",
	description: 'Personal technical notes',
	lang: 'zh-CN',
	lastUpdated: true,
	ignoreDeadLinks: true,
	base,
	vite: {
		publicDir: 'resources',
	},
	markdown: {
		html: false,
		config: (md) => {
			const rawText = md.renderer.rules.text || ((tokens, idx) => tokens[idx].content)
			md.renderer.rules.text = (tokens, idx, options, env, self) => {
				// Escape Vue mustache braces to avoid interpolation inside code-like content
				tokens[idx].content = tokens[idx].content
					.replace(/\{\{/g, '&#123;&#123;')
					.replace(/\}\}/g, '&#125;&#125;')
				return rawText(tokens, idx, options, env, self)
			}

			const defaultImage = md.renderer.rules.image || ((tokens, idx, options, env, self) => self.renderToken(tokens, idx, options))
			md.renderer.rules.image = (tokens, idx, options, env, self) => {
				const srcIndex = tokens[idx].attrIndex('src')
				if (srcIndex >= 0 && tokens[idx].attrs) {
					let src = tokens[idx].attrs[srcIndex][1]
					// Normalize any path that contains "resources/" to root-absolute without leading ../
					const pos = src.indexOf('resources/')
					if (pos !== -1) {
						const rest = src.slice(pos + 'resources/'.length)
						// resources acts as publicDir, so served from site root; base is handled by VitePress
						src = `/${rest}`
						tokens[idx].attrs[srcIndex][1] = src
					}
				}
				return defaultImage(tokens, idx, options, env, self)
			}
		},
	},
	themeConfig: {
		siteTitle: "Sphinx's Notes",
		nav: [
			{ text: 'Home', link: '/' },
		],
		sidebar: parseDocsifySidebar('_sidebar.md'),
		socialLinks: [
			{ icon: 'github', link: 'https://github.com/Sphinxes0o0/notes' },
		],
	},
})