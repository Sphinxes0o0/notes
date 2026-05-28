---
type: source
source-type: github
title: Modern C++ Features Reference (C++11/14/17/20/23)
author: Anthony Calandra
date: 2024
path: raw/github/modern-cpp-features/README.md
size: large
summary: "Comprehensive feature reference covering C++11 through C++23 — 100+ language and library features with examples. Anthony Calandra's curated reference."
created: 2024
tags: [cpp, modern-cpp]
---
# Modern C++ Features Reference (C++11/14/17/20/23)

## Overview

Comprehensive, example-driven reference of Modern C++ features spanning five standards:
- **C++23**: consteval if, deducing this, coroutines (library), std::expected, std::span, monadic optional
- **C++20**: concepts, three-way comparison (spaceship), coroutines, ranges, std::format, std::jthread, constinit
- **C++17**: std::variant, std::optional, std::any, if constexpr, structured bindings, parallel algorithms
- **C++14**: generic lambdas, variable templates, std::make_unique, relaxed constexpr
- **C++11**: move semantics, rvalue refs, lambdas, auto, constexpr, smart pointers, variadic templates, threads

## Core Content

### Language Features by Standard

| Standard | Key Language Features |
|----------|----------------------|
| C++23 | consteval if, deducing this, multidimensional subscript, range-for safety fixes |
| C++20 | coroutines, concepts, spaceship operator, designated initializers, constinit, explicit(bool) |
| C++17 | constexpr if, CTAD, structured bindings, inline variables, nested namespaces, folding expressions |
| C++14 | generic lambdas, lambda capture initializers, variable templates, decltype(auto), relaxed constexpr |
| C++11 | move semantics, rvalue refs, forwarding refs, lambdas, auto, decltype, constexpr, smart pointers |

### Library Features by Standard

| Standard | Key Library Features |
|----------|---------------------|
| C++23 | std::expected, std::unreachable, std::to_underlying, spanstream, stacktrace, monadic optional |
| C++20 | std::format, std::span, std::jthread, std::bit_cast, synchronized output stream, concepts library |
| C++17 | std::variant, std::optional, std::any, std::string_view, std::invoke, std::apply, std::filesystem |
| C++14 | std::make_unique, std::integer_sequence, user-defined literals for chrono |
| C++11 | std::move, std::forward, std::thread, std::async, std::tuple, std::chrono, type traits |

## Key Feature Groups

### Core Language
- **Move Semantics**: rvalue references, std::move, std::forward, move constructor/assignment, Rule of 5
- **Templates**: variadic templates, auto, decltype, forwarding references, CTAD, if constexpr, concepts
- **Lambdas**: capture lists, generic lambdas (C++14), capture initializers, template syntax (C++20), parameter pack capture
- **Type System**: auto, decltype, constexpr, consteval, strong enums, attributes, nullptr

### Library Abstractions
- **Smart Pointers**: unique_ptr, shared_ptr, weak_ptr, make_unique, make_shared, custom deleters
- **Concurrency**: std::thread, std::jthread, atomic, memory_order, locks, futures/promises
- **Range & Functional**: std::invoke, std::apply, std::bind_front, std::function alternatives
- **Type Utilities**: std::variant, std::optional, std::any, std::string_view, std::byte

### C++20+ Additions
- **Concepts**: named constraints, requires clauses, standard concepts library
- **Coroutines**: co_await, co_yield, co_return, stackless coroutines
- **Spaceship**: operator<=> synthesis, std::strong_ordering, std::weak_ordering, std::partial_ordering

## Source Files

- `raw/github/modern-cpp-features/README.md` — consolidated reference (this source)
- `raw/github/modern-cpp-features/CPP11.md` — C++11 features only
- `raw/github/modern-cpp-features/CPP14.md` — C++14 features only
- `raw/github/modern-cpp-features/CPP17.md` — C++17 features only
- `raw/github/modern-cpp-features/CPP20.md` — C++20 features only
- `raw/github/modern-cpp-features/CPP23.md` — C++23 features only

## Related Pages

- [[entities/cpp/modern-cpp/cpp-auto-type-deduction]] — auto, decltype, decltype(auto), forwarding refs
- [[entities/cpp/modern-cpp/cpp-move-semantics]] — move semantics, rvalue refs, std::move, std::forward
- [[entities/cpp/modern-cpp/cpp-lambda-expressions]] — lambdas, generic lambdas, captures
- [[entities/cpp/modern-cpp/cpp-smart-pointers]] — unique_ptr, shared_ptr, weak_ptr
- [[entities/cpp/modern-cpp/cpp-variadic-templates]] — variadic templates, parameter packs, fold expressions
- [[entities/cpp/modern-cpp/cpp-constexpr]] — constexpr, consteval, constexpr if, constexpr virtual
- [[entities/cpp/modern-cpp/cpp-concepts]] — concepts, requires, constraints
- [[entities/cpp/modern-cpp/cpp-structured-bindings]] — structured bindings, decomposition
- [[entities/cpp/modern-cpp/cpp-coroutines]] — coroutines, co_await, co_yield, co_return
- [[entities/cpp/modern-cpp/cpp-attributes]] — attributes, [[entities/cpp/nodiscard]], [[likely]], [[deprecated]]
- [[entities/cpp/modern-cpp/cpp-stl-optional-variant-any]] — std::variant, std::optional, std::any
- [[entities/cpp/modern-cpp/cpp-stl-functional]] — std::invoke, std::apply, std::bind_front, std::not_fn
- [[entities/cpp/modern-cpp/cpp-stl-string-view]] — std::string_view, starts_with, ends_with
- [[entities/cpp/modern-cpp/cpp-stl-format-span]] — std::format, std::span, std::spanstream
- [[entities/cpp/modern-cpp/cpp-concurrency]] — std::thread, std::jthread, atomic, memory_model
- [[sources/cpp-modern-skills]] — C++17 Skills + Master mental models (complementary)
- [[sources/pdf-cpp-modern-tutorial]] — Modern C++ Tutorial (C++11/14/17/20)
- [[sources/pdf-book-modern-cpp]] — The Book of Modern C++ (C++20/23)
