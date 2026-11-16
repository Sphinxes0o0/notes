---
type: entity
tags: [arm, cortex-a9, cpu, architecture]
created: 2026-05-23
sources: [pdf-arm-architecture]
---

# ARM Cortex-A9 Processor

## Definition

The Cortex-A9 is an ARMv7-A out-of-order, superscalar processor core introduced in 2008. It was one of the most widely deployed application processors in smartphones (Apple A5, Samsung Exynos 4, TI OMAP4) and remains a reference design for embedded multicore systems.

## Key Features

### Microarchitecture
- **Pipeline**: 8-11 stage, out-of-order, speculative execution
- **Issue**: Superscalar (partial dual-issue)
- **Branch Prediction**: Global history + BTAC, 8-entry return stack
- **NEON SIMD**: Advanced SIMD unit (128-bit)
- **FPU**: VFPv3-D16 or VFPv3-D32

### Memory Hierarchy
- **L1 I-Cache**: 16KB-64KB, 4-way set associative
- **L1 D-Cache**: 16KB-64KB, 4-way, write-back, pseudo-LRU
- **L2 Cache**: 128KB-8MB (optional), 8-16 way
- **TLB**: Micro-TLB (L1) + Main TLB (L2), 2-level walk

### Multiprocessing
- **SCU (Snoop Control Unit)**: Cache coherency between up to 4 cores
- **ACP (Accelerator Coherency Port)**: Coherent DMA
- **GIC (Generic Interrupt Controller)**: Interrupt distribution

## Related Pages

- [[entities/arm/armv8-architecture]] — Successor architecture (ARMv8-A)
- [[entities/arm/trustzone-op-tee]] — TrustZone Security Extensions (supported on Cortex-A9)
- [[qemu-index]] — QEMU supports Cortex-A9 emulation

## Source Details

- [[sources/pdf-arm-architecture]] — DDI0388H Cortex-A9 TRM
