import { writeSourceDownloads } from './downloads.mjs'
import { compressedSearchPlugin } from './plugins/compressed-search.mjs'
import { asyncSearchPlugin } from './plugins/async-search.mjs'
import { renderSearchContent } from './search.mjs'
import sidebar from './sidebar/index.mjs'
import { defineConfig } from 'vitepress'
import { VitePWA } from 'vite-plugin-pwa'
import { readingTimePlugin } from './plugins/readingTime.mjs'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  base: '/notes/',
  buildEnd: writeSourceDownloads,
  vite: { plugins: [asyncSearchPlugin(), compressedSearchPlugin()] },

  plugins: [
    readingTimePlugin(),
  ],

  title: "Sphinx's Notes",
  description: "技术学习笔记和总结",

  // Content source directory
  srcDir: '.',

  // Clean URLs without .html
  cleanUrls: true,

  // Show last updated timestamp
  lastUpdated: true,

  // Smooth scroll navigation
  smoothScroll: true,

  // Exclude courses and wiki directories from VitePress processing
  srcExclude: ['courses/**', 'wiki/**', 'android/**'],

  // Ignore dead links for excluded content
  ignoreDeadLinks: true,

  // Markdown configuration
  markdown: {
    theme: {
      light: 'github-light',
      dark: 'github-dark'
    },
    lineNumbers: true,
    container: {
      tipLabel: '💡 提示',
      warningLabel: '⚠️ 注意',
      dangerLabel: '🚨 危险',
      infoLabel: 'ℹ️ 信息',
      detailsLabel: '详情'
    },
    // These grammars are unavailable in the installed Shiki bundle.
    // Keep their language labels and render them explicitly as plain text.
    languages: ['dts', 'haproxy', 'snort', 'conf', 'pam', 'rego', 'cel', 'cedar', 'plantuml']
      .map((name) => ({ name, scopeName: `text.${name}`, patterns: [] })),
    languageAlias: { 'file_api/file_config.h': 'c' }
  },

  // PWA configuration
  pwa: {
    base: '/notes/',
    includeAssets: ['favicon.ico', 'robots.txt'],
    manifest: {
      name: "Sphinx's Notes",
      short_name: 'Sphinx笔记',
      description: '技术学习笔记和总结',
      theme_color: '#3c8772',
      background_color: '#ffffff',
      display: 'standalone',
      icons: [
        {
          src: '/pwa-192x192.svg',
          sizes: '192x192',
          type: 'image/svg+xml'
        },
        {
          src: '/pwa-512x512.svg',
          sizes: '512x512',
          type: 'image/svg+xml'
        }
      ]
    },
    workbox: {
      globPatterns: ['**/*.{js,css,html,ico,png,svg,woff,woff2}'],
      runtimeCaching: [
        {
          urlPattern: /^https:\/\/fonts\.googleapis\.com\/.*/i,
          handler: 'CacheFirst',
          options: {
            cacheName: 'google-fonts-cache',
            expiration: {
              maxEntries: 10,
              maxAgeSeconds: 60 * 60 * 24 * 365
            },
            cacheableResponse: {
              statuses: [0, 200]
            }
          }
        },
        {
          urlPattern: /^https:\/\/fonts\.gstatic\.com\/.*/i,
          handler: 'CacheFirst',
          options: {
            cacheName: 'gstatic-fonts-cache',
            expiration: {
              maxEntries: 10,
              maxAgeSeconds: 60 * 60 * 24 * 365
            },
            cacheableResponse: {
              statuses: [0, 200]
            }
          }
        }
      ]
    }
  },

  // Sitemap
  sitemap: {
    // Trailing slash required: with `base: '/notes/'`, the URL builder
    // treats `/notes` as a file that gets discarded when resolving relative
    // page paths. Without the trailing slash the sitemap emits URLs with
    // the base path missing, so every entry returns 404.
    hostname: 'https://Sphinxes0o0.github.io/notes/',
    lastmodDateOnly: false
  },

  // Head meta tags for SEO
  head: [
    ['link', { rel: 'icon', href: '/notes/logo.svg' }],
    ['meta', { name: 'theme-color', content: '#3c8772' }],
    ['meta', { name: 'og:type', content: 'website' }],
    ['meta', { name: 'og:title', content: "Sphinx's Notes" }],
    ['meta', { name: 'og:description', content: '技术学习笔记和总结' }],
    ['meta', { name: 'og:url', content: 'https://Sphinxes0o0.github.io/notes/' }],
    ['meta', { name: 'twitter:card', content: 'summary_large_image' }],
    ['meta', { name: 'author', content: 'Sphinx' }],
    ['meta', { name: 'robots', content: 'index, follow' }]
  ],

  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config

    // Search configuration (local search)
    search: {
      provider: 'local',
      options: {
        detailedView: true,
        _render: renderSearchContent
      }
    },

    // Outline (table of contents)
    outline: {
      level: [2, 3],
      label: '目录'
    },

    // Edit link - allow users to edit page on GitHub
    editLink: {
      pattern: 'https://github.com/Sphinxes0o0/notes/edit/main/:path',
      text: '在 GitHub 上编辑此页'
    },

    // Doc footer (prev/next navigation)
    docFooter: {
      prev: '上一页',
      next: '下一页'
    },

    // Social links
    socialLinks: [
      { icon: 'github', link: 'https://github.com/Sphinxes0o0' }
    ],

    // Footer
    footer: {
      message: '基于 VitePress 构建',
      copyright: 'Copyright © 2024-present Sphinx'
    },

    // Last updated text
    lastUpdated: {
      text: '最后更新于',
      formatOptions: {
        dateStyle: 'short',
        timeStyle: 'short'
      }
    },

    // Nav
    nav: [
      { text: '首页', link: '/' },
      { text: 'C/C++', link: '/ccpp/' },
      { text: '系统', link: '/sys/' },
      { text: '内核', link: '/kernel/' },
      { text: '网络/协议', link: '/network/' },
      { text: '安全', link: '/security/' },
      { text: '工具', link: '/tools/' },
      { text: 'AI 编码 Agent', link: '/coding_agent/' },
      { text: '研究', link: '/research/' },
      {
        text: '课程',
        items: [
          { text: '数据结构', link: '/datastructure/' },
          { text: '设计模式', link: '/design_patterns/' },
          { text: '网络基础', link: '/network_fundamentals/' },
          { text: '操作系统基础', link: '/os_fundamentals/' }
        ]
      },
      { text: 'QEMU', link: '/qemu/' },
      { text: '面试', link: '/interview/' }
    ],

    sidebar
  }
})
