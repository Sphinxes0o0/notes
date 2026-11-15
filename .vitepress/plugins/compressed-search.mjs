import { gzipSync } from 'node:zlib'
import { createHash } from 'node:crypto'

export function compressedSearchPlugin() {
  return {
    name: 'notes:compressed-search',
    apply: 'build',
    transform(code, id) {
      if (!id.startsWith('/@localSearchIndex') || !/^export default "/.test(code)) return
      const raw = JSON.parse(code.replace(/^export default /, ''))
      const hash = createHash('sha256').update(raw).digest('hex').slice(0, 12)
      const compressed = this.emitFile({ type: 'asset', fileName: `assets/search-index-${hash}.json.gz`, source: gzipSync(raw, { level: 9 }) })
      const fallback = this.emitFile({ type: 'asset', fileName: `assets/search-index-${hash}.json`, source: raw })
      return `export default (async () => {
        if (typeof DecompressionStream !== 'undefined') {
          try {
            const response = await fetch(import.meta.ROLLUP_FILE_URL_${compressed});
            if (!response.ok) throw new Error('Compressed search index unavailable');
            // Fetch transparently decodes servers that advertise Content-Encoding.
            if (response.headers.get('content-encoding')?.includes('gzip')) return response.text();
            return await new Response(response.body.pipeThrough(new DecompressionStream('gzip'))).text();
          } catch { /* Retry using the uncompressed index. */ }
        }
        const response = await fetch(import.meta.ROLLUP_FILE_URL_${fallback});
        if (!response.ok) throw new Error('Search index unavailable');
        return response.text();
      })();`
    }
  }
}
