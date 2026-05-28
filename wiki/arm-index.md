---
type: index
tags: [arm, architecture, cpu, embedded, iot]
created: 2026-05-23
---

# ARM Architecture

> ARM processor architecture, microarchitecture, and security extensions

## Entities

| Entity | Description | Tags |
|--------|-------------|------|
| [[entities/arm/armv8-architecture]] | ARMv8-A: 64-bit ISA, AArch64/AArch32, Exception Levels, VMSAv8-64 | arm, architecture, armv8, aarch64 |
| [[entities/arm/arm-cortex-a9]] | Cortex-A9: out-of-order, superscalar, NEON SIMD, multiprocessing (SCU/GIC) | arm, cortex-a9, cpu, architecture |
| [[entities/arm/computer-architecture]] | Computer Architecture: Amdahl's law, memory hierarchy, DSA, chiplets | architecture, computer-science, cpu, performance |
| [[entities/cpu-architecture]] | CPU Architecture: ISA设计(RISC/CISC/VLIW)、微架构(流水线/超标量/乱序执行)、分支预测 | computer-architecture, CPU, ISA, pipeline |
| [[entities/memory-hierarchy]] | Memory Hierarchy: 寄存器→Cache→DRAM→SSD存储层次、Cache映射、TLB、一致性协议MESI | memory-hierarchy, cache, TLB, storage |
| [[entities/arm/trustzone-op-tee]] | TrustZone & OP-TEE: TEE, Secure World, Monitor Mode, ATF boot stages | security, arm, trustzone, tee, op-tee, mobile-security |

## Sources

| Source | Description | Date |
|--------|-------------|------|
| [[sources/pdf-arm-architecture]] | ARM体系结构4册：Armv8/Armv9参考手册、Cortex-A9 TRM、量化研究方法 | 2026-05 |

## Cross-References

- [[qemu-index]] — QEMU simulates ARM Cortex-A9 and ARMv8-A CPUs
- [[os-index]] — ARM processors run Linux OS with MMU, cache coherency
- [[kernel-virt-index]] — ARM virtualization extensions (EL2, KVM)
- [[security-index]] — TrustZone for hardware security isolation
