#!/usr/bin/env python3
"""fix_external_links.py — One-shot fixer for broken external links in notes/.

Two modes:
  replace  — swap [text](old_url) with [text](new_url) on a line matching
             a substring. For 404 broken URLs we point at a working
             fallback (docs site, project root, or generic homepage).
  delete   — remove the entire bullet/list/table line. For URLs with no
             reasonable replacement.

By design this does NOT use archive.org. Archive.org is a redirector —
when the target itself is dead, the snapshot is also dead. Pointing at
archive.org as a fallback masks a real problem; deleting or replacing
is more honest.

Run:  python3 scripts/fix_external_links.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

NOTES = Path("notes")

LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")


def fix_replace(file_path: Path, old_url: str, new_url: str, line_match: str) -> bool:
    """Replace `[text](old_url)` with `[text](new_url)` on a line containing line_match."""
    text = file_path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    changed = False
    for i, line in enumerate(lines):
        if line_match not in line:
            continue
        if old_url not in line:
            continue
        new_line = LINK_PATTERN.sub(
            lambda m: f"[{m.group(1)}]({new_url})"
            if m.group(2) == old_url
            else m.group(0),
            line,
        )
        if new_line != line:
            lines[i] = new_line
            changed = True
            break
    if changed:
        file_path.write_text("".join(lines), encoding="utf-8")
    return changed


def fix_delete(file_path: Path, line_match: str) -> bool:
    """Delete the entire line containing line_match."""
    text = file_path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    changed = False
    for i, line in enumerate(lines):
        if line_match not in line:
            continue
        # Only delete if the line looks like a single-link bullet/list/table
        if line.lstrip().startswith(("-", "*", "|", "1.", "2.", "3.")):
            del lines[i]
            changed = True
            break
    if changed:
        file_path.write_text("".join(lines), encoding="utf-8")
    return changed


# Each fix: {file, line_match, action, old_url, new_url (for replace)}
FIXES = [
    # ===== 404 — replace with working URL or delete =====
    {
        "file": "ccpp/hermes_memory_research_2026h1.md",
        "line_match": "GitHub Search API",
        "action": "replace",
        "old_url": "https://api.github.com/search/repositories",
        "new_url": "https://github.com/search?q=&type=repositories",
    },
    {
        "file": "interview/07_推荐资源.md",
        "line_match": "System Design Interview",
        "action": "delete",  # 商品下架,无合理替代
    },
    {
        "file": "kernel/openbmc/kvm_virtualmedia.md",
        "line_match": "phosphor-virtualmedia 源码",
        "action": "replace",
        "old_url": "https://github.com/openbmc/phosphor-virtualmedia",
        "new_url": "https://github.com/openbmc",  # 删库的 repo → 项目主页
    },
    {
        "file": "kernel/openbmc/kvm_virtualmedia.md",
        "line_match": "phosphor-kvm (obmc-ikvm) 源码",
        "action": "replace",
        "old_url": "https://github.com/openbmc/phosphor-kvm",
        "new_url": "https://github.com/openbmc",
    },
    {
        "file": "kernel/openbmc/kvm_virtualmedia.md",
        "line_match": "Linux USB Gadget API",
        "action": "replace",
        "old_url": "https://www.kernel.org/doc/html/latest/usb/gadget/index.html",
        "new_url": "https://docs.kernel.org/driver-api/usb/",
    },
    {
        "file": "security/network-traffic-analysis/README.md",
        "line_match": "Encrypted Traffic Analysis - Cisco ETA",
        "action": "delete",  # 产品页下架
    },
    {
        "file": "security/nids/snort3_architecture_analysis.md",
        "line_match": "Snort 3配置指南",
        "action": "replace",
        "old_url": "https://snort.org/documents/snort-3-configuration-guide",
        "new_url": "https://docs.snort.org/",
    },
    {
        "file": "security/nids/snort3_architecture_analysis.md",
        "line_match": "Snort 3规则编写",
        "action": "replace",
        "old_url": "https://snort.org/documents/snort-3-rule-writing",
        "new_url": "https://docs.snort.org/",
    },
    # 临时错误(5xx/403/521/422) — 保留原 URL,不动
    # csdn / hackerrank / leetcode: temporary, leave alone
]


def main() -> int:
    ok = 0
    fail = 0
    for fx in FIXES:
        path = NOTES / fx["file"]
        if not path.exists():
            print(f"  ✗ {fx['file']}: file not found")
            fail += 1
            continue
        if fx["action"] == "replace":
            if fix_replace(path, fx["old_url"], fx["new_url"], fx["line_match"]):
                print(f"  ✓ {fx['file']}  replace {fx['line_match']}")
                ok += 1
            else:
                print(f"  ✗ {fx['file']}: no match for line {fx['line_match']!r} + URL {fx['old_url']}")
                fail += 1
        elif fx["action"] == "delete":
            if fix_delete(path, fx["line_match"]):
                print(f"  ✓ {fx['file']}  delete line {fx['line_match']!r}")
                ok += 1
            else:
                print(f"  ✗ {fx['file']}: no match for line {fx['line_match']!r}")
                fail += 1
    print()
    print(f"Replaced/Appended: {ok}")
    print(f"Failed:            {fail}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
