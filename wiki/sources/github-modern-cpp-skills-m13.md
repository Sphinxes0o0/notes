---
type: source
source-type: github
title: "m13-domain-error — C++ Master: Domain Errors Mental Model"
author: "Sphinx Shi"
date: 2026-05-27
size: small
path: raw/Modern-Cpp-Skills/m13-domain-error/SKILL.md
summary: "C++ Master-level skill for domain errors. Core question: Who catches this? Covers std::runtime_error, std::logic_error, std::expected, exception hierarchies, and system errors with std::error_code."
tags: [cpp, master, domain-error, exception-hierarchy]
---

# m13-domain-error — C++ Domain Errors

## 核心內容

**Core Question**: 誰來捕獲這個？

- **Exception**: 繼承 `std::runtime_error`
- **System Error**: `std::error_code` (OS codes)

### 思維框架

1. **Is it a domain event?** `InsufficientFunds` is an exception type.
2. **Does it have context?** "File not found" needs "Which file?" → `struct FileError : std::runtime_error { path p; }`

### Quick Reference

| Pattern | Use Case |
|---------|----------|
| `std::runtime_error` | Base for most failures. |
| `std::logic_error` | Bug (violation of precondition). |
| `std::expected` | Visible failure path. |

## 相關 Entity

- [[entities/cpp/modern/modern-m13-domain-error]]
- [[entities/cpp/modern/modern-m06-error-handling]]
- [[entities/cpp/modern/modern-m09-domain]]