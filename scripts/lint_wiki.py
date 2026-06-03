#!/usr/bin/env python3
"""Pyramid Wiki Lint Script — checks orphan pages, broken wikilinks, index completeness,
frontmatter validation, stale content, and page size.

Usage:
  python3 scripts/lint_wiki.py                  # default text output
  python3 scripts/lint_wiki.py --json           # full JSON results to /tmp/lint_results.json
  python3 scripts/lint_wiki.py --csv            # CSV report (broken_links.csv, orphans.csv, etc.)
  python3 scripts/lint_wiki.py --bucket-stats   # group by namespace (entities/cpp/... vs linux/...)
  python3 scripts/lint_wiki.py --ignore raw/    # exclude raw/ from lint (raw/ is source data)
  python3 scripts/lint_wiki.py --fix-stub       # auto-generate 10-line stub for orphan entity pages
"""

import os
import re
import sys
import json
import csv
import argparse
from collections import defaultdict, Counter
from datetime import datetime, date

# ──────────────────────────────────────────────
# Argument parsing
# ──────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Pyramid wiki lint")
parser.add_argument("--json", action="store_true", help="write full JSON to /tmp/lint_results.json")
parser.add_argument("--csv", action="store_true", help="write CSV reports to /tmp/lint_*.csv")
parser.add_argument("--bucket-stats", action="store_true", help="group broken/orphans by top-level namespace")
parser.add_argument("--ignore", action="append", default=[], help="path prefix to ignore (e.g. raw/)")
parser.add_argument("--fix-stub", action="store_true", help="auto-generate stub for orphan entity pages")
parser.add_argument("--quiet", action="store_true", help="suppress text output (still writes JSON/CSV if requested)")
args = parser.parse_args()

WIKI = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "wiki")

# ──────────────────────────────────────────────
# 1. Collect all wiki page files (with --ignore filter)
# ──────────────────────────────────────────────
def is_ignored(rel):
    for prefix in args.ignore:
        if rel.startswith(prefix):
            return True
    return False

all_files = []
for root, dirs, files in os.walk(WIKI):
    # Skip .obsidian, .templates, attachments
    dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'attachments']
    for f in files:
        if f.endswith('.md'):
            full = os.path.join(root, f)
            rel = os.path.relpath(full, WIKI)
            if not is_ignored(rel):
                all_files.append((rel, full))

if not args.quiet:
    print(f"Total .md files found: {len(all_files)}", end="")
    if args.ignore:
        print(f" (ignored prefixes: {', '.join(args.ignore)})")
    else:
        print()

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
    for line in raw.split('\n'):
        line = line.strip()
        if ':' in line:
            key, _, val = line.partition(':')
            key = key.strip()
            val = val.strip()
            if val.startswith('"') and val.endswith('"'):
                val = val[1:-1]
            elif val.startswith('[') and val.endswith(']'):
                items = [v.strip().strip('"').strip("'") for v in val[1:-1].split(',') if v.strip()]
                val = items
            fields[key] = val
    return fields

# ──────────────────────────────────────────────
# Helper: extract [[wikilinks]] from body
# ──────────────────────────────────────────────
def extract_wikilinks(content):
    body = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, count=1, flags=re.DOTALL)
    links = set()
    for m in re.finditer(r'\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]', body):
        target = m.group(1).strip()
        if target.startswith('./'):
            target = target[2:]
        links.add(target)
    return links

def get_updated(content):
    fm = parse_frontmatter(content)
    if fm and 'updated' in fm:
        try:
            return datetime.strptime(str(fm['updated']), '%Y-%m-%d').date()
        except:
            pass
    return None

def get_created(content):
    fm = parse_frontmatter(content)
    if fm and 'created' in fm:
        try:
            return datetime.strptime(str(fm['created']), '%Y-%m-%d').date()
        except:
            pass
    return None

