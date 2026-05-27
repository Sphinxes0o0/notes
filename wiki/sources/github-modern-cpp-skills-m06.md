---
type: source
source-type: github
title: "m06-error-handling — C++ Master: Error Handling Mental Model"
author: "Sphinx Shi"
date: 2026-05-27
size: small
path: raw/Modern-Cpp-Skills/m06-error-handling/SKILL.md
summary: "C++ Master-level skill for error handling. Core question: Is this error recoverable? Covers std::optional, std::expected, exceptions, asserts, noexcept, and [[nodiscard]]."
tags: [cpp, master, error-handling, exceptions, expected]
---

# m06-error-handling — C++ Error Handling

## 核心內容

**Core Question**: 這個錯誤可恢復嗎？

- **Yes (Local)**: `std::expected<T, E>` 或返回碼
- **Yes (Distant)**: 異常 (`throw`)
- **No (Bug)**: `assert` 或 `std::terminate`

### Error → Design 映射

| 錯誤 | 設計問題 |
|------|----------|
| Uncaught Exception | 是否忘記了 catch，或在 `noexcept` 中拋出？ |
| Silent Failure | 是否忽視了返回碼？（用 `[[nodiscard]]`） |
| Destructor Throw | 是否在析構函數中拋出異常？ |

### 思維框架

1. **Is absence valid?** Yes → `std::optional<T>`.
2. **Does caller need details?** Yes → `std::expected<T, E>` or Exception. No → `bool` or `std::optional`.
3. **Is it a logic error (bug)?** Yes → `assert()` or `std::terminate()`. Do not throw for bugs.

### Quick Reference

| Mechanism | Cost (Happy) | Cost (Sad) | Use When |
|-----------|--------------|------------|----------|
| `std::optional` | Branch | Branch | Return may be empty. |
| `std::expected` | Branch | Branch | Recoverable error (Parsing). |
| Exception | Zero | Huge | Rare IO/Resource errors. |
| Assert | Zero (Release) | Abort | Logic bugs / Invariants. |

## 相關 Entity

- [[entities/cpp/modern/modern-m06-error-handling]]
- [[entities/cpp/modern/modern-m13-domain-error]]
- [[entities/cpp/modern/modern-m12-lifecycle]]