#!/usr/bin/env node

// Validate configured navigation against source pages, independently of ignoreDeadLinks.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import config from '../../.vitepress/config.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const excluded = config.srcExclude.map((pattern) => pattern.replace(/\/\*\*$/, '/'));
const issues = [];
let checked = 0;

function check(link, location) {
  if (!link || /^(?:[a-z][a-z\d+.-]*:|\/\/|#)/i.test(link)) return;
  checked++;
  let route;
  try {
    route = decodeURIComponent(link.split(/[?#]/)[0]).replace(/^\//, '');
  } catch {
    issues.push(`${location}: invalid URL ${link}`);
    return;
  }
  const stem = route.replace(/\.(?:html|md)$/, '').replace(/\/$/, '');
  const pages = stem ? [`${stem}.md`, `${stem}/index.md`] : ['index.md'];
  const candidates = [...pages, `public/${route}`];
  const found = candidates.some((candidate) => {
    const absolute = path.resolve(root, candidate);
    const relative = path.relative(root, absolute);
    if (relative.startsWith('..') || path.isAbsolute(relative)) return false;
    if (!candidate.startsWith('public/') && excluded.some((prefix) => candidate.startsWith(prefix))) return false;
    return fs.existsSync(absolute) && fs.statSync(absolute).isFile();
  });
  if (!found) issues.push(`${location}: ${link}`);
}

function walk(items, location) {
  for (const item of items) {
    check(item.link, `${location} / ${item.text}`);
    if (item.items) walk(item.items, `${location} / ${item.text}`);
  }
}

walk(config.themeConfig.nav, 'nav');
for (const [prefix, items] of Object.entries(config.themeConfig.sidebar)) {
  check(prefix, 'sidebar entry');
  walk(items, `sidebar ${prefix}`);
}

console.log(`Navigation audit: ${checked} local links, ${issues.length} broken.`);
for (const issue of issues) console.error(`  ${issue}`);
process.exitCode = issues.length ? 1 : 0;
