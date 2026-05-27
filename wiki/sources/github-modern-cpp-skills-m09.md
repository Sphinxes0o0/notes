---
type: source
source-type: github
title: "m09-domain — C++ Master: Domain Modeling (DDD) Mental Model"
author: "Sphinx Shi"
date: 2026-05-27
size: small
path: raw/Modern-Cpp-Skills/m09-domain/SKILL.md
summary: "C++ Master-level skill for domain modeling (DDD). Core question: Identity or Value? Covers Value Objects, Entities, Aggregates, Repository pattern, Pimpl, and invariant enforcement."
tags: [cpp, master, domain-modeling, ddd, entity-value-object]
---

# m09-domain — C++ Domain Modeling (DDD)

## 核心內容

**Core Question**: 身份還是值？

- **Value Object**: 由屬性定義 (`Color`, `Money`) — 比較相等性，可拷貝
- **Entity**: 由身份定義 (`User`, `Socket`) — 由 ID 判等，通常不可拷貝

### Error → Design 映射

| 錯誤 | 設計問題 |
|------|----------|
| Data Inconsistency | 公共字段是否允許無效狀態？ |
| Object Slicing | 是否按值傳遞了多態實體？ |
| Header Hell | 是否泄露了實現細節？（用 Pimpl） |

### 思維框架

1. **Is it copyable?** Yes → Value Type (Rule of Zero, defaults). No → Entity (Delete copy ctor, enable move).
2. **Does it have invariants?** Yes → `class` with private data + public methods. No → `struct` (POD).
3. **Does it own others?** Aggregate Root → Owns children via `std::vector` / `unique_ptr`.

### Quick Reference

| Pattern | C++ Implementation |
|---------|-------------------|
| Value Object | `struct` + `operator<=>`. |
| Entity | `class` + Deleted Copy + ID field. |
| Repository | Pure Virtual Interface (`virtual ... = 0`). |
| Aggregate | Parent class owning children. |

## 相關 Entity

- [[entities/cpp/modern/modern-m09-domain]]
- [[entities/cpp/modern/modern-m05-type-driven]]
- [[entities/cpp/modern/modern-m01-ownership]]