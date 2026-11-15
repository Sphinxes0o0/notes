import assert from 'node:assert/strict'
import test from 'node:test'
import { createMarkdownRenderer } from 'vitepress'
import { renderSearchContent } from '../../.vitepress/search.mjs'

const md = await createMarkdownRenderer(process.cwd(), { lineNumbers: true })

test('search retains prose, code identifiers and headings without generated controls', async () => {
  const source = '# Heading\n\n检索正文\n\n```cpp\nint unique_function() { return 42; }\n```\n'
  const original = await md.renderAsync(source, {})
  assert.match(original, /line-numbers-wrapper/)
  const indexed = await renderSearchContent(source, {}, md)
  assert.match(indexed, /检索正文/)
  assert.match(indexed, /unique_function/)
  assert.match(indexed, /id="heading"/)
  assert.match(indexed, /class="header-anchor" href="#heading"/)
  assert.doesNotMatch(indexed, /line-numbers-wrapper|class="copy"|class="lang"/)
})

test('search opt-out frontmatter remains effective', async () => {
  const indexed = await renderSearchContent('---\nsearch: false\n---\n\n# Private heading\n', {}, md)
  assert.equal(indexed, '')
})
