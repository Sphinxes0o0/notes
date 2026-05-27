---
type: entity
tags: [linux, ebpf, tools, cloud-native, anolis, tracing]
created: 2026-05-27
sources: [pdf-ebpf-technical-practice]
---

# eBPF Technical Practice (龙蜥社区白皮书 v2)

## Definition

eBPF Technical Practice v2 is a 100-page white paper authored by the Anolis Community (龙蜥社区) — a consortium of Inspur, Alibaba Cloud, and Southeast University. It provides a systematic introduction to eBPF development workflow, toolchain, and production application scenarios.

## Key Concepts

### Development Workflow

```
1. Clang/LLVM → eBPF object file (.o)
2. bpftool/iproute2 → BPF ELF loader (load to kernel)
3. BPF Verifier → Safety validation (control flow graph, bounds checking)
4. JIT Compiler → Native machine code (x86_64/arm64/ppc64/s390x)
5. Attach to hook point (XDP/tracepoint/kprobe/LSM)
6. User space ↔ eBPF Map (data exchange)
```

### BPF Map Types

| Type | Use Case |
|------|----------|
| **Hash Map** | General key-value storage |
| **Array** | Indexed arrays |
| **LRU Hash** | Cache-like eviction |
| **Ring Buffer** | Low-latency event delivery |
| **Stack Trace** | Profiling |

### Application Scenarios

- **Network**: Cilium CNI, Hubble observability
- **Security**: Falco runtime detection, KRSI audit
- **Performance**: bpftrace one-liners, bcc tools

## Related Pages

- [[entities/linux/ebpf/ebpf-overview]] — eBPF核心架构
- [[sources/pdf-ebpf-books]] — eBPF书籍索引
- [[sources/pdf-ebpf-papers]] — eBPF论文索引
- [[kernel-net-index]] — Linux网络子系统

## Source Details

- [[sources/pdf-ebpf-technical-practice]] — eBPF技术实践 v2（龙蜥社区白皮书）