---
type: source
source-type: github
title: "m10-performance — C++ Master: Performance Mental Model"
author: Sphinx Shi
date: 2026-05-27
size: small
path: raw/Modern-Cpp-Skills/m10-performance/SKILL.md
summary: "C++ Master-level skill for performance. Core question: Where is the data? Covers cache locality, heap allocation, inlining, SIMD, standard layout, string_view, reserve, and PMR."
tags: [cpp, master, performance, cache-locality, allocation]
created: 2026-05-27
---
# m10-performance — C++ Performance

## 核心內容

**Core Question**: 數據在哪裡？

- **Contiguous?** (Cache friendly) → `std::vector`
- **Scattered?** (Cache miss) → `std::list`, `std::map`

### 思維框架

1. **Count the allocations.** Can they be fused? (`reserve`) Can they be removed? (Stack / SSO)
2. **Measure, don't guess.** Use Google Benchmark or Quick-Bench.
3. **Data layout.** Struct padding? Reorder members largest to smallest. Pointer chasing? Flatten the graph.

### Quick Reference

| Technique | Benefit | Implementation |
|-----------|---------|----------------|
| `reserve()` | Avoid reallocs | Call before loop. |
| `string_view` | No copy string | Params. |
| `std::vector` | Cache locality | Default container. |
| PMR | Custom alloc | `std::pmr::monotonic_buffer_resource`. |

## 相關 Entity

- [[entities/cpp/modern/modern-m10-performance]]
- [[entities/cpp/modern/modern-m11-ecosystem]]
- [[entities/cpp/cpp-perf-optimization]]