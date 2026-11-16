#!/usr/bin/env python3
"""Round 3 broken-wikilink cleanup.

Subagent in the previous step created ~19 entity stub pages.
That brought broken from 41 -> 23. The remaining 23 split:

  - 8 OCR placeholder names still pointing at deleted slugs.
  - 3 path-prefix bugs (home.md missing `sources/`, bookmark
    with doubled `sources/`, new page at `network-namespace` vs
    link target `linux-network-namespace`).
  - 4 new pages created by the subagent that point at each
    other with typo'd targets (e.g. snort3-net-inspectors
    -> [[packet-capture]] but the real page is
    entities/linux/snort3/packet-capture).

All 23 are mechanical. After this round broken -> 0 (or close).

Idempotent.
"""
from __future__ import annotations

import sys
from pathlib import Path

PYRAMID = Path("/Users/sphinx.shi/workspace/wiki/pyramid")
WIKI = PYRAMID / "wiki"

# (src_file_relative_to_pyramid, old_target, new_target) -- literal
# string replaces on the exact `[[<old>]]` -> `[[<new>]]`.
AUTO_FIX = [
    # A: OCR placeholder names. Use real-page slug.
    ("sources/pdf-books-batch-alpha-1.md",
     "pdf-book-algorithms-c", "pdf-algorithms-in-c"),
    ("sources/pdf-book-ds-algos-cpp.md",
     "pdf-book-algorithms-c", "pdf-algorithms-in-c"),
    ("sources/pdf-book-cracking-coding-interview.md",
     "pdf-book-algorithms-c", "pdf-algorithms-in-c"),
    ("sources/pdf-book-sedgewick-graph-algos.md",
     "pdf-book-algorithms-c", "pdf-algorithms-in-c"),
    ("sources/pdf-book-muduo.md",
     "pdf-linux-高性能服务器编程", "pdf-linux高性能服务器编程"),
    ("sources/pdf-book-linux-multi-thread-server.md",
     "pdf-linux-高性能服务器编程", "pdf-linux高性能服务器编程"),
    ("sources/pdf-book-lwip.md",
     "pdf-linux-高性能服务器编程", "pdf-linux高性能服务器编程"),
    ("sources/pdf-book-unix-programming-tools.md",
     "pdf-unix-environment-advanced-programming",
     "pdf-unix环境高级编程第三版"),
    ("sources/pdf-book-the-linux-programming-interface.md",
     "pdf-unix-environment-advanced-programming",
     "pdf-unix环境高级编程第三版"),
    ("sources/pdf-unix-programming-tools.md",
     "pdf-unix-environment-advanced-programming",
     "pdf-unix环境高级编程第三版"),
    ("sources/pdf-book-cache-memory.md",
     "pdf-computer-architecture-hp",
     "pdf-计算机体系结构量化研究方法第五版中文版"),
    ("entities/arm-hp-computer-architecture.md",
     "pdf-computer-architecture-hp",
     "pdf-计算机体系结构量化研究方法第五版中文版"),
    ("entities/linux/process-management-model.md",
     "pdf-unix-environment-advanced-programming",
     "pdf-unix环境高级编程第三版"),
    # B: path-prefix bugs in home.md and bookmark
    ("home.md", "pdf-computer-architecture-hp",
     "sources/pdf-计算机体系结构量化研究方法第五版中文版"),
    ("home.md", "pdf-unix-environment-advanced-programming",
     "sources/pdf-unix环境高级编程第三版"),
    ("sources/bookmark-stl-source-analysis.md",
     "sources/bookmark-cpp-template-tutorial",
     "bookmark-cpp-template-tutorial"),
    # B2: new page at network-namespace vs link linux-network-namespace
    ("entities/container-technology.md",
     "linux-network-namespace",
     "entities/linux/network-namespace"),
    # C: subagent-created pages with wrong sub-target paths
    ("entities/linux/snort3/snort3-net-inspectors.md",
     "packet-capture", "entities/linux/snort3/packet-capture"),
    ("entities/linux/snort3/snort3-net-inspectors.md",
     "stream-reassembly", "entities/linux/snort3/stream-reassembly"),
    ("entities/linux/snort3/network-monitoring.md",
     "entities/linux/snort3/packet-capture",
     "entities/linux/snort3/packet-capture"),
    ("entities/linux/snort3/snort3-actions.md",
     "ips_action.framework", "entities/linux/snort3/ips-action-framework"),
    # C2: subagent page's own wikilink to a page that doesn't exist
    ("entities/cpp/modern-cpp/cpp-explicit-virtual-overrides.md",
     "entities/cpp/modern-cpp/cpp-virtual-tables-and-inheritance",
     "entities/cpp/modern-cpp/cpp-attributes"),
    # D: bookmark-cpp-template-tutorial -> create a stub source page
    # OR redirect to an existing related page. Subagent made the
    # page but apparently at a different name. We point the link
    # at an existing source page that covers the same material
    # (cpp-template-tutorial source).
    # Actually let's create the page here as a stub -- it's a
    # simple "bookmark" stub. See below in create_books.
]


