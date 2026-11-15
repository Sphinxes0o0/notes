import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import MiniSearch from 'minisearch'
import { asyncSearchPlugin } from '../../.vitepress/plugins/async-search.mjs'

test('the installed VitePress search component uses asynchronous restoration', () => {
  const id = 'node_modules/vitepress/dist/client/theme-default/components/VPLocalSearchBox.vue'
  const output = asyncSearchPlugin().transform(fs.readFileSync(id, 'utf8'), id)
  assert.match(output, /markRaw\(\s*await MiniSearch.loadJSONAsync/)
  assert.throws(() => asyncSearchPlugin().transform('changed component', id), /loader changed/)
})

test('asynchronous restoration preserves full-text and code search results', async () => {
  const options = { fields: ['title', 'text'], storeFields: ['title'] }
  const original = new MiniSearch(options)
  original.addAll([{ id: 'one', title: '内核机制', text: 'DetectionEngine packets' }, { id: 'two', title: '数组操作', text: 'vector insert' }])
  const json = JSON.stringify(original)
  const restored = await MiniSearch.loadJSONAsync(json, options)
  for (const query of ['DetectionEngine', '内核机制', 'vector']) assert.deepEqual(restored.search(query), original.search(query))
})
