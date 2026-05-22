---
type: index
tags: [linux, ebpf, kernel, networking, security, xdp, tracing]
created: 2026-05-22
---

# eBPF Module Index

> eBPF (extended Berkeley Packet Filter) — Linux 内核沙盒虚拟机，实现内核可编程化，无需加载内核模块。
> 触发方式：事件驱动（系统调用/网络包/函数入口出口/tracepoint）
> 核心保障：Verifier 静态校验 + JIT 原生性能编译

## Entities

| Entity | Domain | Key Concepts | Sources |
|--------|--------|-------------|---------|
| [[entities/linux/ebpf/ebpf-overview]] | 核心架构 | Verifier/JIT/Maps/Helpers/Tail Call/CO-RE/BTF | 书籍×3, 论文×7 |
| [[entities/linux/ebpf/ebpf-xdp]] | XDP 高速数据面 | XDP Actions/Modes/Offload/~20Mpps | 书籍, UFMG论文 |
| [[entities/linux/ebpf/ebpf-security]] | 安全监控与Rootkit | Falco/KRSI/LSM/Atomics/Ringbuf | Apple/Google论文, Black Hat |
| [[entities/linux/ebpf/ebpf-networking]] | 网络与Cilium | TC/sock_ops/Cilium/Hubble/Kubernetes | Thomas Graf论文×2 |
| [[entities/linux/ebpf/ebpf-ecosystem]] | 生态库与工具 | BCC/libbpf/cilium-ebpf/aya/bpftrace | 书籍, Kyle Quest论文 |

## Cross-Reference Map

```
ebpf-overview
  ├── ebpf-xdp (网络数据面)
  ├── ebpf-security (安全监控)
  ├── ebpf-networking (TC/Cilium)
  ├── ebpf-ecosystem (开发框架)
  ├── kernel-subsystems-index (crypto/locking/IPC/RCU)
  ├── kernel-net-index (sk_buff/Netfilter/TCP)
  └── kernel-protocols-index (TCP/IP/路由)
       │
ebpf-xdp ──────────────→ kernel-net-index (sk_buff层可见性)
       │
ebpf-security ─────────→ kernel-subsystems-index (LSM/seccomp)
       │
ebpf-networking ───────→ kernel-net-index (Netfilter/Conntrack)
       │                → kernel-protocols-index (L3-L4路由)
       │
ebpf-ecosystem ───────→ tools-index (bpftool/tcpdump)
```

## Sources

| Source | Description | Type | Date |
|--------|-------------|------|------|
| [[sources/pdf-ebpf-books]] | 3册eBPF书籍：龙蜥白皮书(架构/CO-RE)、技术实践(XDP/TC)、Liz Rice入门 | pdf | 2026-05 |
| [[sources/pdf-ebpf-papers]] | 7篇eBPF论文：Thomas Graf微内核愿景/Apple Falco/Google审计/Black Hat Rootkit/UFMG XDP/生态库评测 | pdf | 2026-05 |

## Quick Navigation

- **入门**：[[entities/linux/ebpf/ebpf-overview]] → Verifier/JIT/Maps 核心概念
- **网络**：[[entities/linux/ebpf/ebpf-xdp]] (XDP) + [[entities/linux/ebpf/ebpf-networking]] (TC/Cilium)
- **安全**：[[entities/linux/ebpf/ebpf-security]] (Falco/LSM/Rootkit)
- **开发**：[[entities/linux/ebpf/ebpf-ecosystem]] → BCC/libbpf/cilium-ebpf/aya
- **工具**：bpftool / iproute2 / bpftrace

## Key Stats

- **Total Sources**：10 PDFs (3 books + 7 papers)
- **Total Entities**：5
- **Kernel Version**：eBPF 从 Linux 3.18 广泛可用，CO-RE 从 4.18+ 广泛可用
- **CO-RE 依赖**：CONFIG_DEBUG_INFO_BTF=y (Ubuntu 20.10+ 默认开启)