# ──────────────────────────────────────────────
# Helpers: bucket analysis
# ──────────────────────────────────────────────
def bucket_for(rel):
    """Return top-level bucket for a wiki file path, e.g. 'entities/cpp', 'sources', 'synthesis'."""
    parts = rel.split('/')
    if len(parts) >= 2 and parts[0] in ('entities', 'sources', 'synthesis', 'temporal', 'indexes'):
        if parts[0] == 'entities' and len(parts) >= 2:
            return f"{parts[0]}/{parts[1]}"
        return parts[0]
    return parts[0] if parts else '(root)'

# ──────────────────────────────────────────────
# RESULTS
# ──────────────────────────────────────────────
orphan_pages = []           # list of rel paths
broken_links = []           # list of (src, target) tuples
index_missing = []          # list of (kind, path) tuples
frontmatter_issues = []     # list of (rel, issue_str) tuples
stale_pages = []
large_pages = []
fuzzy_resolved = []         # list of (src, target, resolved_path, kind) tuples

# Build outbound link map
outbound_links = {}
for rel, full in all_files:
    outbound_links[rel] = extract_wikilinks(file_contents[rel])

# ──────────────────────────────────────────────
# 2a. ORPHAN PAGES
# ──────────────────────────────────────────────
content_files = [rel for rel, _ in all_files
                 if rel.startswith('entities/') or rel.startswith('sources/') or rel.startswith('synthesis/')]

# Build inbound counts
inbound_counts = defaultdict(int)
for src, targets in outbound_links.items():
    for t in targets:
        for rel, _ in all_files:
            base = rel.replace('.md', '')
            if base == t:
                inbound_counts[rel] += 1
                break

for rel in content_files:
    if inbound_counts.get(rel, 0) == 0:
        orphan_pages.append(rel)

# ──────────────────────────────────────────────
# 2b. BROKEN WIKILINKS (with fuzzy basename + legacy wiki/ prefix)
# ──────────────────────────────────────────────
valid_targets = set()
valid_target_with_path = {}
basename_index = {}
for rel, _ in all_files:
    base = rel.replace('.md', '')
    valid_targets.add(base)
    valid_target_with_path[base] = rel
    bn = os.path.basename(base)
    if bn not in basename_index or len(rel) < len(basename_index[bn]):
        basename_index[bn] = rel

def resolve_target(t):
    if t in valid_targets:
        return ("exact", t)
    if t.startswith("wiki/"):
        stripped = t[5:]
        if stripped in valid_targets:
            return ("legacy_prefix", stripped)
    if t in basename_index:
        return ("fuzzy", basename_index[t])
    return None

for src_rel, targets in outbound_links.items():
    for t in targets:
        res = resolve_target(t)
        if res is None:
            broken_links.append((src_rel, t))
        elif res[0] == "exact":
            pass
        else:
            fuzzy_resolved.append((src_rel, t, res[1], res[0]))

# ──────────────────────────────────────────────
# 2c. INDEX COMPLETENESS
# ──────────────────────────────────────────────
all_referenced_entities = set()
all_referenced_sources = set()
for src_rel, targets in outbound_links.items():
    for t in targets:
        if t.startswith('entities/'):
            all_referenced_entities.add(t)
        elif t.startswith('sources/'):
            all_referenced_sources.add(t)

actual_entities = set()
actual_sources = set()
for rel, _ in all_files:
    if rel.startswith('entities/'):
        actual_entities.add(rel.replace('.md', ''))
    elif rel.startswith('sources/'):
        actual_sources.add(rel.replace('.md', ''))

for ent in sorted(actual_entities):
    if ent not in all_referenced_entities:
        index_missing.append(('entity', ent))
for src in sorted(actual_sources):
    if src not in all_referenced_sources:
        index_missing.append(('source', src))

# ──────────────────────────────────────────────
# 2d. FRONTMATTER VALIDATION (with detailed categorization)
# ──────────────────────────────────────────────
valid_types = {'entity', 'source', 'synthesis', 'journal', 'index', 'log', 'dashboard'}

