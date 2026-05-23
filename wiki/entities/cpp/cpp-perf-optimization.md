---
type: entity
tags: [cpp, performance, optimization, cpu-cache, simd, profiling]
created: 2026-05-22
sources: [pdf-cpp-slides, pdf-cpp-perf-memory, pdf-cpp-modern-books]
---

# C++ Performance Optimization

## Definition

C++ performance optimization is the practice of **reducing CPU cycles, memory bandwidth usage, and memory allocation overhead** through a combination of hardware-aware programming, algorithmic improvements, and profiling-driven refinement. The foundational principle: **measure first, optimize only what matters**.

## Foundational Principles

### Amdahl's Law
System speedup is limited by the **non-parallelizable fraction**:

```
S = 1 / ((1 - P) + P/N)
```

Where `P` = parallelizable fraction, `N` = number of parallel resources. Focus optimization effort on the serial bottleneck.

### 90/10 Rule
90% of execution time is spent in **10% of code** (the "hot path"). Optimization should target measurable hotspots, not intuition.

### Optimization Strategies (from Kurt Guntheroth's *Optimized C++*)

1. Use a good compiler with optimization flags (`-O2`/`-O3`, LTO, PGO)
2. Use better algorithms — O(n log n) vs O(n²) matters more than micro-optimizations
3. Use better libraries — std::vector over raw arrays, std::string over C strings
4. Reduce memory allocation and copying — move semantics, object pools, pre-allocation
5. Remove unnecessary computations — hoisting loop-invariant code
6. Use better data structures — cache-friendly layouts, avoid indirection
7. Increase concurrency — parallelize independent work
8. Optimize memory management — allocator selection, memory pools

## Memory Hierarchy Optimization

### Cache Levels (x86/x64)

| Level | Latency | Bandwidth | Capacity | Key Techniques |
|-------|---------|-----------|---------|----------------|
| L1 | ~1–4 cycles | ~150 GB/s | 64–512 KB/core | Data locality, alignment, false sharing avoidance |
| L2 | ~10 cycles | ~50–100 GB/s | 256 KB–16 MB/core | Loop unrolling, prefetching, avoid cross-cache-line access |
| L3 | ~20–50 cycles | ~40–80 GB/s | 8–512 MB (shared) | NUMA awareness, thread data placement |
| DRAM | ~60–120 ns | ~20–60 GB/s | GB-level | Memory pools, avoid frequent alloc/free |

### Cache Line
Cache lines are **64 bytes** on modern x86. A single load instruction loads the entire line. Key implications:
- **False sharing**: two threads modifying different variables on the same cache line cause cache line invalidation storms (avoid with padding or `std::hardware_destructive_interference_size`)
- **Strided access**: accessing every 64th byte thrashes the cache; sequential access is vastly superior
- **Write policies**: write-back is common; be aware of write-combining

### NUMA (Non-Uniform Memory Access)
In multi-socket systems, local memory is faster than remote memory:
- Use `numactl` or libnuma to bind threads to cores and allocate local memory
- Interleave allocations across memory channels for bandwidth-intensive workloads

### Memory Bandwidth
DRAM bandwidth is limited and often the bottleneck for large data copies:
- Avoid unnecessary memory copies (use `std::move`, `std::span`, views)
- Use memory pools to reduce `new`/`delete` overhead
- Batch operations to amortize per-item overhead

## CPU-Side Optimization

### Registers
- x86-64 has 16 general-purpose registers
- Simple, tight loops fully registerize — compilers optimize these aggressively
- Avoid excessive local variables or complex control flow that inhibits register allocation

### Instruction-Level Parallelism
- **Pipelining**: CPUs overlap execution of multiple instructions
- **Superscalar**: CPUs issue multiple instructions per cycle
- **Out-of-order execution**: CPU reorders independent instructions
- Data dependencies (RAW hazards) break ILP — keep dependent chains short

### SIMD (Single Instruction, Multiple Data)
- Process multiple data elements per instruction (e.g., AVX-512: 512-bit = 16 floats × 32-bit)
- Use when processing large arrays: image processing, numerical computation, parsers
- `std::experimental::SIMD` (C++26 will have `std::simd`), or intrinsics (`<immintrin.h>`)
- Profile to verify: SIMD overhead can exceed benefit for small datasets

### Branch Prediction
- CPUs predict branch targets to keep the pipeline full
- Mispredictions cause pipeline flushes (~15–20 cycle penalty)
- Patterns: use branchless alternatives for simple conditions; ensure hot code is contiguous in memory

## Profiling Tools

### `perf` (Linux)
Hardware PMU events:
- `cpu-cycles`, `instructions` — basic efficiency
- `cache-misses`, `L1-dcache-load-misses` — cache behavior
- `branch-misses` — branch predictor effectiveness
- `context-switches` — OS overhead

Commands:
- `perf stat` — event counting
- `perf record` — sampling profiler
- `perf report` — annotate with source/assembly

### eBPF (`bcc`, `bpftrace`)
Dynamic kernel/userspace tracing without instrumenting code:
- `kprobes`/`kretprobes` — kernel function entry/return
- `uprobes`/`uretprobes` — user-space function entry/return
- `tracepoints` — stable kernel ABI trace points
- `perf_events` — hardware PMU sampling

### Intel Processor Trace (IPT)
Hardware-level control-flow tracing:
- Sub-ns timing resolution
- Captures taken/not-taken for every conditional branch, indirect jump target
- Use `perf intel-pt` to record and decode

### PolarDB Fast Stack
Async stack dumping with 1/131th overhead of `pstack` (14% QPS impact vs. 100% for `pstack`).

## Relationship to Existing Entities

- [[entities/cpp/move-semantics]] — `std::move` eliminates unnecessary copies of large objects
- [[entities/cpp/constexpr]] — move computation to compile time; zero runtime cost
- [[entities/cpp/cpp-stl-containers]] — `std::vector` cache-friendly vs `std::list`; `reserve()` prevents reallocation
- [[entities/cpp/cpp-memory-management]] — 内存管理深入分析
- [[entities/cpp/cpp-memory-model]] — Memory ordering and atomics for concurrent access
- [[entities/cpp/cpp-stl-algorithms]] — `std::for_each` with SIMD, algorithms vs hand-written loops
- [[entities/cpp/concurrency]] — parallel execution requires understanding Amdahl's Law; `std::thread` for parallelism
- [[entities/cpp/if-constexpr]] — compile-time branch elimination reduces instruction cache pressure

## Sources

- [[sources/pdf-cpp-perf-memory]] — C++ 性能优化与内存管理 4 册
- [[sources/pdf-cpp-modern-books]] — Modern C++ 书籍的性能章节
