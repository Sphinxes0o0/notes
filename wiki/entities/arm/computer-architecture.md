---
type: entity
tags: [architecture, computer-science, cpu, performance]
created: 2026-05-23
sources: [pdf-arm-architecture]
---

# Computer Architecture

## Definition

Computer architecture is the science and art of designing computer systems — defining the ISA (Instruction Set Architecture), microarchitecture, memory hierarchy, and I/O system. The **quantitative approach**, pioneered by Hennessy & Patterson, uses empirical measurement and cost-benefit analysis to guide design decisions.

## Key Principles

### Design Metrics
- **Amdahl's Law**: Speedup limited by the non-parallelizable fraction
- **Moore's Law**: Transistor density doubles ~2 years (slowing)
- **Dennard Scaling**: Voltage/threshold scaling (ended ~2006) → Dark Silicon era
- **Power Wall**: CMOS power density limits clock frequency scaling

### Memory Hierarchy
| Level | Size | Latency | Bandwidth |
|-------|------|---------|-----------|
| L1 Cache | 32-64KB | 1-2 cycles | ~1TB/s |
| L2 Cache | 256KB-1MB | ~10 cycles | ~500GB/s |
| L3 Cache | 8-32MB | ~40 cycles | ~100GB/s |
| DRAM | 8-64GB | ~100ns | ~50GB/s |
| SSD | 256GB-2TB | ~10μs | ~5GB/s |

### Modern Trends
- **DSA (Domain-Specific Architecture)**: TPU, GPU, NPU — specialized for AI/ML
- **Chiplet Architecture**: Multi-die packaging (AMD Zen, Intel EMIB)
- **Heterogeneous Computing**: ARM big.LITTLE, Intel P/E cores
- **Near-Memory Computing**: Processing in/near DRAM (HBM-PIM, CXL)

## Related Pages

- [[entities/arm/armv8-architecture]] — ARMv8-A as a concrete ISA example
- [[entities/arm/arm-cortex-a9]] — Cortex-A9 microarchitecture
- [[os-index]] — OS interacts with architecture (context switch, MMU, cache)
- [[qemu-index]] — QEMU simulates computer architectures

## Source Details

- [[sources/pdf-arm-architecture]] — 计算机体系结构：量化研究方法 第五版 (Hennessy & Patterson)
