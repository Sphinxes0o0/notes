---
type: entity
tags: [cpp, master, zero-cost, templates, polymorphism]
created: 2026-05-27
sources: [github-modern-cpp-skills-m04]
---

# modern-m04-zero-cost

## 定義

C++ 零成本抽象的核心思維模型：**何時確定類型？編譯時（靜態）還是運行時（動態）？**

## 核心問題

**何時確定類型？**

- **編譯時** (Static): Templates, Concepts, CRTP — 零運行時開銷，代碼膨脹
- **運行時** (Dynamic): 虛函數，`std::any`，`std::variant` — 靈活，vtable 開銷

## 關鍵要點

- C++ 的核心承諾：不為你不使用的特性付出代價
- 動態多態（virtual）：靈活但有 vtable 查找 + 緩存未命中代價
- 靜態多態（template）：零開銷但代碼膨脹，編譯時間增加
- CRTP (Curiously Recurring Template Pattern)：靜態模擬繼承，零虛函數調用開銷
- `std::variant` + `std::visit`：封閉類型集的編譯時分支，接近手工 switch 的性能
- `std::function`：運行時多態，堆分配 + 間接調用開銷

## 常見錯誤映射

| 錯誤 | 設計問題 |
|------|----------|
| Template spew | 是否缺少 Concepts 約束？ |
| Linker error | 是否在 .cpp 中定義了模板？ |
| Object slicing | 是否將 Derived 賦值給 Base 值？ |
| Slow build | 是否過度使用模板/頭文件？ |

## 思維框架

1. **Is the set of types known at compile time?** Yes → Templates or `std::variant`. No → Inheritance.
2. **Do I need to store them in a list?** Homogeneous → `vector<T>`. Heterogeneous → `vector<unique_ptr<Base>>` or `variant<...>`.
3. **Does the interface match exactly?** Duck typing → Templates (Concepts). Strict hierarchy → Inheritance.

## 相關概念

- [[entities/cpp/modern/modern-m05-type-driven]] — Concepts 是模板約束的類型驅動工具
- [[entities/cpp/modern/modern-m10-performance]] — 零成本是性能的基礎
- [[entities/cpp/variadic-templates]] — 模板變參是靜態多態的核心
- [[entities/cpp/cpp-templates]] — C++ 模板完整指南
- [[entities/cpp/cpp-stl-containers]] — STL 容器的選擇影響靜態/動態語義

## Source

- [[sources/github-modern-cpp-skills-m04]]