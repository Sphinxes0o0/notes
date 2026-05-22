---
type: source
created: 2026-05-22
source-type: pdf
title: "C++ Performance & Architecture Books"
author: "Kurt Guntheroth, John Lakos"
date: 2016-2019
size: medium
path: raw/PDFs/books/
summary: "Two books: Optimized C++ (string/algorithm/memory optimization techniques) and Large-Scale C++ Software Design (physical design, levelization, insulation)"
---

# C++ Performance & Architecture Books

## C++性能优化指南 (Optimized C++)

**Author:** Kurt Guntheroth
**Publisher:** O'Reilly / 人民邮电出版社
**Year:** 2016 (English), 2018 (Chinese)

### Core Strategies (from Ch. 1.5)

1. **Use a good compiler and use it well** — enable optimization flags (`-O2`/`-O3`, LTO, PGO)
2. **Use better algorithms** — O(n log n) vs O(n²); knowing when to use which
3. **Use better libraries** — std::vector vs raw array, std::string vs C strings
4. **Reduce memory allocation and copying** — move semantics, object pools, pre-allocation
5. **Remove unnecessary computations** — hoisting invariant computations, caching results
6. **Use better data structures** — cache-friendly layouts, avoiding indirection
7. **Increase concurrency** — parallelize independent operations
8. **Optimize memory management** — allocator selection, memory pools, arena allocation

### Key Insights (from Ch. 2: What Computers Do)

- **Memory is slow** — RAM latency ~60–120ns vs L1 cache ~1ns; caching is everything
- **Memory access is in chunks** — cache lines are 64 bytes; strided access is expensive
- **Instruction pipelining** — CPUs execute many instructions in parallel; data dependencies break pipelines
- **Not all statements cost the same** — a division costs ~3-40x more than an addition

### String Optimization Case Study (Ch. 4)

String performance issues:
- Dynamic allocation on every modification
- Excessive copying (pass-by-value, return-by-value)
- Unnecessary conversions between C strings and std::string

Optimization techniques:
- Use `std::string::reserve()` before repeated concatenation
- Pass strings by `const&`; use `std::move` on return
- Use iterators instead of index arithmetic
- Consider `std::string_view` to avoid copying substrings
- Replace `std::string` with `std::vector<char>` for performance-critical code

### Algorithm Optimization (Ch. 5)

- Know your input distribution — partially sorted data favors certain algorithms
- Use `std::partition` instead of separate find+sort when you only need top-k elements
- Precompute expensive results (memoization)
- Batch processing amortizes per-item overhead
- Cache-friendly data structures: arrays of structs (AoS) vs structs of arrays (SoA)

### Memory Allocation (implied from book structure)

- Object pools eliminate per-allocation overhead and fragmentation
- Arena allocators batch-delete all objects at once
- Custom allocators for specific usage patterns (e.g., pool allocator for fixed-size nodes)

---

## Large-Scale C++ Software Design

**Author:** John Lakos
**Publisher:** Addison-Wesley
**Year:** 1996

### Focus: Physical Design

While object-oriented design focuses on classes (logical design), physical design focuses on **components** — the smallest separately compilable units. Poor physical design causes:

- **Cyclic dependencies** — A includes B, B includes A; cannot link in any order
- **Excessive link-time dependencies** — a change in low-level code forces recompilation of everything
- **Excessive compile-time dependencies** — header changes propagate across the entire codebase
- **Name pollution** — global namespace congestion from large projects

### Key Concepts

**Component** = a pair of header file (.h) + implementation file (.c/.cpp). The fundamental unit of physical design.

**Uses relation** — A "uses" B if a change to B's interface potentially requires A to be recompiled or relinked.

**Physical hierarchy** — Components form acyclic dependency levels (Level 0 = no dependencies, Level 1 = only uses Level 0, etc.). The rule: dependencies can only go down in level number.

**Level numbers** — Assign integer levels to components based on their dependency structure. Higher-level components can be tested in isolation; lower-level components are tested later in the integration cycle.

**Insulation techniques** — Reduce compile-time coupling between components:
- **Protocol classes** — abstract interface + concrete implementation class; clients depend on abstract interface only
- **Handle/body (pimpl)** — split class into a handle (interface, heap-allocated body (implementation)); changing body does not require recompiling clients
- **Fully-insulating concrete classes** — wrap concrete class in a protocol
- Removing unnecessary includes via forward declarations

**Reasons for cyclic dependencies:**
1. **Enhancement** — adding a new feature requires A to know about B temporarily
2. **Convenience** — it's easier to include than to forward-declare
3. **Intrinsic** — two classes truly need each other (typically resolved by extracting a third class)

### Testing Implications

- Components at lower levels (fewer dependencies) can be tested in isolation earlier
- **Hierarchical and incremental testing** — test Level 0 components first, then Level 1 (which only depends on Level 0), etc.
- **Testability vs. testing** — testable design makes testing possible but doesn't guarantee testing happens

### Connection to Modern C++

- The `pimpl` idiom (pointer to implementation) is a direct descendant of Lakos's handle/body pattern
- The rule of minimizing header includes and using forward declarations remains central
- Component-level thinking maps to modern practices: header-only libraries vs. compiled libraries, unity builds, precompiled headers

## Related Pages
- [[entities/cpp/cpp-perf-optimization]] — CPU cache, SIMD, profiling, memory optimization
- [[entities/cpp/cpp-safety]] — defense-in-depth and safe C++ practices
- [[entities/cpp/cpp20-features]] — Modules in C++20 directly address physical design problems (separate compilation, header units)
- [[entities/cpp/smart-pointers]] — move semantics for avoiding memory copies
- [[entities/cpp/constexpr]] — compile-time computation to eliminate runtime overhead
