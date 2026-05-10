#!/usr/bin/env node

/**
 * Audit Code Blocks in Markdown Files
 *
 * This script scans all markdown files in the notes/ directory and checks for:
 * a. Missing closing ``` backticks
 * b. Chinese text bleeding into code blocks
 * c. Invalid or missing language markers
 * d. Truncated code (code that ends abruptly with Chinese text)
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const REPO_ROOT = path.resolve(__dirname, '..', '..');
const NOTES_DIR = path.join(REPO_ROOT, 'notes');

// Chinese character range (common CJK Unified Ideographs)
const CHINESE_REGEX = /[一-鿿]/;

// Issues found during audit
const issues = [];

function walkDir(dir) {
  const files = [];

  if (!fs.existsSync(dir)) {
    return files;
  }

  const entries = fs.readdirSync(dir, { withFileTypes: true });

  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);

    // Skip node_modules and hidden directories
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
        // Opening fence
        inCodeBlock = true;
        blockStartLine = i + 1;
        language = line.slice(3).trim();
        codeLines = [];
      } else {
        // Closing fence
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

  // If still in code block, it's unclosed
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
      message: `Unclosed code block starting at line ${block.startLine} - missing closing \`\`\``
    });
  }

  // Check c: Invalid or missing language markers
  // A valid language marker should only contain alphanumeric characters, not Chinese or special chars
  if (block.language && CHINESE_REGEX.test(block.language)) {
    issues.push({
      file: filePath,
      line: block.startLine,
      type: 'INVALID_LANGUAGE_MARKER',
      message: `Code block at line ${block.startLine} has invalid language marker containing Chinese characters: "${block.language}"`
    });
  }

  // Check for empty language with potential issues
  if (block.lines.length > 0 && !block.language) {
    // Check if the first line looks like it should have a language marker
    const firstLine = block.lines[0].content;
    if (firstLine.match(/^[a-zA-Z]/) && !firstLine.match(/^\s/)) {
      // First line looks like it might be a language marker that got lost
    }
  }

  // Check b & d: Chinese text in code blocks and truncated code
  if (block.lines.length > 0) {
    const lastLine = block.lines[block.lines.length - 1];
    const content = lastLine.content;

    // Check d: Truncated code (ends with Chinese text)
    const trimmedContent = content.trim();
    if (trimmedContent && CHINESE_REGEX.test(trimmedContent)) {
      issues.push({
        file: filePath,
        line: lastLine.lineNumber,
        type: 'TRUNCATED_CODE',
        message: `Code block at line ${block.startLine} appears truncated - ends with Chinese text: "${trimmedContent}"`
      });
    }

    // Check b: Chinese characters inside code block (not just at end)
    for (const lineObj of block.lines) {
      // Skip the last line as it's handled by truncated code check
      if (lineObj === lastLine) continue;

      const lineContent = lineObj.content;
      // Check if there's Chinese text mixed with code (not just whitespace around it)
      if (CHINESE_REGEX.test(lineContent)) {
        issues.push({
          file: filePath,
          line: lineObj.lineNumber,
          type: 'CHINESE_IN_CODE_BLOCK',
          message: `Chinese text found inside code block at line ${lineObj.lineNumber}: "${lineContent.trim()}" `
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

  const files = walkDir(NOTES_DIR);
  console.log(`Found ${files.length} markdown files to audit.\n`);

  for (const file of files) {
    const relativePath = path.relative(REPO_ROOT, file);
    auditFile(file);
  }

  // Report results
  if (issues.length === 0) {
    console.log('No code block issues found.');
    process.exit(0);
  } else {
    console.log(`Found ${issues.length} issue(s):\n`);

    // Group issues by file
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
