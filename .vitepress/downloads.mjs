import fs from 'node:fs'
import path from 'node:path'

// Publish the source examples that documentation links to, without duplicating
// editable copies under public/. Only these example directories are exported.
export function writeSourceDownloads(config) {
  function walk(folder) {
    for (const item of fs.readdirSync(folder, { withFileTypes: true })) {
      const source = path.join(folder, item.name)
      if (item.isDirectory()) walk(source)
      else if (item.isFile() && (/\.(c|cc|cpp|h|hpp|py|rs)$/.test(item.name) || item.name === 'requirements.txt')) {
        const target = path.join(config.outDir, path.relative(config.srcDir, source))
        fs.mkdirSync(path.dirname(target), { recursive: true })
        fs.copyFileSync(source, target)
      }
    }
  }
  for (const relative of ['ccpp/concurrency', 'a2a/examples']) walk(path.join(config.srcDir, relative))
}
