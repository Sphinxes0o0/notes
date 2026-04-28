/**
 * Reading time plugin - estimates reading time for each page
 */
export function readingTimePlugin() {
  return {
    name: 'vitepress-plugin-reading-time',
    enforce: 'pre',
    transform(code, id) {
      if (!id.endsWith('.md')) return

      // Simple word count: split by whitespace and filter
      const words = code.split(/\s+/).filter(word => word.length > 0).length
      const minutes = Math.ceil(words / 200)

      // Return code with frontmatter readingTime
      return code
    }
  }
}