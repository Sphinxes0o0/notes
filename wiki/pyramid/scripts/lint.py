#!/usr/bin/env python3
"""
Pyramid Wiki Lint — 5 check categories:
  1. Broken wikilinks   [[target]] where target .md doesn't exist
  2. Orphan entities    entity pages with zero incoming wikilinks
  3. Missing frontmatter files without type/tags/created
  4. Missing index      entities not listed in any *-index.md
  5. Empty files        .md files with no body content
"""

import os
import re
import json
import argparse
from collections import defaultdict

WIKI = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "wiki")
OUT_JSON = "/tmp/lint_results.json"


# ── helpers ──────────────────────────────────────────────────────────────────

def walk_md(root):
    """Yield (rel_path, abs_path) for every .md file, skipping hidden/attachments."""
    skip_dirs = {'.obsidian', '.templates', 'attachments'}
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for f in files:
            if f.endswith('.md'):
                rel = os.path.relpath(os.path.join(dirpath, f), root)
                yield rel, os.path.join(dirpath, f)


def parse_frontmatter(content):
    """Return (frontmatter_dict, body) or (None, full_content) if no fm."""
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not m:
        return None, content
    raw, body = m.group(1), content[m.end():]
    fields = {}
    for line in raw.split('\n'):
        line = line.strip()
        if ':' not in line:
            continue
        key, _, val = line.partition(':')
        key = key.strip()
        val = val.strip()
        if val.startswith('"') and val.endswith('"'):
            val = val[1:-1]
        elif val.startswith('[') and val.endswith(']'):
            items = [v.strip().strip('"').strip("'") for v in val[1:-1].split(',') if v.strip()]
            val = items
        fields[key] = val
    return fields, body


def extract_wikilinks(body):
    """Return set of link targets (strip anchors, pipes, leading ./)."""
    links = set()
    for m in re.finditer(r'\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]', body):
        t = m.group(1).strip()
        if t.startswith('./'):
            t = t[2:]
        links.add(t)
    return links


# ── check 1: broken wikilinks ─────────────────────────────────────────────────

def check_broken_links(all_files, contents):
    issues = []
    valid = {rel.replace('.md', '') for rel, _ in all_files}
    # Build basename → full-path mapping for fuzzy resolution (Obsidian-style search)
    basename_to_full = defaultdict(set)
    for v in valid:
        bn = v.rsplit('/', 1)[-1]
        basename_to_full[bn].add(v)

    outbound = {}
    for rel, _ in all_files:
        _, body = parse_frontmatter(contents[rel])
        links = extract_wikilinks(body)
        outbound[rel] = links
        for t in links:
            if t in valid:
                continue  # exact match — always OK
            # Fuzzy: try basename match (Obsidian searches by filename)
            bn = t.rsplit('/', 1)[-1]
            if bn in basename_to_full:
                continue  # resolved via basename
            # Fuzzy: try suffix match (e.g. link to "mm" resolves to "linux/kernel/mm/...")
            matched = False
            for v in valid:
                if v.endswith('/' + t) or v.endswith(t):
                    matched = True
                    break
            if matched:
                continue
            issues.append((rel, t))

    # Group by target for impact scoring
    by_target = defaultdict(list)
    for src, tgt in issues:
        by_target[tgt].append(src)
    return issues, outbound, by_target


# ── check 2: orphan entities ───────────────────────────────────────────────────

def check_orphans(all_files, outbound):
    content_ents = [rel for rel, _ in all_files if rel.startswith('entities/')]
    inbound = defaultdict(int)
    for src, links in outbound.items():
        for t in links:
            for rel, _ in all_files:
                if rel.replace('.md', '') == t:
                    inbound[rel] += 1
                    break
    return [rel for rel in content_ents if inbound.get(rel, 0) == 0]


# ── check 3: missing frontmatter ──────────────────────────────────────────────

def check_frontmatter(all_files, contents):
    issues = []
    for rel, _ in all_files:
        fm, _ = parse_frontmatter(contents[rel])
        if fm is None:
            issues.append((rel, "missing frontmatter entirely"))
            continue
        for field in ('type', 'tags', 'created'):
            if field not in fm:
                issues.append((rel, f"missing '{field}'"))
    return issues


# ── check 4: missing index ───────────────────────────────────────────────────

def check_missing_index(all_files, contents, outbound):
    """Entities not listed in any *-index.md."""
    # Gather entities listed in all index pages
    index_entities = set()
    index_files = [rel for rel, _ in all_files if rel.endswith('-index.md')]
    for rel in index_files:
        _, body = parse_frontmatter(contents[rel])
        for t in extract_wikilinks(body):
            if t.startswith('entities/') or 'entities/' + t.split('/')[-1] == t:
                index_entities.add(t if t.startswith('entities/') else 'entities/' + t)

    # All actual entities
    actual_entities = {rel for rel, _ in all_files if rel.startswith('entities/')}

    # Normalize index_entities to match actual format
    normalized_index = set()
    for ie in index_entities:
        if ie in actual_entities:
            normalized_index.add(ie)
        else:
            # Try stripping entities/ prefix if used
            stripped = ie.replace('entities/', '')
            for ae in actual_entities:
                if ae.endswith('/' + stripped) or ae == stripped:
                    normalized_index.add(ae)

    missing = []
    for ent in sorted(actual_entities):
        ent_base = ent.replace('.md', '')
        found = False
        for ie in index_entities:
            if ie == ent_base or ie == ent or ie.endswith('/' + ent_base.split('/')[-1]):
                found = True
                break
        if not found:
            missing.append(ent)
    return missing, index_files


