#!/usr/bin/env node

import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import MiniSearch from 'minisearch'
import { gunzipSync } from 'node:zlib'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..')
const assets = path.join(root, '.vitepress/dist/assets')
const chunks = assets
const indexes = fs.readdirSync(chunks).filter((name) => name.startsWith('search-index-') && name.endsWith('.json.gz'))
assert.ok(indexes.length, 'No generated search index; run npm run docs:build first')

for (const file of indexes) {
  const compressed = fs.readFileSync(path.join(chunks, file))
  const raw = gunzipSync(compressed).toString()
  assert.equal(raw, fs.readFileSync(path.join(chunks, file.slice(0, -3)), 'utf8'), 'Compressed index and fallback differ')
  console.log(`Compressed search payload: ${(compressed.length / 1024 / 1024).toFixed(2)} MiB`)
  const data = JSON.parse(raw)
  assert.ok(data.documentCount > 0 && data.index.length > 0, `${file}: search index is empty`)
  const search = MiniSearch.loadJSON(raw, {
    fields: ['title', 'titles', 'text'],
    storeFields: ['title', 'titles']
  })
  const results = search.search('DetectionEngine', { prefix: true })
  assert.ok(results.some((result) => result.id.includes('/security/nids/snort3/')), 'Snort code identifiers are missing from search')
  console.log(`Search audit: ${data.documentCount} sections, ${data.index.length} terms, ${(Buffer.byteLength(raw) / 1024 / 1024).toFixed(2)} MiB; Snort query passed.`)
}
