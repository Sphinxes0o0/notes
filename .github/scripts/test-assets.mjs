import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { execFileSync, spawnSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { fileURLToPath } from 'node:url'

const script = fileURLToPath(new URL('./audit-assets.mjs', import.meta.url))

function fixture(t) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'notes-assets-'))
  t.after(() => fs.rmSync(root, { recursive: true, force: true }))
  fs.mkdirSync(path.join(root, '.github/scripts'), { recursive: true })
  fs.copyFileSync(script, path.join(root, '.github/scripts/audit-assets.mjs'))
  execFileSync('git', ['init', '-q', root])
  const files = ['one.svg', 'two.svg']
  const bytes = '<svg>preserved import</svg>'
  for (const file of files) fs.writeFileSync(path.join(root, file), bytes)
  const hash = createHash('sha256').update(bytes).digest('hex')
  fs.writeFileSync(path.join(root, '.github/pyramid-asset-baseline.json'), JSON.stringify({ groups: { [hash]: files } }))
  return {
    root,
    run() {
      execFileSync('git', ['-C', root, 'add', '.'])
      return spawnSync(process.execPath, [path.join(root, '.github/scripts/audit-assets.mjs')], { encoding: 'utf8' })
    }
  }
}

test('preserved duplicate assets require the exact bytes and path set', (t) => {
  const f = fixture(t)
  assert.equal(f.run().status, 0)
})

test('a new duplicate path is rejected even for a known import hash', (t) => {
  const f = fixture(t)
  fs.copyFileSync(path.join(f.root, 'one.svg'), path.join(f.root, 'three.svg'))
  assert.equal(f.run().status, 1)
})

test('different duplicated bytes cannot reuse an import exemption', (t) => {
  const f = fixture(t)
  for (const name of ['one.svg', 'two.svg']) fs.writeFileSync(path.join(f.root, name), '<svg>new bytes</svg>')
  assert.equal(f.run().status, 1)
})
