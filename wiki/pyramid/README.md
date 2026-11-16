# Pyramid — Tech LLM Wiki

LLM-maintained interlinked knowledge base covering Linux kernel, C++, eBPF, networking, algorithms, security, ARM, and more.

## 📦 OKF Conformance

This repository is packaged as a compliant **[Open Knowledge Format v0.1](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing)** knowledge pack.

| OKF Element | Location |
|---|---|
| Pack metadata | [`okf.yaml`](./okf.yaml) |
| Content manifest | [`okf.manifest.yaml`](./okf.manifest.yaml) |
| Schema / agent rules | [`AGENT.md`](./AGENT.md) |
| Knowledge root | `wiki/` |
| Raw sources (immutable) | `raw/` |
| Entry point | [`wiki/index.md`](./wiki/index.md) |
| Lint script | [`scripts/lint_okf.py`](./scripts/lint_okf.py) |

**Concept types supported:** `entity`, `source`, `synthesis`, `journal`, `index`, `log`, `dashboard`.

Pyramid predates OKF v0.1 (Google Cloud, 2026-06) — it has been a direct implementation of [Karpathy's LLM-Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) since 2026-05, and the OKF conformance layer was added retroactively without structural changes.

## Stats

~205 pages | 19 module indexes | 35 PDF sources + 25+ notes sources | 124 PDFs ingested

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
