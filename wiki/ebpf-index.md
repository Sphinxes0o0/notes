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
| [[entities/linux/ebpf/ebpf-container-audit]] | 容器审计 | saBPF/LSM/Cgroup/Sidecar模式 | saBPF论文 |
| [[entities/linux/ebpf/ebpf-security-observability]] | 安全可观测性 | 四金信号/Cilium/K8s可观测性 | O'Reilly报告 |

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
ebpf-security-observability ───→ kernel-net-index (K8s网络/四金信号)
       │
ebpf-ecosystem ───────→ tools-index (bpftool/tcpdump)
```

## Sources

| Source | Description | Type | Date |
|--------|-------------|------|------|
| [[sources/pdf-ebpf-books]] | 3册eBPF书籍：龙蜥白皮书(架构/CO-RE)、技术实践(XDP/TC)、Liz Rice入门 | pdf | 2026-05 |
| [[sources/pdf-ebpf-papers]] | 10篇eBPF论文：Thomas Graf微内核愿景/微服务感知OS/Apple Falco/Google KRSI/Black Hat Rootkit/UFMG XDP/生态库/saBPF容器审计/Isovalent安全可观测性/PTPsec | pdf | 2026-05 |
| [[sources/pdf-bpf-rethinking-kernel]] | Rethinking Linux Kernel (Thomas Graf)：eBPF微内核愿景 | pdf | 2020 |
| [[sources/pdf-bpf-microservices-os]] | BPF Microservices-aware OS (Thomas Graf)：Cilium/Hubble功能矩阵 | pdf | 2018 |
| [[sources/pdf-google-bpf-audit]] | BPF Security Auditing at Google (Brendan Jackman)：KRSI/Atomics/Ringbuf | pdf | 2021 |
| [[sources/pdf-falco-apple]] | Falco at Apple (eBPF Summit)：BPF vs内核模块/Syscall监控 | pdf | 2021 |
| [[sources/pdf-ebpf-library-ecosystem]] | eBPF Library Ecosystem (Kyle Quest)：Go/Rust/Python/C生态库评测 | pdf | 2021 |
| [[sources/pdf-xdp-fast-packet]] | XDP Fast Packet Processing (UFMG)：BPF指令格式/~20Mpps性能 | pdf | 2021 |
| [[sources/pdf-infocom-ptpsec]] | PTPsec (INFOCOM 2024)：IEEE 1588延迟攻击检测与缓解 | pdf | 2024 |

## Quick Navigation

- **入门**：[[entities/linux/ebpf/ebpf-overview]] → Verifier/JIT/Maps 核心概念
- **网络**：[[entities/linux/ebpf/ebpf-xdp]] (XDP) + [[entities/linux/ebpf/ebpf-networking]] (TC/Cilium)
- **安全**：[[entities/linux/ebpf/ebpf-security]] (Falco/LSM/Rootkit) + [[entities/linux/ebpf/ebpf-container-audit]] (saBPF) + [[entities/linux/ebpf/ebpf-security-observability]] (四金信号)
- **开发**：[[entities/linux/ebpf/ebpf-ecosystem]] → BCC/libbpf/cilium-ebpf/aya
- **工具**：bpftool / iproute2 / bpftrace

## Key Stats

- **Total Sources**：17 PDFs (3 books + 10 papers + 2 individual paper pages) + 8 additional individual paper pages
- **Total Entities**：7
- **Kernel Version**：eBPF 从 Linux 3.18 广泛可用，CO-RE 从 4.18+ 广泛可用
- **CO-RE 依赖**：CONFIG_DEBUG_INFO_BTF=y (Ubuntu 20.10+ 默认开启)
- **Individual Papers**：10 papers from raw/PDFs/papers/ now have dedicated source pages
