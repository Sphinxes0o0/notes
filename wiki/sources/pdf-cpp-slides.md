---
type: source
created: 2026-05-22
source-type: pdf
title: "C++ Slides Collection (2025)"
author: "Bloomberg, Adobe, 阿里云"
date: 2025-12-13
size: medium
path: raw/PDFs/slides/
summary: "5 C++ conference talks covering reflection, safety/defense-in-depth, and LLM inference framework construction"
---

# C++ Slides Collection (2025)

## Core Content

### 彭博 C++反射的核心原理实践与最新进展
**Speakers:** Meya Zhao, Henry Haorong Yang, Zhenchao Lin (Bloomberg Feeds Engineering)
**Conference:** CPP-Summit, December 2025

C++26 reflection (P2996) introduces three core facilities:
- **`^^` operator** — lifts an expression into the reflection domain, yielding a `std::meta::info` value at compile time
- **`[: expr :]` splice operator** — splices a `std::meta::info` back into the source code at compile time
- **Meta functions** — e.g., `std::meta::nonstatic_data_members_of(type, access_context)` returns a vector of member descriptors

Use case: Bloomberg uses reflection to auto-generate serialization formatters. Instead of writing separate `std::formatter` specializations for each message type, a single `json_formatter` template uses reflection to iterate members at compile time. This eliminates the need for hand-written per-type formatters and keeps serialization logic DRY.

`access_context::unchecked()` bypasses private-member access checks. The `access_context::current()` and `access_context::unprivileged()` provide different access levels for querying member visibility.

Note: All meta functions are `consteval` — C++ reflection is purely compile-time.

### David Sankel 大规模安全 C++：纵深防御策略
**Speaker:** David Sankel (Adobe Principal Scientist, WG21 committee)
**Conference:** 2025

Memory safety vulnerabilities account for **70% of zero-day CVEs** across Microsoft, Google Android, Chromium, and Mozilla. The root cause is not logic errors but memory management.

**Defense-in-Depth ("Swiss Cheese") Model — 4 Layers:**

1. **Isolate (Sandboxing)** — Run parsers of untrusted input in sandboxed processes (Sandbox2, WebAssembly/RLBox, OS-level seccomp)
2. **Harden (Compiler + Library Flags)** — `-ftrivial-auto-var-init=pattern`, `-D_FORTIFY_SOURCE=3`, `-fstack-clash-protection`; libc++ hardening modes (`_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_FAST`)
3. **Detect (Sanitizers + Fuzzing)** — ASan, UBSan, TSan in CI; fuzz targets for public APIs
4. **Prevent (Modern C++ Idioms)** — Write code that cannot exhibit undefined behavior; prefer range-for over index loops; avoid raw pointers; C++26 Contracts (`pre!`, `post`, `contract_assert`)

Key insight: New code is the primary source of vulnerabilities. If organizations stop introducing memory-safety bugs in new code, the problem eventually decays.

### John Lakos C++ "安全优先"开发模式演进与路线图
**Speaker:** John Lakos (Bloomberg Senior Architect, Office of the CTO)
**Conference:** CPP-Summit, December 2025

**Bloomberg's three-part strategy for C++:** Safety, Health, Efficiency.

**Safety dimensions:**
- Functional safety — contracts, pre/postconditions
- Language safety — eliminating UB
- Memory safety — preventing use-after-free, buffer overflow
- Lifetime safety — ensuring objects are valid when accessed
- Data-race safety — `std::atomic`, thread-safe memory model

**C++26 Contracts MVP (P2900):**
- `pre!` / `pre` — hardened/default preconditions (caller must satisfy)
- `post` — postconditions (function guarantees)
- `contract_assert` / `contract_assert!` — internal assertions

Timeline: Bloomberg BDE team invented contracts in 2003; they were removed from C++20; SG21 was formed; C++26 MVP is now being prototyped in Clang and GCC.

Key goal: Every C++ program can be compiled such that no core-language UB is ever executed — without changing source code.

### 吴晓飞 高性能CC++系统性能优化：从理论到实践
**Speaker:** 吴晓飞 (阿里云 RDS MySQL 内核负责人)
**Topic:** Performance optimization using PolarDB TPCC as case study

**Theory:**
- **Amdahl's Law** — overall speedup limited by non-parallelizable fraction
- **90/10 Rule** — 90% of time spent in 10% of code; measure first, then optimize

**Memory Hierarchy Optimization:**
- Register allocation: keep hot variables in registers; simple loops fully registerize
- L1/L2/L3 cache: data locality, alignment, avoid false sharing (different threads modifying different variables on same cache line → cache line invalidation storms)
- NUMA: local vs remote memory access latency difference; `numactl` / libnuma
- DRAM: bandwidth limited; sequential access >> random; use memory pools

**Tools:** `perf` (PMU events: cache misses, branch mispredictions), eBPF (`bcc`, `bpftrace`) for kernel/userspace dynamic tracing, Intel Processor Trace (IPT) for sub-ns control-flow tracing, PolarDB Fast Stack (async stack dumping, 1/131th overhead of `pstack`)

### 刘童旋 基于C++构建大模型推理优化框架xLLM实践
**Speaker:** 刘童旋
**Topic:** xLLM — C++ inference optimization framework for e-commerce LLM workloads

**Architecture (deeply decoupled, distributed):**
- **PD Separation** — Prefill and Decode nodes; dynamic PD ratio adjustment; KV Cache migration between nodes; 1.59X–2.2X throughput improvement
- **EPD Separation** — Encoder/Prefill/Decode each scheduled on heterogeneous instances; up to 3.7X throughput improvement
- **Unified online/offline scheduling** — SLO-aware; evict offline KV Cache under load; 3X offline throughput improvement

**Runtime optimizations:**
- Multi-layer pipeline: CPU scheduling and GPU/NPU compute run asynchronously; different layers overlap compute and communication; different execution units (Cube/Vector/MTE) run in parallel
- **xTensor** — optimized GPU memory management
- Speculative inference optimization

**C++ advantages:** Low-latency scheduling, custom operators, efficient scheduler implementation, direct hardware control for production LLM serving.

## Key Cross-Cutting Themes

- **C++26 is the safety release** — Contracts, reflection, and better UB guarantees all land in C++26
- **Defense in depth** — No single layer is sufficient; combine language features, tooling, and process
- **Performance = measurement + hardware awareness** — Always profile before optimizing; understand memory hierarchy
- **C++ for production AI** — C++ enables fine-grained control needed for LLM inference that Python/languages cannot match

## Related Pages
- [[entities/cpp/cpp-reflection]] — compile-time reflection in C++26
- [[entities/cpp/cpp-safety]] — safety-first development and defense-in-depth
- [[entities/cpp/cpp-perf-optimization]] — CPU cache, SIMD, profiling
- [[entities/cpp/cpp-llm-inference]] — C++ for LLM inference frameworks
