---
type: source
source-type: pdf
created: 2026-05-25
title: "Security Observability with eBPF (O'Reilly, Isovalent)"
author: "Jed Salazar & Natalia Reka Ivanko"
date: 2022-04
size: medium
path: raw/PDFs/papers/isovalent_security_observability.pdf
summary: "Isovalent出品：云原生安全可观测性，eBPF Four Golden Signals监控框架"
tags: [security, ebpf, cloud-native, isovalent, observability, kubernetes]
---

# Security Observability with eBPF — Measuring Cloud Native Security Through eBPF Observability

## 核心内容

**Authors:** Jed Salazar & Natalia Reka Ivanko (Isovalent) | April 2022, O'Reilly

### Four Golden Signals for Kubernetes Security
1. **Latency** — network/response time anomalies indicating DoS or compromise
2. **Traffic** — unexpected network flows, lateral movement detection
3. **Errors** — application error rate spikes (HTTP 5xx, custom errors)
4. **Saturation** — resource exhaustion (CPU, memory, connections)

### eBPF-Based Security Monitoring Architecture
- **Kernel-level collection**: eBPF programs attach to LSM hooks, tracepoints, kprobes
- **No kernel modification required** — CO-RE (Compile Once, Run Everywhere)
- **Per-pod/namespace granularity** — unlike traditional host-level tools
- **Userspace communication**: ringbuffer for low-latency event delivery

### Security Observability Use Cases
- **Network policy enforcement** — Cilium uses eBPF to enforce L3/L4/L7 policies
- **Runtime security** — Falco rules via eBPF, KRSI (Kernel Runtime Security Instrumentation)
- **Data plane visibility** — Hubble for Kubernetes networking + security flow visualization
- **Compliance** — PCI-DSS, SOC2 audit trails from eBPF telemetry

### Key eBPF Hooks for Security
| Hook Type | Security Use |
|-----------|-------------|
| LSM (security_* ) | Access control, file/socket operations |
| tracepoint/syscalls | Audit syscalls, process creation |
| kprobe/kretprobe | Function entry/exit monitoring |
| XDP | Network packet filtering at wire speed |

---

## 关键引用

> "eBPF allows us to observe kernel behavior without modifying the kernel or requiring external agents."

> "Cilium's eBPF data path replaces iptables for Kubernetes network policy enforcement."

---

## 相关页面
- [[entities/linux/ebpf/ebpf-security-observability]]
- [[entities/linux/security/linux-security-observability-ebpf]]
- [[kernel-subsystems-index]]
- [[sources/pdf-ebpf-papers]]
- [[ebpf-index]]
