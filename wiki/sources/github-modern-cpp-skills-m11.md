---
type: source
source-type: github
title: "m11-ecosystem — C++ Master: Ecosystem Mental Model"
author: Sphinx Shi
date: 2026-05-27
size: small
path: raw/Modern-Cpp-Skills/m11-ecosystem/SKILL.md
summary: "C++ Master-level skill for C++ ecosystem. Core question: How do I build and maintain this? Covers CMake, vcpkg, Conan, sanitizers (ASan/TSan/UBSan), and Clang-Tidy."
tags: [cpp, master, ecosystem, cmake, build-tool]
created: 2026-05-27
---
# m11-ecosystem — C++ Ecosystem

## 核心內容

**Core Question**: 如何構建和維護這個項目？

- **Build**: CMake (Standard)
- **Deps**: vcpkg 或 Conan (不要手動安裝)
- **Quality**: Clang-Tidy + AddressSanitizer

### 思維框架

1. **Is the build reproducible?** Yes → CMake + Manifest (vcpkg.json). No → Manual paths (Bad).
2. **Are you checking for bugs?** `fsanitize=address` (ASan) catches 90% of memory errors.

### Quick Reference

| Tool | Purpose |
|------|---------|
| CMake | Build System Generator. |
| vcpkg | MSFT Package Manager (Source based). |
| Conan | Python Package Manager (Binary caching). |
| ASan | Address Sanitizer (Memory bugs). |
| Clang-Tidy | Static Analysis / Linter. |

## 相關 Entity

- [[entities/cpp/modern/modern-m11-ecosystem]]
- [[entities/cpp/modern/modern-m10-performance]]
- [[entities/cpp/cpp-safety]]