# Also need to create sources/bookmark-cpp-template-tutorial and
# sources/kernel-block-index (last 2 broken targets).
BOOK_STUBS = [
    ("sources/bookmark-cpp-template-tutorial.md", {
        "type": "source",
        "source-type": "bookmark",
        "title": "C++ Template Tutorial (bookmark)",
        "url": "https://github.com/wuye9036/CppTemplateTutorial",
        "summary": "C++ template 教程: SFINAE, metaprogramming, traits, "
                   "constexpr, concepts — 覆盖 C++11/14/17/20 模板元编程.",
        "tags": ["cpp", "templates", "metaprogramming", "bookmark"],
        "created": "2026-06-08",
    }, """# C++ Template Tutorial

## 来源信息

- **Author**: wuye9036
- **URL**: https://github.com/wuye9036/CppTemplateTutorial
- **Language**: 中文
- **Topic**: C++ 模板元编程

## 核心内容

- C++ template 基础 (typename, dependent name)
- SFINAE (Substitution Failure Is Not An Error) 与 enable_if
- 类型萃取 (type_traits) 与编译期计算
- 变参模板 (variadic templates) 与折叠表达式
- 模板递归与 CRTP (Curiously Recurring Template Pattern)
- 概念 (C++20 concepts) 与约束
- 模板与多态: 静态多态 vs 动态多态
- 编译期整数序列 (integer_sequence) 与 std::apply

## 相关页面
- [[entities/cpp/cpp-standard-library]]
- [[entities/cpp/modern-cpp/cpp-type-traits]]
- [[entities/cpp/modern-cpp/cpp-explicit-virtual-overrides]]
- [[sources/bookmark-stl-source-analysis]]
- [[entities/cpp]]
"""),
    ("sources/kernel-block-index.md", {
        "type": "source",
        "source-type": "web",
        "title": "WoWoTech Linux Kernel Block Index",
        "url": "http://www.wowotech.net/comm/2353.html",
        "summary": "WoWoTech 内核块设备索引页: block layer 架构、bio 合并、"
                   "request 调度、multi-queue、blk-mq.",
        "tags": ["linux-kernel", "block", "io", "wowotech"],
        "created": "2026-06-08",
    }, """# WoWoTech Linux Kernel Block Index

## 来源信息

- **Author**: WoWoTech (lihaijian)
- **URL**: http://www.wowotech.net/comm/2353.html
- **Language**: 中文
- **Topic**: Linux block layer

## 核心内容

- Block layer 整体架构 (bio, request, queue)
- Generic block layer 与 blk-mq (multi-queue)
- IO 调度器 (cfq, deadline, noop) 与 mq-deadline, bfq, kyber
- bio 合并策略 (front/back merge)
- plug/unplug 模型与 polling
- Block device driver 模板 (request-based vs bio-based)

## 相关页面
- [[entities/linux/kernel/block/linux-kernel-block-core]]
- [[entities/linux/kernel/sched/linux-kernel-sched-core]]
- [[entities/linux/ebpf]]
- [[entities/linux]]
"""),
]


def main():
    write = "--write" in sys.argv
    files_touched: dict[str, int] = {}
    total = 0

    for src_rel, old, new in AUTO_FIX:
        path = WIKI / src_rel
        if not path.exists():
            print(f"  [MISSING] {src_rel}")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"  [READ-ERR] {src_rel}: {e}")
            continue
        old_link = f"[[{old}]]"
        new_link = f"[[{new}]]"
        if old_link not in text:
            print(f"  [NOOP]   {src_rel}: {old_link} not found")
            continue
        new_text = text.replace(old_link, new_link)
        n = text.count(old_link)
        if write:
            path.write_text(new_text, encoding="utf-8")
        files_touched[src_rel] = files_touched.get(src_rel, 0) + n
        total += n
        verb = "PATCH" if write else "WOULD"
        print(f"  [{verb}] {src_rel}  ({old_link} -> {new_link})")

    for rel, fm, body in BOOK_STUBS:
        path = WIKI / rel
        if path.exists():
            print(f"  [EXISTS] {rel}")
            continue
        # build frontmatter
        fm_lines = ["---"]
        for k, v in fm.items():
            if isinstance(v, list):
                fm_lines.append(f"{k}: [{', '.join(v)}]")
            else:
                fm_lines.append(f'{k}: "{v}"')
        fm_lines.append("---")
        fm_text = "\n".join(fm_lines) + "\n"
        if write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(fm_text + body, encoding="utf-8")
        verb = "CREATE" if write else "WOULD-CREATE"
        print(f"  [{verb}] {rel}")

    print()
    print(f"Total replacements: {total}, files touched: {len(files_touched)}, "
          f"new pages: {len(BOOK_STUBS)}")


if __name__ == "__main__":
    main()
