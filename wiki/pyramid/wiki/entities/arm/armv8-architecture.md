---
type: entity
tags: [arm, architecture, cpu, armv8, aarch64]
created: 2026-05-23
sources: [pdf-arm-architecture]
---

# ARMv8-A Architecture

## Definition

ARMv8-A is a 64-bit architecture introduced by Arm in 2011, adding the AArch64 execution state while maintaining backward compatibility with AArch32 (32-bit ARM). It is the foundation for modern mobile processors (Cortex-A), server CPUs (Neoverse), and embedded SoCs.

## Key Concepts

### Execution States
- **AArch64**: 64-bit mode with 31 general-purpose X registers (64-bit), SP_ELx, PC
- **AArch32**: 32-bit mode compatible with ARMv7-A, 16 general-purpose registers

### Exception Levels (ELs)

| Level | Typical Use | Privilege |
|-------|-------------|-----------|
| EL0 | Applications | Least |
| EL1 | OS Kernel (Linux) | — |
| EL2 | Hypervisor (KVM) | — |
| EL3 | Secure Monitor (ATF) | Highest |

### Memory Model
- **VMSAv8-64**: Virtual memory with 4KB/16KB/64KB page sizes
- **TTBR0/TTBR1**: Separate translation tables for user/kernel space
- **ASID**: Address Space ID for TLB tagging
- **Contiguous Bit**: Large page hints for TLB efficiency

### Extensions
- **Armv8.0-8.6**: Incremental ISA extensions (CRC, LSE, JSCVT, FP16, BTI, MTE, etc.)
- **Cryptographic Extension**: AES, SHA1/SHA256 instructions
- **SVE (Armv8.2+)**: Scalable Vector Extension for HPC/AI
- **SME (Armv9)**: Scalable Matrix Extension

## Related Pages

- [[entities/arm/trustzone-op-tee]] — TrustZone uses ARMv8 security extensions
- [[entities/arm/arm-cortex-a9]] — Predecessor ARMv7-A processor
- [[qemu-index]] — QEMU simulates ARMv8-A CPUs

## Source Details

- [[sources/pdf-arm-architecture]] — DDI0487Fc (Armv8) + DDI0487 M.a.a (Armv9.6)