for rel, _ in all_files:
    content = file_contents[rel]
    fm = parse_frontmatter(content)

    if fm is None:
        frontmatter_issues.append((rel, "missing frontmatter"))
        continue

    if 'type' not in fm:
        frontmatter_issues.append((rel, "missing 'type' field"))
    elif fm['type'] not in valid_types:
        frontmatter_issues.append((rel, f"invalid type: '{fm['type']}'"))

    if 'tags' not in fm:
        frontmatter_issues.append((rel, "missing 'tags' field"))
    elif not fm['tags']:
        frontmatter_issues.append((rel, "empty 'tags' field"))
    else:
        tags = fm['tags'] if isinstance(fm['tags'], list) else [fm['tags']]
        for tag in tags:
            if len(tag) > 30:
                frontmatter_issues.append((rel, f"suspicious long tag: '{tag}'"))

    if 'created' not in fm:
        frontmatter_issues.append((rel, "missing 'created' field"))
    elif get_created(content) is None:
        frontmatter_issues.append((rel, f"invalid 'created' date: '{fm.get('created')}'"))

    if 'updated' in fm and get_updated(content) is None:
        frontmatter_issues.append((rel, f"invalid 'updated' date: '{fm.get('updated')}'"))

# ──────────────────────────────────────────────
# 2e. STALE CONTENT
# ──────────────────────────────────────────────
most_recent_source_update = None
for rel, _ in all_files:
    if rel.startswith('sources/'):
        updated = get_updated(file_contents[rel])
        if updated and (most_recent_source_update is None or updated > most_recent_source_update):
            most_recent_source_update = updated

if most_recent_source_update:
    for rel, _ in all_files:
        if rel.startswith('entities/') or rel.startswith('synthesis/'):
            updated = get_updated(file_contents[rel])
            created = get_created(file_contents[rel])
            if updated and updated < most_recent_source_update:
                stale_pages.append((rel, str(updated), str(most_recent_source_update)))
            elif created and created < most_recent_source_update and updated is None:
                days_old = (most_recent_source_update - created).days
                if days_old > 7:
                    stale_pages.append((rel, f"never updated (created {created})", str(most_recent_source_update)))

# ──────────────────────────────────────────────
# 2f. PAGE SIZE
# ──────────────────────────────────────────────
for rel, full in all_files:
    content = file_contents[rel]
    line_count = content.count('\n') + 1
    if line_count > 200:
        large_pages.append((rel, line_count))

# ──────────────────────────────────────────────
# --fix-stub: generate 10-line stub for orphan entity pages AND
#             short-name broken targets that don't exist
# ──────────────────────────────────────────────
def _stub_content(slug, today):
    return f"""---
type: entity
tags: [stub, needs-content]
created: {today}
status: stub
---

# {slug}

> ⚠️ This is a placeholder stub generated by `lint_wiki.py --fix-stub`.
> Either:
> (a) a wiki page was referenced by an index but didn't exist, or
> (b) a short-name wikilink (e.g. `[[{slug}]]`) didn't resolve to any file.
> Fill in real content here, then remove `status: stub` from frontmatter.

## Definition
TODO: one-sentence definition.

## Key points
- TODO

## Related pages
- TODO (add `[[wikilinks]]` here)

## Sources
- TODO
"""

stubs_created = []
if args.fix_stub:
    today = date.today().isoformat()

    # 1) Orphans that don't have a file (rare — most orphans are existing files
    #    with no inbound links). Skip if file exists.
    for orphan_rel in orphan_pages:
        if not orphan_rel.startswith('entities/'):
            continue
        full_path = os.path.join(WIKI, orphan_rel)
        if os.path.exists(full_path):
            continue  # orphan file exists, not our problem to stub
        slug = os.path.basename(orphan_rel).replace('.md', '')
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(_stub_content(slug, today))
        stubs_created.append(orphan_rel)

    # 2) Short-name broken targets that don't resolve to any existing file.
    #    These are the most common fixable broken-link case (e.g. [[Adapter]]
    #    referencing a non-existent design-pattern page).
    #    Place stubs in entities/ root, then user can move to right namespace.
    unresolved_short_targets = set()
    for src, t in broken_links:
        if '/' not in t:  # short name only
            if not is_ignored(t + '.md'):  # don't stub ignored paths
                # Check if any existing file has this basename
                if t not in basename_index:
                    unresolved_short_targets.add(t)
    for short_t in sorted(unresolved_short_targets):
        # Sanity check: only stub if name looks like a real wiki slug
        # (alphanumerics, spaces, hyphens, underscores). Reject if it contains
        # control chars, pipes, brackets, newlines, or other markdown/code markers.
        if not re.match(r'^[A-Za-z0-9][A-Za-z0-9 _-]{0,60}$', short_t):
            continue  # skip snort rules, code excerpts, etc.
        # Try a few common slugs
        candidate_paths = [
            f"entities/{short_t}.md",
            f"entities/{short_t.lower()}.md",
            f"entities/topics/{short_t}.md",
        ]
        # Use the first candidate that doesn't exist
        target_rel = None
        for cp in candidate_paths:
            if not os.path.exists(os.path.join(WIKI, cp)):
                target_rel = cp
                break
        if not target_rel:
            continue
        full_path = os.path.join(WIKI, target_rel)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(_stub_content(short_t, today))
        stubs_created.append(target_rel)

