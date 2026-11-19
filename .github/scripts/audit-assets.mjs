#!/usr/bin/env node
import fs from 'node:fs'
import path from 'node:path'
import { createHash } from 'node:crypto'
import { execFileSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..')
const baselinePath = path.join(root, '.github/pyramid-asset-baseline.json')
const baseline = fs.existsSync(baselinePath) ? JSON.parse(fs.readFileSync(baselinePath, 'utf8')).groups : {}
const files = execFileSync('git', ['-c', 'core.fsmonitor=false', 'ls-files', '-z'], { cwd: root }).toString().split('\0').filter(Boolean)
const groups = new Map()
let scanned = 0
for (const file of files) {
  if (!/\.(pdf|png|jpe?g|svg|webp)$/i.test(file) || !fs.existsSync(path.join(root, file))) continue
  const hash = createHash('sha256').update(fs.readFileSync(path.join(root, file))).digest('hex')
  if (!groups.has(hash)) groups.set(hash, [])
  groups.get(hash).push(file)
  scanned++
}
const duplicates = [...groups.entries()].filter(([, group]) => group.length > 1)
const unexpected = duplicates.filter(([hash, group]) =>
  JSON.stringify([...group].sort()) !== JSON.stringify(baseline[hash]))
console.log(`Asset audit: ${scanned} tracked assets, ${duplicates.length - unexpected.length} preserved import groups, ${unexpected.length} unexpected duplicate groups.`)
for (const [, group] of unexpected) console.error(group.join('\n'))
process.exitCode = unexpected.length ? 1 : 0
