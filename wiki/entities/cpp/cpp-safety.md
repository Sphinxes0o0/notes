---
type: entity
tags: [cpp, safety, security, defense-in-depth, contracts, cpp26]
created: 2026-05-22
sources: [pdf-cpp-slides]
---

# C++ Safety-First Development

## Definition

C++ safety-first development means prioritizing **prevention, detection, and containment of defects** — especially memory-safety vulnerabilities — through a combination of language features, tooling, coding practices, and architectural isolation. The goal is to make C++ code as safe by default as possible while preserving its performance advantages.

## The Problem

**70–94% of zero-day CVEs** across major software (Microsoft, Google Android, Chromium, Mozilla) are **memory-safety vulnerabilities**: buffer overflows, use-after-free, null dereferences, data races. The root cause is not logic errors but **undefined behavior (UB)** in the C++ type system.

Key insight (from David Sankel, Adobe): Organizations are not failing at logic — they are failing at memory management. Memory safety issues almost always arise from UB. In C++, UB is not just a bug; it is a security vulnerability.

## Defense-in-Depth: The "Swiss Cheese" Model

No single safety measure is sufficient. Multiple layers are combined so that if one fails, the next catches the bug.

### Layer 1: Isolation (Sandboxing)
Contain the blast radius — if a parser is exploited, it cannot touch the rest of the system.
- **Sandbox2 / SAPI** (Google): C++ libraries running in restricted processes
- **WebAssembly (Wasm)**: Compile C++ to Wasm; run in lightweight sandbox (e.g., RLBox)
- **OS-level**: Seccomp-bpf (Linux), AppSandbox (Mac), AppContainer (Windows)

### Layer 2: Hardening (Compiler + Library Flags)
Low-cost, production-safe flags with negligible performance impact (<1%):
- `-ftrivial-auto-var-init=pattern` — initializes stack variables to a recognizable pattern; prevents uninitialized memory exploits
- `-D_FORTIFY_SOURCE=3` — detects buffer overflows in libc functions at compile and runtime
- `-fstack-clash-protection` — prevents stack clash attacks
- **libc++ hardening modes**:
  - `FAST` — security-critical preconditions (e.g., vector out-of-bounds); designed for production
  - `EXTENSIVE` — more checks, higher cost
  - `DEBUG` — full internal consistency; development only

### Layer 3: Detection (Sanitizers + Fuzzing)
Development-only tools that find bugs before they ship:
- **ASan** (Address Sanitizer): catches buffer overflows, use-after-free, double-free
- **UBSan**: catches integer overflow, bad shifts, alignment issues, undefined behavior
- **TSan** (Thread Sanitizer): catches data races
- **Fuzzing**: write fuzz targets for public APIs; libFuzzer, OneFuzz, ClusterFuzz

### Layer 4: Prevention (Modern Idioms + C++26 Contracts)
Write code that **cannot exhibit UB**:
- Prefer range-for loops over index loops (guaranteed bounds safety)
- Use `std::span` instead of pointer+size pairs
- Avoid raw `new`/`delete`; use smart pointers
- Prefer value semantics and move semantics over shared ownership where possible
- Use **`std::atomic`** for lock-free data structures

## C++26 Contracts (P2900)

Contracts provide **language-level preconditions, postconditions, and assertions**:

```cpp
int safe_divide(int a, int b)
  pre!(b != 0)              // hardened precondition — cannot be disabled
  post(r: r == a / b)       // postcondition
{
    return a / b;
}
```

- `pre!` / `pre` — caller must satisfy before the call; `!` variant is "hardened" (always enabled)
- `post` — function guarantees postcondition on return
- `contract_assert!` / `contract_assert` — internal assertions

Contract syntax has a long history: Bloomberg BDE team invented contracts in 2003; removed from C++20; SG21 formed to carry it forward; C++26 MVP now being prototyped in Clang and GCC.

## Safety Dimensions (John Lakos's Framework)

Bloomberg categorizes safety into five dimensions:

| Dimension | Focus | Key Mechanisms |
|-----------|-------|----------------|
| Functional | Contracts, pre/post-conditions | C++26 Contracts |
| Language | No core-language UB | Contracts, sanitizers, coding standards |
| Memory | No buffer overflow, use-after-free | Smart pointers, RAII, ASan |
| Lifetime | Objects valid when accessed | Smart pointers, `std::optional` |
| Data-race | Safe concurrent access | `std::atomic`, threading library |

**Key goal**: Every C++ program can be built such that no core-language UB is ever executed — without changing source code.

## Relationship to Existing Entities

- [[entities/cpp/smart-pointers]] — prevent use-after-free and double-free; RAII-based resource management
- [[entities/cpp/raii]] — automatic cleanup via constructors/destructors; prevents resource leaks
- [[entities/cpp/concurrency]] — data-race safety via `std::atomic` and proper mutex usage
- [[entities/cpp/cpp20-features]] — C++20 Concepts can express preconditions (requires clauses)
- [[entities/cpp/cpp-reflection]] — reflection enables generating serialization without manual buffer management (avoids one class of UB)

## Action Plan (from David Sankel)

1. **New projects**: seriously consider Rust for safety-critical new code
2. **Existing C++**:
   - Isolate: sandbox parsers of untrusted input
   - Harden: enable `-ftrivial-auto-var-init` and standard library hardening today
   - Detect: use sanitizers in CI; add fuzz targets for public APIs
   - Prevent: teach the team that **UB = Security Vulnerability**
