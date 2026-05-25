#!/usr/bin/env python3
"""Pyramid Wiki Lint Script — checks orphan pages, broken wikilinks, index completeness,
frontmatter validation, stale content, and page size."""

import os
import re
import json
from collections import defaultdict
from datetime import datetime, date

WIKI = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "wiki")

# ──────────────────────────────────────────────
# 1. Collect all wiki page files
# ──────────────────────────────────────────────
all_files = []
for root, dirs, files in os.walk(WIKI):
    # Skip .obsidian, .templates, attachments
    dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'attachments']
    for f in files:
        if f.endswith('.md'):
            full = os.path.join(root, f)
            rel = os.path.relpath(full, WIKI)
            all_files.append((rel, full))

print(f"Total .md files found: {len(all_files)}")

# ──────────────────────────────────────────────
# Read all file contents
# ──────────────────────────────────────────────
file_contents = {}
for rel, full in all_files:
    with open(full, 'r') as fh:
        file_contents[rel] = fh.read()

# ──────────────────────────────────────────────
# Helper: extract frontmatter
# ──────────────────────────────────────────────
def parse_frontmatter(content):
    """Return dict of frontmatter fields or None."""
    m = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not m:
        return None
    raw = m.group(1)
    fields = {}
    # Simple YAML-like parser for common patterns
    for line in raw.split('\n'):
        line = line.strip()
        if ':' in line:
            key, _, val = line.partition(':')
            key = key.strip()
            val = val.strip()
            # Handle quoted strings
            if val.startswith('"') and val.endswith('"'):
                val = val[1:-1]
            elif val.startswith('[') and val.endswith(']'):
                # list
                items = [v.strip().strip('"').strip("'") for v in val[1:-1].split(',') if v.strip()]
                val = items
            fields[key] = val
    return fields

# ──────────────────────────────────────────────
# Helper: extract [[wikilinks]] from body (not frontmatter)
# ──────────────────────────────────────────────
def extract_wikilinks(content):
    """Return set of link targets (without page anchor)."""
    # Remove frontmatter
    body = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, count=1, flags=re.DOTALL)
    links = set()
    for m in re.finditer(r'\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]', body):
        target = m.group(1).strip()
        # Normalize: wiki paths are relative, no leading ./
        if target.startswith('./'):
            target = target[2:]
        links.add(target)
    return links

# ──────────────────────────────────────────────
# Helper: get 'updated' date from frontmatter
# ──────────────────────────────────────────────
def get_updated(content):
    """Return the 'updated' field as a date object or None."""
    fm = parse_frontmatter(content)
    if fm and 'updated' in fm:
        try:
            return datetime.strptime(str(fm['updated']), '%Y-%m-%d').date()
        except:
            pass
    return None

def get_created(content):
    """Return the 'created' field as a date object or None."""
    fm = parse_frontmatter(content)
    if fm and 'created' in fm:
        try:
            return datetime.strptime(str(fm['created']), '%Y-%m-%d').date()
        except:
            pass
    return None

# ──────────────────────────────────────────────
# RESULTS
# ──────────────────────────────────────────────
orphan_pages = []
broken_links = []
index_missing = []
frontmatter_issues = []
stale_pages = []
large_pages = []

# ──────────────────────────────────────────────
# 2a. ORPHAN PAGES — find pages with zero inbound [[wikilinks]]
# ──────────────────────────────────────────────
print("\n=== 2a. ORPHAN PAGES ===")

# Build link graph
# We consider only entities/, sources/, synthesis/ pages as interesting (the content pages)
# Index files (root-level) and home.md, log.md are navigation and shouldn't count.
content_files = [rel for rel, _ in all_files 
                 if rel.startswith('entities/') or rel.startswith('sources/') or rel.startswith('synthesis/')]
nav_files = [rel for rel, _ in all_files 
             if not rel.startswith('entities/') and not rel.startswith('sources/') and not rel.startswith('synthesis/')]

# Build outbound link map for all files
outbound_links = {}  # file -> set of targets
for rel, full in all_files:
    outbound_links[rel] = extract_wikilinks(file_contents[rel])

