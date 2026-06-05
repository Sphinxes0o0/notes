#!/usr/bin/env node

/**
 * Audit / Inject frontmatter in markdown files.
 *
 * Modes:
 *   --audit   (default) Only report files missing frontmatter or missing title/description.
 *   --apply             Inject inferred title + description into files that have no frontmatter.
 *
 * Inference rules (apply mode):
 *   - title:       first H1 (`# ...`) in the file, else filename without extension.
 *   - description: first non-empty paragraph (or blockquote / list) that is not a heading and not a code block.
 *
 * Safety:
 *   - Apply mode NEVER overwrites existing frontmatter.
 *   - Apply mode preserves the original body verbatim.
 *   - Run from the repo root: `node .github/scripts/audit-frontmatter.js`
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const REPO_ROOT = path.resolve(__dirname, '..', '..');

const CONTENT_DIRS = [
  'ccpp', 'kernel', 'network', 'sys', 'security', 'tools', 'midware',
  'qemu', 'interview', 'datastructure', 'design_patterns',
  'network_fundamentals', 'os_fundamentals', 'coding_agent'
];

const MODE = process.argv.includes('--apply') ? 'apply' : 'audit';

function walkDir(dir) {
  const files = [];
  if (!fs.existsSync(dir)) return files;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.name === 'node_modules' || entry.name.startsWith('.')) continue;
    if (entry.isDirectory()) files.push(...walkDir(full));
    else if (entry.isFile() && entry.name.endsWith('.md')) files.push(full);
  }
  return files;
}

function parseFrontmatter(content) {
  if (!content.startsWith('---')) return { has: false, body: content, fm: null };
  const m = content.match(/^---\n([\s\S]*?)\n---\n?/);
  if (!m) return { has: false, body: content, fm: null };
  return { has: true, body: content.slice(m[0].length), fm: m[1] };
}

function fmHas(fm, key) {
  if (!fm) return false;
  return new RegExp(`^${key}\\s*:`, 'm').test(fm);
}

function inferTitle(filepath, body) {
  const h1 = body.match(/^#\s+(.+?)\s*$/m);
  if (h1) return h1[1].trim();
  return path.basename(filepath, '.md');
}

function inferDescription(body) {
  // Strip code fences first
  const stripped = body.replace(/```[\s\S]*?```/g, '');
  // Pick the first non-empty line that isn't a heading, list marker, or blockquote
  const lines = stripped.split('\n');
  for (const raw of lines) {
    const line = raw.trim();
    if (!line) continue;
    if (line.startsWith('#')) continue;
    if (line.startsWith('- ') || line.startsWith('* ') || /^\d+\.\s/.test(line)) continue;
    if (line.startsWith('>')) continue;
    if (line.startsWith('|')) continue; // table
    if (line.startsWith('!') || line.startsWith('[')) continue; // image/link-only
    if (line.length < 4) continue;
    // Truncate to 200 chars at a sentence boundary if possible
    const capped = line.length > 200 ? line.slice(0, 200).replace(/[,，;；\s]+[^\s,，;；]*$/, '') + '…' : line;
    return capped;
  }
  return '';
}

function escapeYamlString(s) {
  // Use double-quoted YAML; escape backslashes and double-quotes
  return '"' + s.replace(/\\/g, '\\\\').replace(/"/g, '\\"') + '"';
}

function buildFrontmatterBlock(title, description) {
  const lines = ['---'];
  lines.push(`title: ${escapeYamlString(title)}`);
  if (description) lines.push(`description: ${escapeYamlString(description)}`);
  lines.push('---');
  lines.push('');
  return lines.join('\n');
}

function main() {
  const files = CONTENT_DIRS.flatMap((d) => walkDir(path.join(REPO_ROOT, d)));
  const stats = { total: files.length, missing: [], noTitle: [], noDesc: [], injected: 0 };

  for (const f of files) {
    const content = fs.readFileSync(f, 'utf-8');
    const { has, body, fm } = parseFrontmatter(content);

    if (!has) {
      stats.missing.push(f);
      if (MODE === 'apply') {
        const title = inferTitle(f, body);
        const description = inferDescription(body);
        const newContent = buildFrontmatterBlock(title, description) + body;
        fs.writeFileSync(f, newContent, 'utf-8');
        stats.injected++;
      }
    } else {
      if (!fmHas(fm, 'title')) stats.noTitle.push(f);
      if (!fmHas(fm, 'description')) stats.noDesc.push(f);
    }
  }

  const rel = (p) => path.relative(REPO_ROOT, p);

  if (MODE === 'audit') {
    console.log(`[frontmatter audit] 模式: audit（只读，不会修改文件）\n`);
    console.log(`扫描目录: ${CONTENT_DIRS.length} 个`);
    console.log(`扫描文件: ${stats.total} 个 .md\n`);
    console.log(`  无 frontmatter:        ${stats.missing.length}`);
    console.log(`  有 frontmatter 无 title:    ${stats.noTitle.length}`);
    console.log(`  有 frontmatter 无 description: ${stats.noDesc.length}`);

    if (stats.missing.length) {
      console.log(`\n示例无 frontmatter 文件（最多 10 个）：`);
      for (const f of stats.missing.slice(0, 10)) console.log(`  - ${rel(f)}`);
    }
    if (stats.noTitle.length) {
      console.log(`\n示例无 title 文件（最多 10 个）：`);
      for (const f of stats.noTitle.slice(0, 10)) console.log(`  - ${rel(f)}`);
    }
    if (stats.noDesc.length) {
      console.log(`\n示例无 description 文件（最多 10 个）：`);
      for (const f of stats.noDesc.slice(0, 10)) console.log(`  - ${rel(f)}`);
    }
    console.log(`\n使用 --apply 参数可自动为无 frontmatter 文件注入 title + description。`);
  } else {
    console.log(`[frontmatter apply] 模式: apply（已写入）\n`);
    console.log(`扫描文件: ${stats.total} 个`);
    console.log(`新注入 frontmatter: ${stats.injected} 个`);
    console.log(`有 frontmatter 但无 title:   ${stats.noTitle.length}`);
    console.log(`有 frontmatter 但无 description: ${stats.noDesc.length}`);
    if (stats.noTitle.length) {
      console.log(`\n需要补 title 的文件：`);
      for (const f of stats.noTitle) console.log(`  - ${rel(f)}`);
    }
  }
}

main();
