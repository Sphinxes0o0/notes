---
type: entity
tags: [cpp, master, performance, cache-locality, allocation]
created: 2026-05-27
sources: [github-modern-cpp-skills-m10]
---

# modern-m10-performance

## 定義

C++ 性能優化的核心思維模型：**數據在哪裡？**

## 核心問題

**數據在哪裡？**

- **Contiguous?** (Cache friendly) → `std::vector`
- **Scattered?** (Cache miss) → `std::list`, `std::map`

## 關鍵要點

- 內存層次：寄存器 → L1 → L2 → L3 → 主存 → 磁盤。相鄰訪問最優
- 分配次數最小化：`reserve()` 避免重新分配，SSO (Small String Optimization) 避免堆分配
- 數據佈局：`struct` 成員按大小降序排列減少 padding；平坦化指針追逐的圖結構
- `string_view`：零拷貝字符串視圖，適合函數參數
- PMR (Polymorphic Memory Resource)：`std::pmr::monotonic_buffer_resource` 減少分配開銷
- **測量，不要猜測**：Google Benchmark 或 Quick-Bench

## 常見錯誤映射

| 問題 | 設計問題 |
|------|----------|
| Cache miss | 數據是否連續？是否在指針圖中跳躍？ |
| 分配過多 | 是否可以融合分配？是否可以棧分配/SSO？ |
| Padding | struct 成員是否按大小排序？ |

## 思維框架

1. **Count the allocations.** Can they be fused? (`reserve`) Can they be removed? (Stack / SSO)
2. **Measure, don't guess.** Use Google Benchmark or Quick-Bench.
3. **Data layout.** Struct padding? Reorder members largest to smallest. Pointer chasing? Flatten the graph.

## 相關概念

- [[entities/cpp/modern/modern-m11-ecosystem]] — 性能測量工具是 ecosystem 的一部分
- [[entities/cpp/modern/modern-m04-zero-cost]] — 零成本抽象是性能的保證
- [[entities/cpp/cpp-stl-containers]] — 容器選擇直接影響性能
- [[entities/cpp/cpp-perf-optimization]] — 性能優化的完整技術棧
- [[entities/cpp/modern/modern-m02-resource]] — 堆分配是性能的敵人
- [[entities/cpp/modern/modern-m07-concurrency]] — False Sharing 是並發性能殺手

## Source

- [[sources/github-modern-cpp-skills-m10]]