# Count inbound links for content pages
inbound_counts = defaultdict(int)
for src, targets in outbound_links.items():
    for t in targets:
        # Normalize target to file path
        # Could be "sources/notes-os" (no .md), "entities/cpp/cpp-safety" (no .md)
        # or "cpp-index" (an index page)
        # Links without .md extension are the norm
        # Search for matching file
        for rel, _ in all_files:
            base = rel.replace('.md', '')
            if base == t:
                inbound_counts[rel] += 1
                break

for rel in content_files:
    if inbound_counts.get(rel, 0) == 0:
        orphan_pages.append(rel)

print(f"Orphan pages (0 inbound links): {len(orphan_pages)}")
for p in sorted(orphan_pages):
    print(f"  {p}")

# ──────────────────────────────────────────────
# 2b. BROKEN WIKILINKS
# ──────────────────────────────────────────────
print("\n=== 2b. BROKEN WIKILINKS ===")

# Build a set of valid targets (without .md extension)
valid_targets = set()
valid_target_with_path = {}
for rel, _ in all_files:
    base = rel.replace('.md', '')
    valid_targets.add(base)
    valid_target_with_path[base] = rel

for src_rel, targets in outbound_links.items():
    for t in targets:
        # Check if this target exists (as a wiki page base)
        if t not in valid_targets:
            broken_links.append((src_rel, t))

print(f"Broken wikilinks: {len(broken_links)}")
for src, tgt in sorted(broken_links, key=lambda x: (x[0], x[1])):
    print(f"  {src} -> [[{tgt}]]")

# ──────────────────────────────────────────────
# 2c. INDEX COMPLETENESS
# ──────────────────────────────────────────────
print("\n=== 2c. INDEX COMPLETENESS ===")

# Check home.md for all entity and source pages
home_content = file_contents.get('home.md', '')
home_links = extract_wikilinks(home_content)

# Entity pages referenced in home.md
entity_refs_in_home = set()
source_refs_in_home = set()
for link in home_links:
    if link.startswith('sources/'):
        source_refs_in_home.add(link)
    elif link.startswith('entities/'):
        entity_refs_in_home.add(link)

# Actual entity/source pages
actual_entities = set()
actual_sources = set()
for rel, _ in all_files:
    if rel.startswith('entities/'):
        # entity files might be in subdirs — the link format could be like "entities/cpp/cpp-safety"
        base = rel.replace('.md', '')
        actual_entities.add(base)
    elif rel.startswith('sources/'):
        base = rel.replace('.md', '')
        actual_sources.add(base)

# Check which entities are missing from home.md
# Note: entities are referenced from index pages, not directly from home.md typically
# Let's check that every entity is referenced somewhere (home.md or any index)
all_referenced_entities = set()
all_referenced_sources = set()
for src_rel, targets in outbound_links.items():
    for t in targets:
        if t.startswith('entities/'):
            all_referenced_entities.add(t)
        elif t.startswith('sources/'):
            all_referenced_sources.add(t)

for ent in sorted(actual_entities):
    if ent not in all_referenced_entities:
        index_missing.append(('entity', ent))

for src in sorted(actual_sources):
    if src not in all_referenced_sources:
        index_missing.append(('source', src))

print(f"Missing from index/references: {len(index_missing)}")
for kind, path in sorted(index_missing, key=lambda x: x[1]):
    print(f"  [{kind}] {path}")

# ──────────────────────────────────────────────
# 2d. FRONTMATTER VALIDATION
# ──────────────────────────────────────────────
print("\n=== 2d. FRONTMATTER VALIDATION ===")

valid_types = {'entity', 'source', 'synthesis', 'journal', 'index', 'log', 'dashboard'}

