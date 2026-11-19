---
type: entity
tags: [cpp, master, ecosystem, cmake, vcpkg, conan, build-tooling]
created: 2026-05-25
sources: [cpp-modern-skills]
---

# Master: C++ Ecosystem Mental Model

## 核心問題

**如何構建和維護這個項目？**

- **Build**: CMake (Standard)
- **Deps**: vcpkg 或 Conan（不要手動安裝）
- **Quality**: Clang-Tidy + AddressSanitizer

## Thinking Prompt

1. **構建可重現嗎？**
   - 是？→ CMake + Manifest (vcpkg.json)
   - 否？→ 手動路徑（壞）

2. **你在檢查 bug 嗎？**
   - `fsanitize=address` 捕捉 90% 的內存錯誤

## Quick Reference

| 工具 | 用途 |
|------|------|
| **CMake** | 構建系統生成器 |
| **vcpkg** | MSFT 包管理器（基於源）|
| **Conan** | Python 包管理器（二進制緩存）|
| **ASan** | Address Sanitizer（內存 bug）|
| **Clang-Tidy** | 靜態分析 / Linter |

## 相關概念

- [[entities/cpp/cpp-safety]] - AddressSanitizer、UBSan 是安全工具的一部分
- [[entities/cpp/modern/c17-11-ecosystem]] - C++17 Ecosystem 技能

## 來源詳情

- [[sources/cpp-modern-skills]] - m11-ecosystem: CMake, vcpkg, Conan, sanitizers, tooling
