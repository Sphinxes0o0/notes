# Pyramid — Tech LLM Wiki

LLM-maintained interlinked knowledge base covering Linux kernel, C++, eBPF, networking, algorithms, security, ARM, and more.

## Stats

~175 pages | 19 module indexes | 70+ sources

## Structure

```
raw/          — Immutable sources (PDFs, bookmarks, web clips)
wiki/         — LLM-authored pages (Obsidian vault)
  entities/   — Concept pages (Linux kernel, eBPF, C++11, etc.)
  sources/    — Source summaries (PDFs, GitHub repos, notes)
  synthesis/  — Cross-topic analysis
  */index     — Module index pages (sub-hubs for graph navigation)
```

raw/ → sources → wiki/ (one-way, LLM never modifies raw/)

## Quick Start

Open in Obsidian, VS Code, or any markdown editor:

```bash
cd wiki && open .
```

Start from [[wiki/home]] for full navigation.

## Recent Activity

- **2026-05-23** lint: add missing sources:/created: fields
- **2026-05-22** lint: fix navigation — 13 entities to indexes, 4 orphans cross-linked
- **2026-05-22** lint: normalize tag naming (case, singular/plural)
- **2026-05-22** ingest: ~56 books across C++/Linux/Algo/Security/ARM
- **2026-05-21** ingest: 3 eBPF papers + 16 notes/docs PDFs

Full history: `git log --oneline`
