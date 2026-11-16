---
type: entity
tags: [cpp, master, ecosystem, cmake, build-tool]
created: 2026-05-27
sources: [github-modern-cpp-skills-m11]
---

# modern-m11-ecosystem

## 定義

C++ 生態工具鏈的核心思維模型：**如何構建和維護這個項目？**

## 核心問題

**如何構建和維護這個項目？**

- **Build**: CMake (Standard)
- **Deps**: vcpkg 或 Conan (不要手動安裝)
- **Quality**: Clang-Tidy + AddressSanitizer

## 關鍵要點

- CMake 是 C++ 標準構建系統生成器，幾乎所有主流項目都在用
- vcpkg：微軟出品，基於源碼的 C++ 包管理器（CMake 集成好）
- Conan：Python 包管理器生態，擅長二進制緩存
- AddressSanitizer (ASan)：`fsanitize=address` 捕捉 90% 的內存錯誤（洩漏、越界、使用後釋放）
- Clang-Tidy：C++ 靜態分析工具 + linter，自動檢查常見 bug 和風格問題
- 可重現構建依賴於 CMake + manifest (vcpkg.json) 的組合

## 思維框架

1. **Is the build reproducible?** Yes → CMake + Manifest (vcpkg.json). No → Manual paths (Bad).
2. **Are you checking for bugs?** `fsanitize=address` (ASan) catches 90% of memory errors.

## 相關概念

- [[entities/cpp/modern/modern-m10-performance]] — 性能優化需要測量工具（benchmark）
- [[entities/cpp/modern/modern-m01-ownership]] — AddressSanitizer 幫你發現內存所有權問題
- [[entities/cpp/cpp-safety]] — 工具鏈是 C++ 安全性的基礎設施
- [[entities/cpp/modern/modern-m06-error-handling]] — 調試工具幫你發現錯誤處理問題
- [[entities/cpp/modern/modern-m15-anti-pattern]] — 很多 anti-pattern 可被 Clang-Tidy 檢測

## Source

- [[sources/github-modern-cpp-skills-m11]]