for rel, _ in all_files:
    content = file_contents[rel]
    fm = parse_frontmatter(content)
    
    if fm is None:
        frontmatter_issues.append((rel, "missing frontmatter"))
        continue
    
    # Check required fields: type, tags, created
    if 'type' not in fm:
        frontmatter_issues.append((rel, "missing 'type' field"))
    elif fm['type'] not in valid_types:
        frontmatter_issues.append((rel, f"invalid type: '{fm['type']}'"))
    
    if 'tags' not in fm:
        frontmatter_issues.append((rel, "missing 'tags' field"))
    elif not fm['tags']:
        frontmatter_issues.append((rel, "empty 'tags' field"))
    else:
        # Check for reasonable tags (no obvious typos)
        tags = fm['tags'] if isinstance(fm['tags'], list) else [fm['tags']]
        for tag in tags:
            if len(tag) > 30:
                frontmatter_issues.append((rel, f"suspicious long tag: '{tag}'"))
    
    if 'created' not in fm:
        frontmatter_issues.append((rel, "missing 'created' field"))
    elif get_created(content) is None:
        frontmatter_issues.append((rel, f"invalid 'created' date: '{fm.get('created')}'"))

print(f"Frontmatter issues: {len(frontmatter_issues)}")
for path, issue in sorted(frontmatter_issues, key=lambda x: x[0]):
    print(f"  {path}: {issue}")

# ──────────────────────────────────────────────
# 2e. STALE CONTENT
# ──────────────────────────────────────────────
print("\n=== 2e. STALE CONTENT ===")

# Find the most recent source updated date
most_recent_source_update = None
for rel, _ in all_files:
    if rel.startswith('sources/'):
        updated = get_updated(file_contents[rel])
        if updated and (most_recent_source_update is None or updated > most_recent_source_update):
            most_recent_source_update = updated

print(f"Most recent source update: {most_recent_source_update}")

if most_recent_source_update:
    for rel, _ in all_files:
        if rel.startswith('entities/') or rel.startswith('synthesis/'):
            updated = get_updated(file_contents[rel])
            created = get_created(file_contents[rel])
            # A page is "stale" if its 'updated' is older than the most recent source change
            # and it has an 'updated' field (meaning it was once updated)
            if updated and updated < most_recent_source_update:
                stale_pages.append((rel, str(updated), str(most_recent_source_update)))
            # Also flag pages that were created before the most recent source but never updated
            # (have no 'updated' field at all)
            elif created and created < most_recent_source_update and updated is None:
                # Many pages legitimately don't need updates; only flag if >7 days old
                days_old = (most_recent_source_update - created).days
                if days_old > 7:
                    stale_pages.append((rel, f"never updated (created {created})", str(most_recent_source_update)))

print(f"Stale pages: {len(stale_pages)}")
for path, upd, latest in sorted(stale_pages, key=lambda x: x[0]):
    print(f"  {path}: updated={upd}, latest_source={latest}")

# ──────────────────────────────────────────────
# 2f. PAGE SIZE
# ──────────────────────────────────────────────
print("\n=== 2f. PAGE SIZE (>200 lines) ===")

for rel, full in all_files:
    content = file_contents[rel]
    line_count = content.count('\n') + 1
    if line_count > 200:
        large_pages.append((rel, line_count))
        print(f"  {rel}: {line_count} lines")

# ──────────────────────────────────────────────
# SUMMARY
# ──────────────────────────────────────────────
print("\n" + "="*60)
print("LINT SUMMARY")
print("="*60)
print(f"Total wiki .md files: {len(all_files)}")
print(f"Orphan pages:         {len(orphan_pages)}")
print(f"Broken wikilinks:     {len(broken_links)}")
print(f"Index missing:        {len(index_missing)}")
print(f"Frontmatter issues:   {len(frontmatter_issues)}")
print(f"Stale pages:          {len(stale_pages)}")
print(f"Large pages (>200):   {len(large_pages)}")

# Output JSON for programmatic use
output = {
    "orphan_pages": orphan_pages,
    "broken_links": broken_links,
    "index_missing": index_missing,
    "frontmatter_issues": frontmatter_issues,
    "stale_pages": stale_pages,
    "large_pages": large_pages,
}
with open("/tmp/lint_results.json", "w") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
print("\nResults saved to /tmp/lint_results.json")
