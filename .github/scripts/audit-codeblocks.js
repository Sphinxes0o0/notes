#!/usr/bin/env node

/**
 * Audit Code Blocks in Markdown Files
 *
 * Checks for:
 * a. Missing closing backticks (unclosed code blocks)
 * b. Invalid language markers containing Chinese characters
 * c. Content bleeding - markdown text that got mixed into code blocks
 *
 * Note: Chinese comments, Chinese in diagrams, Chinese in strings are all valid
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const REPO_ROOT = path.resolve(__dirname, '..', '..');

const CONTENT_DIRS = [
  'ccpp', 'network', 'sys', 'midware', 'tools', 'kernel',
  'security', 'qemu', 'datastructure', 'design_patterns',
  'network_fundamentals', 'os_fundamentals', 'os', 'net',
  'netfilter', 'mm', 'io_uring', 'ipc', 'locking', 'lib',
  'crypto', 'block', 'sched', 'rcu', 'time', 'vfs', 'sound',
  'virt', 'openbmc'
];

const CHINESE_REGEX = /[一-鿿]/;

const issues = [];

function walkDir(dir) {
  const files = [];

  if (!fs.existsSync(dir)) {
    return files;
  }

  const entries = fs.readdirSync(dir, { withFileTypes: true });

  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);

    if (entry.name === 'node_modules' || entry.name.startsWith('.')) {
      continue;
    }

    if (entry.isDirectory()) {
      files.push(...walkDir(fullPath));
    } else if (entry.isFile() && entry.name.endsWith('.md')) {
      files.push(fullPath);
    }
  }

  return files;
}

/**
 * Check if a line is content bleeding (markdown text mixed into code).
 *
 * Only flags lines that are clearly broken/truncated prose.
 * Diagram labels, comments, tables are all valid.
 */
function isContentBleeding(line, language) {
  const trimmed = line.trim();
  if (!trimmed || !CHINESE_REGEX.test(trimmed)) {
    return false;
  }

  // If language is mermaid, skip
  if (language === 'mermaid') {
    return false;
  }

  // If line starts with comment markers, it's a comment (valid)
  if (/^\s*(\/\/|#|\/\*|\*)/.test(trimmed)) {
    return false;
  }

  // If line has code-like structure, it's valid code
  if (/[;{}()\[\]|]/.test(trimmed)) {
    return false;
  }

  // If line ends with Chinese punctuation (。！？) and has no code structure
  // and looks like a sentence fragment - this is likely bleeding
  if (/[。！？]$/.test(trimmed) && !/[=+\-*/<>]/.test(trimmed)) {
    return true;
  }

  return false;
}

function findCodeBlocks(content) {
  const blocks = [];
  const lines = content.split('\n');

  let inCodeBlock = false;
  let blockStartLine = 0;
  let language = '';
  let codeLines = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    if (line.startsWith('```')) {
      if (!inCodeBlock) {
        inCodeBlock = true;
        blockStartLine = i + 1;
        language = line.slice(3).trim();
        codeLines = [];
      } else {
        blocks.push({
          startLine: blockStartLine,
          endLine: i + 1,
          language: language,
          lines: codeLines,
          hasClosing: true
        });
        inCodeBlock = false;
        codeLines = [];
        language = '';
      }
    } else if (inCodeBlock) {
      codeLines.push({ lineNumber: i + 1, content: line });
    }
  }

  if (inCodeBlock) {
    blocks.push({
      startLine: blockStartLine,
      endLine: lines.length,
      language: language,
      lines: codeLines,
      hasClosing: false
    });
  }

  return blocks;
}

function checkCodeBlock(block, filePath) {
  // Check a: Missing closing backticks
  if (!block.hasClosing) {
    issues.push({
      file: filePath,
      line: block.startLine,
      type: 'UNCLOSED_CODE_BLOCK',
      message: `Unclosed code block starting at line ${block.startLine} - missing closing`
    });
  }

  // Check b: Invalid language markers
  if (block.language && CHINESE_REGEX.test(block.language)) {
    issues.push({
      file: filePath,
      line: block.startLine,
      type: 'INVALID_LANGUAGE_MARKER',
      message: `Invalid language marker containing Chinese: "${block.language}"`
    });
  }

  // Check c: Content bleeding
  if (block.lines.length > 0) {
    for (const lineObj of block.lines) {
      if (isContentBleeding(lineObj.content, block.language)) {
        issues.push({
          file: filePath,
          line: lineObj.lineNumber,
          type: 'CONTENT_BLEEDING',
          message: `Markdown text appears to be inside code block at line ${lineObj.lineNumber}: "${lineObj.content.trim().substring(0, 50)}"`
        });
      }
    }
  }
}

function auditFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const blocks = findCodeBlocks(content);

  for (const block of blocks) {
    checkCodeBlock(block, filePath);
  }
}

function main() {
  console.log('Auditing code blocks in markdown files...\n');

  const files = [];
  for (const dir of CONTENT_DIRS) {
    const fullPath = path.join(REPO_ROOT, dir);
    files.push(...walkDir(fullPath));
  }
  console.log(`Found ${files.length} markdown files to audit.\n`);

  for (const file of files) {
    auditFile(file);
  }

  if (issues.length === 0) {
    console.log('No code block issues found.');
    process.exit(0);
  } else {
    console.log(`Found ${issues.length} issue(s):\n`);

    const issuesByFile = {};
    for (const issue of issues) {
      if (!issuesByFile[issue.file]) {
        issuesByFile[issue.file] = [];
      }
      issuesByFile[issue.file].push(issue);
    }

    for (const [file, fileIssues] of Object.entries(issuesByFile)) {
      const relativePath = path.relative(REPO_ROOT, file);
      console.log(`${relativePath}:`);
      for (const issue of fileIssues) {
        console.log(`  Line ${issue.line}: [${issue.type}] ${issue.message}`);
      }
      console.log('');
    }

    process.exit(1);
  }
}

main();