# ──────────────────────────────────────────────
# --bucket-stats: aggregate by namespace
# ──────────────────────────────────────────────
def bucket_stats(items, key_fn):
    """Return Counter of buckets → count."""
    c = Counter()
    for it in items:
        c[key_fn(it)] += 1
    return c

bucket_broken = bucket_stats(broken_links, lambda x: bucket_for(x[0]))
bucket_orphans = bucket_stats(orphan_pages, bucket_for)
bucket_fm = bucket_stats(frontmatter_issues, lambda x: bucket_for(x[0]))

# Categorize frontmatter issues for granularity
fm_category_counter = Counter()
for rel, issue in frontmatter_issues:
    if 'missing frontmatter' in issue:
        fm_category_counter['missing'] += 1
    elif 'missing ' in issue:
        fm_category_counter[issue.split("'")[0].strip()] += 1
    elif 'invalid ' in issue:
        fm_category_counter[issue.split(":")[0]] += 1
    else:
        fm_category_counter['other'] += 1

# Categorize broken: short-name vs long-name
broken_short = sum(1 for s, t in broken_links if '/' not in t)
broken_long = len(broken_links) - broken_short

# ──────────────────────────────────────────────
# OUTPUT
# ──────────────────────────────────────────────
if not args.quiet:
    print("\n=== 2a. ORPHAN PAGES ===")
    print(f"Orphan pages (0 inbound links): {len(orphan_pages)}")
    for p in sorted(orphan_pages):
        print(f"  {p}")

    print("\n=== 2b. BROKEN WIKILINKS ===")
    print(f"Broken wikilinks: {len(broken_links)}")
    print(f"  - Short-name (no /): {broken_short}")
    print(f"  - Long-name (with /): {broken_long}")
    print(f"Resolved via fuzzy/legacy (basename/prefix match): {len(fuzzy_resolved)}")
    for src, tgt, resolved_via, kind in sorted(fuzzy_resolved, key=lambda x: (x[0], x[1]))[:10]:
        print(f"  {kind.upper():14s}  {src} -> [[{tgt}]]  →  wiki/{resolved_via}")

    print("\n=== 2c. INDEX COMPLETENESS ===")
    print(f"Missing from index/references: {len(index_missing)}")
    for kind, path in sorted(index_missing, key=lambda x: x[1]):
        print(f"  [{kind}] {path}")

    print("\n=== 2d. FRONTMATTER VALIDATION ===")
    print(f"Frontmatter issues: {len(frontmatter_issues)}")
    for k, v in fm_category_counter.most_common():
        print(f"  - {k}: {v}")
    for path, issue in sorted(frontmatter_issues, key=lambda x: x[0]):
        print(f"  {path}: {issue}")

    print("\n=== 2e. STALE CONTENT ===")
    print(f"Most recent source update: {most_recent_source_update}")
    print(f"Stale pages: {len(stale_pages)}")

    print("\n=== 2f. PAGE SIZE (>200 lines) ===")
    print(f"Large pages: {len(large_pages)}")
    for rel, n in sorted(large_pages, key=lambda x: -x[1])[:5]:
        print(f"  {n} lines: {rel}")

    if args.bucket_stats:
        print("\n=== BUCKET STATS (by namespace) ===")
        print("--- Broken wikilinks by source namespace ---")
        for b, n in sorted(bucket_broken.items(), key=lambda x: -x[1])[:15]:
            print(f"  {b:40s} {n}")
        print("--- Orphans by namespace ---")
        for b, n in sorted(bucket_orphans.items(), key=lambda x: -x[1])[:15]:
            print(f"  {b:40s} {n}")
        print("--- Frontmatter issues by namespace ---")
        for b, n in sorted(bucket_fm.items(), key=lambda x: -x[1])[:15]:
            print(f"  {b:40s} {n}")

    if args.fix_stub:
        print(f"\n=== --fix-stub ===")
        print(f"Stubs created: {len(stubs_created)}")
        for s in stubs_created:
            print(f"  {s}")

    print("\n" + "="*60)
    print("LINT SUMMARY")
    print("="*60)
    print(f"Total wiki .md files: {len(all_files)}")
    print(f"Orphan pages:         {len(orphan_pages)}")
    print(f"Broken wikilinks:     {len(broken_links)}  (short={broken_short}, long={broken_long})")
    print(f"Index missing:        {len(index_missing)}")
    print(f"Frontmatter issues:   {len(frontmatter_issues)}")
    print(f"Stale pages:          {len(stale_pages)}")
    print(f"Large pages (>200):   {len(large_pages)}")