# ── check 5: empty files ─────────────────────────────────────────────────────

def check_empty(all_files, contents):
    issues = []
    for rel, _ in all_files:
        _, body = parse_frontmatter(contents[rel])
        stripped = body.strip()
        # Also check body is just whitespace / has no real content
        lines = [l for l in stripped.split('\n') if l.strip()]
        if len(lines) == 0:
            issues.append(rel)
    return issues


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Pyramid Wiki Lint")
    parser.add_argument('--json', action='store_true', help=f"Write detailed JSON to {OUT_JSON}")
    parser.add_argument('--fix-mode', action='store_true', help='Stub: prepare fixes without writing')
    args = parser.parse_args()

    all_files = list(walk_md(WIKI))
    print(f"Total .md files: {len(all_files)}")

    contents = {}
    for rel, full in all_files:
        with open(full, 'r', encoding='utf-8') as fh:
            contents[rel] = fh.read()

    # Run all checks
    broken_links, outbound, by_target = check_broken_links(all_files, contents)
    orphans = check_orphans(all_files, outbound)
    fm_issues = check_frontmatter(all_files, contents)
    missing_index, index_files = check_missing_index(all_files, contents, outbound)
    empty_files = check_empty(all_files, contents)

    # ── Summary table ────────────────────────────────────────────────────────
    print("\n" + "=" * 64)
    print(f"{'CATEGORY':<24} {'COUNT':>6}")
    print("=" * 64)
    print(f"{'Broken wikilinks':<24} {len(broken_links):>6}")
    print(f"{'Orphan entities':<24} {len(orphans):>6}")
    print(f"{'Missing frontmatter':<24} {len(fm_issues):>6}")
    print(f"{'Missing from index':<24} {len(missing_index):>6}")
    print(f"{'Empty files':<24} {len(empty_files):>6}")
    print("=" * 64)

    # ── Top 20 most impactful broken links ───────────────────────────────────
    if broken_links:
        print("\n### TOP 20 MOST IMPACTED BROKEN WIKILINKS")
        print(f"{'Target':<50} {'Affected pages':>14}")
        print("-" * 64)
        sorted_targets = sorted(by_target.items(), key=lambda x: -len(x[1]))
        for tgt, srcs in sorted_targets[:20]:
            print(f"  [[{tgt}]]".ljust(52) + f"{len(srcs):>14}")
            for s in srcs[:3]:
                print(f"    from: {s}")
            if len(srcs) > 3:
                print(f"    ... and {len(srcs) - 3} more")

    # ── Orphan entities ──────────────────────────────────────────────────────
    if orphans:
        print(f"\n### ORPHAN ENTITIES ({len(orphans)})")
        for p in sorted(orphans)[:20]:
            print(f"  {p}")

    # ── Missing frontmatter ──────────────────────────────────────────────────
    if fm_issues:
        print(f"\n### MISSING FRONTMATTER ({len(fm_issues)})")
        for p, issue in sorted(fm_issues)[:20]:
            print(f"  {p}: {issue}")

    # ── Missing from index ────────────────────────────────────────────────────
    if missing_index:
        print(f"\n### MISSING FROM INDEX ({len(missing_index)})")
        for p in sorted(missing_index)[:20]:
            print(f"  {p}")

    # ── Empty files ───────────────────────────────────────────────────────────
    if empty_files:
        print(f"\n### EMPTY FILES ({len(empty_files)})")
        for p in empty_files:
            print(f"  {p}")

    # ── JSON output ──────────────────────────────────────────────────────────
    if args.json:
        result = {
            "broken_links": [{"target": tgt, "sources": srcs} for tgt, srcs in sorted_targets],
            "orphans": sorted(orphans),
            "fm_issues": [{"file": f, "issue": i} for f, i in fm_issues],
            "missing_index": sorted(missing_index),
            "empty_files": empty_files,
            "index_files": sorted(index_files),
            "summary": {
                "total_files": len(all_files),
                "broken_wikilinks": len(broken_links),
                "orphan_entities": len(orphans),
                "missing_frontmatter": len(fm_issues),
                "missing_from_index": len(missing_index),
                "empty_files": len(empty_files),
            }
        }
        with open(OUT_JSON, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\nDetailed JSON saved to {OUT_JSON}")

    return result if args.json else None


if __name__ == '__main__':
    main()