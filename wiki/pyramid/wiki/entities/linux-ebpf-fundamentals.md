---
type: entity
tags: [linux, ebpf, beginner, architecture, instruction-set]
created: 2026-05-27
sources: [pdf-ebpf-basics]
---

# eBPF Fundamentals

## Definition

eBPF (extended Berkeley Packet Filter) is a Linux kernel technology (3.18+) that enables sandboxed programs to run in kernel space with native execution speed, attached to configurable hook points. It evolved from classic BPF (network packet filtering) into a general-purpose in-kernel compute platform.

## Key Concepts

### BPF → eBPF Evolution

| Feature | BPF (classic) | eBPF (extended) |
|---------|----------------|-------------------|
| Origin | Linux 2.5 | Linux 3.18 |
| Registers | 2 (accumulator + index) | 11 × 64-bit (r0-r9, r10=sp) |
| Use case | Network filtering | Tracing/networking/security |
| JIT | No | Yes (all archs) |
| Maps | No | Yes (key-value store) |
| Context | Packet data | Arbitrary kernel data |

### Instruction Set Architecture

**7 instruction classes**: LD/LDX/ST/STX/ALU/ALU64/JMP
**Instruction format** (8-byte): `opcode(8) | dst_reg:4 | src_reg:4 | off:16 | imm:32`
**Registers**: r0=return, r1-r5=args, r6-r9=callee-saved, r10=stack pointer

### CO-RE (Compile Once, Run Everywhere)

- **BTF** (BPF Type Format): compact kernel type information
- `bpf_core_field_exists()`: runtime field existence check
- Linear fallback: most compatible → most complete program version

### Pinning Mechanism

BPF Maps/programs are kernel resources (anonymous inodes). Pinning exposes them at filesystem paths (typically `/sys/fs/bpf/`) for cross-process sharing without file descriptor inheritance.

## Related Pages

- [[entities/linux/ebpf/ebpf-overview]] — eBPF核心架构（详细）
- [[sources/pdf-ebpf-books]] — eBPF书籍索引
- [[sources/pdf-ebpf-technical-practice]] — eBPF技术实践白皮书
- [[entities/linux/kernel/index#networking]] — Linux网络子系统

## Source Details

- [[sources/pdf-ebpf-basics]] — eBPF基础（80页入门教程）
- [[sources/reading-ebpf-how-ebpf-work]] — eBPF深入理解：Verifier/JIT/Maps/Tail Call/XDP vs TC性能排名