# ──────────────────────────────────────────────
# JSON output
# ──────────────────────────────────────────────
if args.json:
    output = {
        "summary": {
            "total_files": len(all_files),
            "ignored": args.ignore,
            "orphans": len(orphan_pages),
            "broken_total": len(broken_links),
            "broken_short": broken_short,
            "broken_long": broken_long,
            "index_missing": len(index_missing),
            "frontmatter_issues": len(frontmatter_issues),
            "stale": len(stale_pages),
            "large": len(large_pages),
            "fuzzy_resolved": len(fuzzy_resolved),
        },
        "frontmatter_categories": dict(fm_category_counter),
        "bucket_stats": {
            "broken_by_source_ns": dict(bucket_broken),
            "orphans_by_ns": dict(bucket_orphans),
            "frontmatter_by_ns": dict(bucket_fm),
        },
        "orphan_pages": orphan_pages,
        "broken_links": broken_links,
        "fuzzy_resolved": fuzzy_resolved,
        "index_missing": index_missing,
        "frontmatter_issues": frontmatter_issues,
        "stale_pages": stale_pages,
        "large_pages": large_pages,
    }
    if args.fix_stub:
        output["stubs_created"] = stubs_created
    with open("/tmp/lint_results.json", "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    if not args.quiet:
        print("\nResults saved to /tmp/lint_results.json")

# ──────────────────────────────────────────────
# CSV output
# ──────────────────────────────────────────────
if args.csv:
    base = "/tmp/lint_"
    with open(base + "broken_links.csv", "w", newline='') as f:
        w = csv.writer(f)
        w.writerow(["source_file", "broken_target", "short_or_long", "bucket"])
        for s, t in broken_links:
            w.writerow([s, t, "short" if '/' not in t else "long", bucket_for(s)])
    with open(base + "orphans.csv", "w", newline='') as f:
        w = csv.writer(f)
        w.writerow(["orphan_file", "bucket"])
        for o in orphan_pages:
            w.writerow([o, bucket_for(o)])
    with open(base + "frontmatter_issues.csv", "w", newline='') as f:
        w = csv.writer(f)
        w.writerow(["file", "issue", "bucket"])
        for r, i in frontmatter_issues:
            w.writerow([r, i, bucket_for(r)])
    with open(base + "index_missing.csv", "w", newline='') as f:
        w = csv.writer(f)
        w.writerow(["kind", "path", "bucket"])
        for k, p in index_missing:
            w.writerow([k, p, bucket_for(p)])
    if not args.quiet:
        print(f"\nCSV reports saved to /tmp/lint_*.csv (4 files)")
