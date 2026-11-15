import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { writeSourceDownloads } from '../../.vitepress/downloads.mjs'

test('only example source files are published, keeping their documented paths', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'notes-downloads-'))
  try {
    for (const dir of ['ccpp/concurrency/future', 'a2a/examples']) fs.mkdirSync(path.join(root, dir), { recursive: true })
    fs.writeFileSync(path.join(root, 'ccpp/concurrency/future/example.cc'), 'int main() {}')
    fs.writeFileSync(path.join(root, 'a2a/examples/example.py'), 'print("example")')
    fs.writeFileSync(path.join(root, 'a2a/examples/.env'), 'private fixture')
    const outDir = path.join(root, 'dist')
    writeSourceDownloads({ srcDir: root, outDir })
    assert.equal(fs.readFileSync(path.join(outDir, 'ccpp/concurrency/future/example.cc'), 'utf8'), 'int main() {}')
    assert.ok(fs.existsSync(path.join(outDir, 'a2a/examples/example.py')))
    assert.ok(!fs.existsSync(path.join(outDir, 'a2a/examples/.env')))
  } finally {
    fs.rmSync(root, { recursive: true, force: true })
  }
})
