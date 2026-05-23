---
type: source
created: 2026-05-22
source-type: pdf
sources: [pdf-cpp-slides]
tags: [cpp, slides]
title: "C++ Slides Collection (2025)"
author: "Bloomberg, Adobe, 阿里云"
date: 2025-12-13
size: medium
path: raw/PDFs/slides/
summary: "5 C++ conference talks covering reflection (Bloomberg), safety/defense-in-depth (Adobe, Bloomberg), performance optimization (Alibaba PolarDB), and LLM inference framework xLLM"
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
**Speaker:** David Sankel (Adobe Principal Scientist, WG21 committee, Boost Foundation Director)
**Conference:** CPP-Summit, December 2025

Memory safety vulnerabilities account for **70% of zero-day CVEs** across Microsoft, Google Android, Chromium, and Mozilla. The root cause is not logic errors but memory management.

**Defense-in-Depth ("Swiss Cheese") Model — 4 Layers:**

1. **Isolate (Sandboxing)** — Run parsers of untrusted input in sandboxed processes: Sandbox2/SAPI (Google), WebAssembly/RLBox (sandboxed compilation), OS-level seccomp-bpf, AppSandbox (Mac), AppContainer (Windows)
2. **Harden (Compiler + Library Flags)** — Low-cost production-safe flags (<1% perf impact): `-ftrivial-auto-var-init=pattern` (stack variable initialization), `-D_FORTIFY_SOURCE=3` (libc buffer overflow detection), `-fstack-clash-protection` (stack clash attacks); libc++ hardening modes (`FAST`/`EXTENSIVE`/`DEBUG`)
3. **Detect (Sanitizers + Fuzzing)** — ASan (buffer overflow/UAF), UBSan (integer overflow/alignment), TSan (data races) in CI; libFuzzer/OneFuzz/ClusterFuzz targets for public APIs
4. **Prevent (Modern C++ Idioms)** — Write code that cannot exhibit UB: prefer range-for over index loops, `std::span` over pointer+size, RAII over raw `new`/`delete`, value semantics over shared ownership

Key insight: **New code is the primary source of vulnerabilities.** If organizations stop introducing memory-safety bugs in new code, the problem eventually decays. Organizations are not failing at logic — they are failing at memory management.

### John Lakos C++ "安全优先"开发模式演进与路线图
**Speaker:** John Lakos (Bloomberg Senior Architect, Office of the CTO)
**Conference:** CPP-Summit, December 2025
**Abstract:** "The world runs on C++. For more than two decades, C++ has served as the workhorse of high-performance, low-power, and low-latency software. Its raw speed and unconstrained flexibility have made C++ the go-to language for large-scale software development."

**Motivation: C++ under pressure**
- Google leaving C++ for Rust, Microsoft no longer uniformly supporting WG21/C++, Adobe quietly moving new development to Rust
- Regulatory pressure from EU, governments, and cybersecurity organizations
- Goal: "Blunt any desire to migrate away from C++"

**Bloomberg's three-part strategy: Safe, Healthy, Efficient**
- **Safety:** Correctness (easy to get programs right) + Security (hard to create vulnerabilities)
- **Health:** Ecosystem support (Clang, GCC, MSVC, EDG; sanitizers, static analyzers, debuggers, fuzzers)
- **Efficiency:** Machine (run time, compile time, link time) + Human (development time, maintenance time)

**Safety dimensions:**
| Dimension | Focus | Key Mechanisms |
|-----------|-------|----------------|
| Functional | Contracts, pre/postconditions | C++26 Contracts |
| Language | No core-language UB | Contracts, sanitizers, coding standards |
| Memory | No buffer overflow, use-after-free | Smart pointers, RAII, ASan |
| Lifetime | Objects valid when accessed | Smart pointers, `std::optional` |
| Data-race | Safe concurrent access | `std::atomic`, threading library |

**C++26 Contracts MVP (P2900):**
- `pre!` / `pre` — hardened/default preconditions (caller must satisfy)
- `post` — postconditions (function guarantees)
- `contract_assert` / `contract_assert!` — internal assertions

**Contracts 20-year timeline:** Bloomberg BDE team invented contracts in 2003; BDE contracts widely used at Bloomberg (2004); productized (2009); open-sourced (2012); uniform contracts proposal failed in WG21; removed from C++20; SG21 formed; Bloomberg sponsors MVP prototyping in Clang and GCC (2024–2025).

Key goal: Every C++ program can be compiled such that no core-language UB is ever executed — without changing source code.

