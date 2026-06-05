/**
 * Reading time plugin - estimates reading time for each page and
 * injects it into the page's frontmatter as `readingTime: N` (minutes).
 *
 * Heuristics:
 *   - Count CJK characters at ~400 chars/min
 *   - Count Latin words at ~200 words/min
 *   - Always round up, minimum 1 minute
 *
 * Usage:
 *   - Available in markdown as `{{ $frontmatter.readingTime }}` minutes
 *   - Available on page data as `pageData.readingTime`
 *   - Skip re-calculation if frontmatter already declares `readingTime:`
 */
export function readingTimePlugin() {
  return {
    name: 'vitepress-plugin-reading-time',
    enforce: 'pre',

    transform(code, id) {
      if (!id.endsWith('.md')) return
      if (!code.startsWith('---')) return // no frontmatter; skip (bulk-injector handles these)

      // Match the leading frontmatter block: ---\n...\n---
      const fmMatch = code.match(/^---\n([\s\S]*?)\n---/)
      if (!fmMatch) return

      const fmBody = fmMatch[1]
      // Respect an explicit override
      if (/^\s*readingTime\s*:/m.test(fmBody)) return

      const cjkChars = (code.match(/[一-鿿]/g) || []).length
      // Latin words: replace CJK runs with spaces, then split, keep words starting with A-Za-z
      const latinWords = code
        .replace(/[一-鿿]/g, ' ')
        .split(/\s+/)
        .filter((w) => /^[A-Za-z]/.test(w)).length

      const minutes = Math.max(1, Math.ceil(cjkChars / 400 + latinWords / 200))

      const newFmBody = `${fmBody}\nreadingTime: ${minutes}`
      return code.replace(fmMatch[0], `---\n${newFmBody}\n---`)
    },

    // Expose reading time on the parsed page data so layouts / components can read it
    transformPageData(pageData) {
      const fm = pageData.frontmatter
      if (fm && typeof fm.readingTime === 'number') {
        pageData.readingTime = fm.readingTime
      }
    },
  }
}
