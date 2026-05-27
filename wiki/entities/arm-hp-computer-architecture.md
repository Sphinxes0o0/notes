---
type: entity
tags: [computer-architecture, cpu, performance, roofline, amdahl, isa, pipeline]
created: 2026-05-27
sources: [pdf-computer-architecture-hp]
---

# Hennessy & Patterson Computer Architecture (量化研究方法 第五版)

## Definition

*Computer Architecture: A Quantitative Approach* by John L. Hennessy and David A. Patterson (H&P), 5th edition (2017), is the definitive textbook on modern computer architecture design. It pioneered the quantitative approach — using empirical measurement and analysis to guide architectural decisions — and is considered alongside CS:APP as one of the two pillars of computer systems education.

## Key Concepts

### Quantitative Design Methodology

| Technique | Application |
|-----------|-------------|
| **Roofline Model** | Plot compute intensity vs. peak memory bandwidth; identify whether a kernel is compute- or memory-bound |
| **Amdahl's Law** | Speedup = 1/((1-P)+P/N); optimize the parallelizable fraction P |
| **CPI Stalls Analysis** | Break down cycles per instruction into ideal CPI + stall cycles |
| **Little's Law** | Throughput = (concurrent work) / (latency) |

### Memory Hierarchy (Roofline)

| Level | Size | Latency | Bandwidth |
|-------|------|---------|-----------|
| L1 Cache | 32-64KB | ~1ns / 4 cycles | ~1TB/s |
| L2 Cache | 256KB-1MB | ~3ns / 12 cycles | ~500GB/s |
| L3 Cache | 8-32MB | ~10ns / 40 cycles | ~100GB/s |
| DRAM | 8-64GB | ~100ns | ~50GB/s |

### Instruction Set Architecture

- RISC vs. CISC: modern x86/ARM decode to RISC-like micro-ops
- ISA design trade-offs: register count, addressing modes, branch encoding
- Case studies: x86, ARMv8, RISC-V

### Modern Parallel Architectures

- **ILP** (Instruction-Level Parallelism): superscalar, out-of-order execution
- **TLP** (Thread-Level Parallelism): multi-core, SMT
- **DLP** (Data-Level Parallelism): SIMD, vector instructions
- **MLP** (Memory-Level Parallelism): prefetching, non-blocking caches

### Domain-Specific Architecture (DSA)

- **TPU**: systolic array, matrix multiply focus
- **GPU**: massive DLP, CUDA programming model
- **NPU**: DNN acceleration, low-precision arithmetic
- **CGRAs**: Coarse-Grained Reconfigurable Arrays

## Related Pages

- [[entities/arm/computer-architecture]] — 计算机体系结构基础
- [[entities/arm/armv8-architecture]] — ARMv8作为具体ISA案例
- [[entities/cpp/cpp-perf-optimization]] — CPU/缓存/SIMD优化（架构层面）
- [[sources/pdf-computer-systems-programmers-perspective]] — CS:APP（程序员视角）
- [[qemu-index]] — QEMU模拟各种体系结构

## Source Details

- [[sources/pdf-computer-architecture-hp]] — 计算机体系结构：量化研究方法（第五版）