### 吴晓飞 高性能CC++系统性能优化：从理论到实践
**Speaker:** 吴晓飞 (阿里云 RDS MySQL 内核负责人)
**Topic:** Performance optimization using PolarDB TPCC as case study

**Theory:**
- **Amdahl's Law** — overall speedup limited by non-parallelizable fraction: S = 1/((1-P) + P/N)
- **90/10 Rule** — 90% of time spent in 10% of code; measure first, then optimize

**Memory Hierarchy Optimization (detailed latency/bandwidth table):**
| Level | Latency | Bandwidth | Key Techniques |
|-------|---------|-----------|----------------|
| Registers | ~0 cycles | Very high | Keep hot variables in registers; simple loops fully registerize |
| L1 Cache | ~1–4 cycles | ~150 GB/s | Data locality, alignment, avoid false sharing |
| L2 Cache | ~10 cycles | ~50–100 GB/s | Prefetching, loop unrolling, reduce cross-cache-line access |
| L3 Cache | ~20–50 cycles | ~40–80 GB/s | NUMA-aware multi-thread data layout |
| DRAM | ~60–120 ns | ~20–60 GB/s | Memory pools, avoid frequent alloc/free |
| SSD/NVMe | ~10–100 μs | ~1–8 GB/s | Async I/O, multi-threading, caching |

**Cache miss types:** Cold Miss (first access), Capacity Miss (cache too small), Conflict Miss (mapping collision). Write strategies: Write-Through vs Write-Back. False sharing is the "multi-thread performance optimization core battlefield."

**Tools:**
- **`perf`** — Linux PMU events: `cpu-cycles`, `instructions`, `cache-misses`, `L1-dcache-load-misses`, `branch-misses`, `context-switches`, `page-faults`. Commands: `stat` (counting), `record`/`report` (profiling), `top` (live)
- **eBPF (`bcc`, `bpftrace`)** — `kprobes`/`kretprobes` for kernel dynamic tracing, `uprobes`/`uretprobes` for userspace, tracepoints for stable kernel ABI
- **Intel Processor Trace (IPT)** — Hardware-level control-flow tracing with sub-ns timing; captures every conditional branch taken/not-taken
- **PolarDB Fast Stack** — Async stack dumping with 1/131th overhead of `pstack` (14% QPS impact vs 100%)

**Hardware benchmarking:** Use Google Benchmark, Intel MLC, fio for hardware characterization before optimization.

### 刘童旋 基于C++构建大模型推理优化框架xLLM实践
**Speaker:** 刘童璇 (Alibaba)
**Topic:** xLLM — C++ inference optimization framework for e-commerce LLM workloads
**Context:** E-commerce AI needs span generative AI (product image/video generation), agentic AI (customer service, inventory optimization), and physical AI (robotics/autonomous driving)

**Architecture (deeply decoupled, distributed):**
- **Adaptive PD Separation** — P and D nodes auto-switch identity based on Input/Output ratio; KV Cache and requests migrate smoothly between nodes. PD ratio is no longer static. **1.59X–2.2X throughput improvement** with SLO-aware scheduling outperforming Mini Load and Round Robin
- **EPD Separation** — Encoder/Prefill/Decode each scheduled on heterogeneous instances based on compute/memory characteristics and optimal batch sizes. **Up to 3.7X throughput improvement**
- **Unified online/offline scheduling** — Load drops → insert offline batch inference; load spikes → evict offline KV Cache, migrate offline requests. SLO-aware with priority-based scheduling. **3X offline throughput improvement with stable SLO**
- **Fault tolerance** — Fast KV Cache and request migration on node failure

**Runtime optimizations:**
- Multi-layer pipeline: CPU scheduling and GPU/NPU compute run asynchronously; different layers overlap compute and communication; different execution units (Cube/Vector/MTE) run in parallel. **5%–10% throughput improvement** (greater gain for smaller models)
- **xTensor** — optimized GPU memory management
- **Speculative inference optimization**
- **Global KV Cache pool** — shared across requests; enables KV Cache-based load balancing and failover

**Generative Recommendation:** xLLM generates 512–4096 semantic IDs per inference (beam width), producing complete item IDs over fixed steps using C++-implemented high-performance Scheduler, Filter mechanisms, and custom operators.

**Business Impact:**
- TP99 ↓ 50%, resource savings ~60%
- Model throughput ↑ 3X (laugh model), inference cost ↓ ~70%
- Multimodal throughput ↑ ~20X, labeling timeliness ↑ 10X+
- UCVR ↑ +5%, active user ratio ↑ +2%

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
