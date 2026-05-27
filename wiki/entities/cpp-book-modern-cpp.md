---
type: entity
tags: [cpp, modern-cpp, cpp20, cpp23, concepts, modules, coroutines, ranges]
created: 2026-05-27
sources: [pdf-book-modern-cpp]
---

# The Book of Modern C++ (第二版)

## Definition

The Book of Modern C++ (第二版) is a 1053-page collaborative book on C++20/23 advanced topics, written by multiple C++ experts and published free online (github.com/lkimuk/the-book-of-modern-cpp). It covers everything from fundamental concepts to bleeding-edge features, structured as multi-author chapters.

## Key Concepts

### C++20 Core Features

| Feature | Description |
|---------|-------------|
| **Concepts** | Compile-time constraints on template parameters; contracts for generic interfaces |
| **Modules** | Replacement for header files; compilation speed + encapsulation |
| **Coroutines** | Stackless async ( resumable functions); `co_await`, `co_yield`, `co_return` |
| **Ranges** | Unified composable views; `std::views::filter | std::views::transform` |
| **constexpr everything** | Allocating constexpr; compile-time `new`/`delete` |
| **std::format** | Type-safe formatting; Python f-string-like syntax |

### C++23 Progress

- **std::print**: formatted output to any stream
- **std::mdspan**: multi-dimensional array view
- **constexpr allocations**: compile-time dynamic memory (controversial but merged)

### Notable Chapters

**I. Basics:**
- Function overload resolution internals
- Monads in C++ (functional programming patterns)
- `static` keyword deep dive
- Move semantics and rvalue references
- ABI compatibility: "To Save C, We Must Save ABI"

**II. Modern C++:**
- Evolution of functions
- constexpr design evolution
- Aggregate initialization with parentheses

### Multi-Author Collaboration

Each chapter authored by a different expert — demonstrates C++ community knowledge-sharing model. Book itself is a case study in large-scale technical collaboration.

## Related Pages

- [[entities/cpp/cpp20-features]] — C++20核心特性（Concepts/Modules/Coroutines）
- [[entities/cpp/cpp-templates-v2]] — C++模板元编程
- [[cpp-index]] — Modern C++模块索引
- [[sources/pdf-cpp-modern-books]] — Modern C++书籍索引

## Source Details

- [[sources/pdf-book-modern-cpp]] — The Book of Modern C++ (第二版，2024)