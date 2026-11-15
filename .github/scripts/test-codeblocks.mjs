import assert from 'node:assert/strict'
import test from 'node:test'
import { findCodeBlocks } from './audit-codeblocks.js'

test('nested examples in longer fences remain a single complete block', () => {
  const blocks = findCodeBlocks('````markdown\n```js\nconst x = 1\n```\n````\n')
  assert.equal(blocks.length, 1)
  assert.equal(blocks[0].hasClosing, true)
})

test('tilde fences and indented closing markers are supported', () => {
  const blocks = findCodeBlocks('~~~text\nexample\n  ~~~\n')
  assert.equal(blocks.length, 1)
  assert.equal(blocks[0].hasClosing, true)
})

test('language-tagged markers cannot close a code fence', () => {
  const blocks = findCodeBlocks('```js\nconst x = 1\n```js\n')
  assert.equal(blocks[0].hasClosing, false)
})
