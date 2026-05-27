---
type: entity
tags: [cpp, master, mental-model, pointer, reference, undefined-behavior]
created: 2026-05-27
sources: [github-modern-cpp-skills-m14]
---

# modern-m14-mental-model

## 定義

C++ 內存心智模型的核心思維模型：**內存中發生了什麼？**

## 核心問題

**內存中發生了什麼？**

- **Value**: 是否擁有這些字節？
- **Reference**: 是否是別名？
- **Pointer**: 是否可為空（需要檢查）？

## 關鍵要點

- `auto x = y`：拷貝（雙方獨立）
- `auto& x = y`：引用（別名，同一對象）
- `auto* x`：可空指針（使用前需檢查）
- 返回局部引用 `&local` 永遠是錯誤的（懸空引用）
- `std::move` 是將值轉換為右值的類型轉換，本身不移動任何東西
- 未定義行為 (UB)：編譯器假設 UB 不會發生，優化可能導致任何結果

## 思維框架

1. **Is it a copy or reference?** `auto x = y` (Copy). `auto& x = y` (Reference).
2. **Does it dangle?** Returning `&local` is always wrong.
3. **Is this UB?** Compiler assumes UB never happens — optimizations may break your code.

## 相關概念

- [[entities/cpp/modern/modern-m01-ownership]] — 值 vs 引用是所有權的底層語義
- [[entities/cpp/modern/modern-m12-lifecycle]] — 引用超出對象生命周期是 UB
- [[entities/cpp/modern/modern-m02-resource]] — 指針的所有權語義
- [[entities/cpp/modern/modern-m15-anti-pattern]] — `void*`、`reinterpret_cast` 是 UB 的溫床
- [[entities/cpp/modern/modern-m04-zero-cost]] — vtable 指針是運行時多態的底層

## Source

- [[sources/github-modern-cpp-skills-m14]]