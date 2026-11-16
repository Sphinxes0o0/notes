---
type: entity
tags: [cpp, master, performance, cache-locality, heap-allocation, inlining]
created: 2026-05-25
sources: [cpp-modern-skills]
---

# Master: C++ Performance Mental Model

## 核心問題

**數據在哪裡？**

- **Contiguous?** (Cache friendly) → `std::vector`
- **Scattered?** (Cache miss) → `std::list`、`std::map`

## Thinking Prompt

1. **計算分配次數**
   - 它們能合併嗎？(`reserve`)
   - 它們能消除嗎？（棧 / SSO）

2. **測量，不要猜測**
   - 使用 Google Benchmark 或 Quick-Bench

3. **數據佈局**
   - `struct` 填充？按從大到小重新排序成員
   - 指針追逐？展平圖

## Quick Reference

| 技術 | 收益 | 實現 |
|------|------|------|
| **`reserve()`** | 避免重分配 | 循環前調用 |
| **`string_view`** | 不拷貝字符串 | 參數 |
| **`std::vector`** | 緩存局部性 | 默認容器 |
| **PMR** | 自定義分配 | `std::pmr::monotonic_buffer_resource` |

## 相關概念

- [[entities/cpp/cpp-perf-optimization]] - CPU cache、SIMD、profiling 工具
- [[entities/cpp/cpp-stl-containers]] - 容器選擇
- [[entities/cpp/modern/c17-10-performance]] - C++17 Performance 技能
- [[entities/cpp/modern/c17-11-ecosystem]] - C++ Ecosystem（CMake、build tooling）

## 來源詳情

- [[sources/cpp-modern-skills]] - m10-performance: cache locality, heap allocation, inlining, SIMD, standard layout
