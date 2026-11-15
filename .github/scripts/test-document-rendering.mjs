import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import { createMarkdownRenderer } from 'vitepress'

const md = await createMarkdownRenderer(process.cwd())

test('vSOMEIP Plugin documentation is prose, not an accidental code block', () => {
  const tokens = md.parse(fs.readFileSync('midware/someip/vsomeip.md', 'utf8'), {})
  assert.ok(tokens.some((token, i) => token.type === 'heading_open' && tokens[i + 1].content === 'Plugin 系统'))
  assert.ok(!tokens.some((token) => token.type === 'fence' && !token.info && /### Plugin 系统/.test(token.content)))
})

test('nested SKILL example preserves both shell fences and subsequent documentation', () => {
  const tokens = md.parse(fs.readFileSync('coding_agent/pi-agent-custom-workflow.md', 'utf8'), {})
  assert.ok(tokens.some((token) => token.type === 'fence' && token.info === 'markdown' && token.content.includes('## Setup') && token.content.includes('## Usage')))
  assert.ok(tokens.some((token, i) => token.type === 'heading_open' && tokens[i + 1].content.startsWith('3.2 Prompt Templates')))
})
