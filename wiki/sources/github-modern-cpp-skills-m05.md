---
type: source
source-type: github
title: "m05-type-driven — C++ Master: Type-Driven Design Mental Model"
author: "Sphinx Shi"
date: 2026-05-27
size: small
path: raw/Modern-Cpp-Skills/m05-type-driven/SKILL.md
summary: "C++ Master-level skill for type-driven design. Core question: Can I make this bug a compile error? Covers strong types, phantom types, type-state pattern, builder pattern, and invalid state unrepresentable."
tags: [cpp, master, type-driven, strong-types, type-safety]
---

# m05-type-driven — C++ Type-Driven Design

## 核心內容

**Core Question**: 能否將這個 bug 變成編譯錯誤？

- **Primitive Obsession**: 用 `int` 表示 ID，用 `double` 表示金錢 — Bad
- **Strong Types**: `struct UserId`, `struct Money` — Good
- **Type State**: `Connection<OFF>` vs `Connection<ON>` — 狀態成為類型的一部分

### Error → Design 映射

| 錯誤 | 設計問題 |
|------|----------|
| Swapped arguments | 是否把 `width` 傳給了 `height`？（用 Strong Types） |
| Invalid State | 是否在關閉的文件上調用了 `read()`？（用 Type State） |
| Unit confusion | 是否混淆了米和英尺？（用 `Dist<Meters>` 模板標籤） |

### 思維框架

1. **Is this `int` unique?** Yes → Wrap in `struct`. `struct UserId { int val; }` prevents `process(OrderId)`.
2. **Does valid usage depend on order?** Yes → Encode state in type. `Builder::port()` returns `BuilderWithPort`.
3. **Are units compatible?** No → Template tag. `Dist<Meters>` + `Dist<Feet>` cannot mix.

### Quick Reference

| Pattern | Cost | Use When |
|---------|------|----------|
| Struct Wrapper | Zero | Distinct IDs, coordinates. |
| Enum Class | Zero | Type-safe flags (no implicit int conv). |
| Phantom Type | Zero | Tracking state without storage. |
| User Literal | Zero | `10_m`, `50_s`. |

## 相關 Entity

- [[entities/cpp/modern/modern-m05-type-driven]]
- [[entities/cpp/modern/modern-m09-domain]]
- [[entities/cpp/modern/modern-m06-error-handling]]