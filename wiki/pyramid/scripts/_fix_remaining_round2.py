#!/usr/bin/env python3
"""Round 2 broken-wikilink cleanup.

Round 1 (cdcaf6f) handled 35 mechanical fixes. Round 2 handles two
more categories that are still mechanical:

  A. wikilinks pointing at OCR-deleted placeholder names like
     [[pdf-book-algorithms-c]] -- these were placeholder slugs that
     got deleted in 2c4f333. The right replacement is the actual
     OCR'd page that the placeholder used to be, typically renamed
     to include the new file's slug. Lookup table below.

  B. wikilinks with a doubled `sources/` prefix -- e.g.
     [[sources/pdf-unix-environment-advanced-programming]] actually
     resolves to wiki/sources/sources/... because the link target
     was written to include the `sources/` prefix while the file
     lives at `sources/<...>.md` (no nested `sources/`). These should
     drop the redundant prefix.

Round 2 does NOT create new entity stub pages for the remaining
~15 missing targets (snort3, linux kernel, cpp, etc) -- those
need LLM judgment and are handled by a separate CC pass.
"""
from __future__ import annotations

import sys
from pathlib import Path

PYRAMID = Path("/Users/sphinx.shi/workspace/wiki/pyramid")
WIKI = PYRAMID / "wiki"

# A. Placeholder-name -> real OCR'd page slug
PLACEHOLDER_TO_REAL = {
    "pdf-book-algorithms-c": "pdf-algorithms-in-c",
    "pdf-book-trustzone-optee": "pdf-book-trustzone-optee-dev",
    "pdf-book-rust-book-zh-cn": "pdf-book-programming-rust",
    "pdf-bpf-rethinking-kernel": "pdf-book-ebpf-basics-cn",
    "pdf-book-algo-ds-books": "pdf-algo-ds-books",
    "pdf-book-unix-advanced-programming": "pdf-unix-environment-advanced-programming",
    "pdf-book-c-language": "pdf-unix-programming-tools",
    "pdf-book-linux-high-perf-server": "pdf-linux-高性能服务器编程",
    "pdf-book-linux-net-server": "pdf-linux-高性能服务器编程",
    "pdf-computer-architecture-hp": "pdf-计算机体系结构量化研究方法第五版中文版",
}

# B. Doubled sources/ prefix: drop the first `sources/`
# Targets where stripping the leading `sources/` yields a real page
SOURCES_PREFIX_FIX = {
    "sources/pdf-unix-environment-advanced-programming": "sources/pdf-unix-environment-advanced-programming".removeprefix("sources/"),
    "sources/pdf-book-algorithms-c": "sources/pdf-book-algorithms-c".removeprefix("sources/"),
    "sources/pdf-computer-architecture-hp": "sources/pdf-computer-architecture-hp".removeprefix("sources/"),
}

# C. Some specific case-by-case fixes (no general pattern)
SPECIFIC_FIXES = {
    # sources in home.md
    ("home.md", "sources/pdf-unix-environment-advanced-programming"):
        "sources/pdf-unix-environment-advanced-programming".removeprefix("sources/"),
    ("home.md", "sources/pdf-computer-architecture-hp"):
        "sources/pdf-computer-architecture-hp".removeprefix("sources/"),
}


def replace_in_text(text: str, old: str, new: str) -> tuple[str, int]:
    """Replace `[[old]]` with `[[new]]` (literal)."""
    old_link = f"[[{old}]]"
    new_link = f"[[{new}]]"
    return text.replace(old_link, new_link), text.count(old_link)


def main():
    write = "--write" in sys.argv
    targets = []

    # A: placeholders -> real
    for src in list(WIKI.rglob("*.md")):
        rel = str(src.relative_to(PYRAMID))
        try:
            text = src.read_text(encoding="utf-8")
        except Exception:
            continue
        for old_short, new_short in PLACEHOLDER_TO_REAL.items():
            old_target = old_short  # placeholder names don't have entities/ prefix
            new_target = new_short
            # Real names are like `pdf-algorithms-in-c` (no entities/
            # prefix) -- but wikilinks sometimes use `sources/`
            # prefix. The lookup table short names are the bare slugs.
            # Try both with and without `sources/` prefix on the new side.
            for new_t in [new_target, "sources/" + new_target]:
                t, n = replace_in_text(text, old_target, new_t)
                if n:
                    text = t
                    break
        if text != src.read_text(encoding="utf-8", errors="replace"):
            if write:
                src.write_text(text, encoding="utf-8")
            n = 0
            for old_short in PLACEHOLDER_TO_REAL:
                for line in text.splitlines() if False else []:
                    pass  # counting is approximate; rely on lint after
            print(f"  [{'PATCH' if write else 'WOULD'}] {rel}")

    # B: doubled sources/ prefix
    print()
    print("=== B: doubled sources/ prefix ===")
    for src in list(WIKI.rglob("*.md")):
        rel = str(src.relative_to(PYRAMID))
        try:
            text = src.read_text(encoding="utf-8")
        except Exception:
            continue
        original = text
        for old, new in SOURCES_PREFIX_FIX.items():
            text, n = replace_in_text(text, old, new)
        if text != original:
            if write:
                src.write_text(text, encoding="utf-8")
            print(f"  [{'PATCH' if write else 'WOULD'}] {rel}")


if __name__ == "__main__":
    main()
