import test from 'node:test'
import assert from 'node:assert/strict'
import { compressedSearchPlugin } from '../../.vitepress/plugins/compressed-search.mjs'

function loader(raw) {
  const files = []
  const context = { emitFile: (file) => { files.push(file); return String(files.length - 1) } }
  const code = compressedSearchPlugin().transform.call(context, `export default ${JSON.stringify(raw)}`, '/@localSearchIndexroot')
  const executable = code.replace('export default ', 'return ').replace(/import.meta.ROLLUP_FILE_URL_(\d+)/g, '"$1"')
  return { files, load: (fetcher, decoder) => new Function('fetch', 'DecompressionStream', 'Response', executable)(fetcher, decoder, Response) }
}

test('compressed search retains every byte and uses the compressed resource', async () => {
  const raw = JSON.stringify({ text: '中文 DetectionEngine '.repeat(1000) })
  const { files, load } = loader(raw)
  const calls = []
  const result = await load(async (id) => { calls.push(id); return new Response(files[Number(id)].source) }, DecompressionStream)
  assert.equal(result, raw)
  assert.deepEqual(calls, ['0'])
  assert.ok(files[0].source.length < Buffer.byteLength(raw) / 2)
})

test('browsers without decompression and failed compressed requests use the full fallback', async () => {
  const raw = '{"text":"full source preserved"}'
  const { files, load } = loader(raw)
  assert.equal(await load(async (id) => new Response(files[Number(id)].source), undefined), raw)
  assert.equal(await load(async (id) => id === '0' ? new Response('', { status: 404 }) : new Response(raw), DecompressionStream), raw)
})


test('server-advertised gzip is already decoded by fetch and must not be decoded twice', async () => {
  const raw = '{"text":"transparent HTTP decompression"}'
  const { load } = loader(raw)
  const calls = []
  const result = await load(async (id) => { calls.push(id); return new Response(raw, { headers: { 'content-encoding': 'gzip' } }) }, DecompressionStream)
  assert.equal(result, raw)
  assert.deepEqual(calls, ['0'])
})
