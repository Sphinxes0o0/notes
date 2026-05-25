---
type: source
source-type: pdf
created: 2026-05-25
title: "saBPF: Secure Namespaced Kernel Audit for Containers (SoCC 2021)"
author: "Soo Yee Lim, Bogdan Stelea, Xueyuan Han, Thomas Pasquier"
date: 2021
size: medium
path: raw/PDFs/papers/2021-Secure_Namespaced_Kernel_Audit_for_Containers.pdf
summary: "UBC/Harvard/Bristol: saBPF扩展eBPF框架实现容器级LSM审计，零内核修改"
tags: [security, ebpf, container, kubernetes, audit, lsm, saBPF, provenance]
---

# saBPF: Secure Namespaced Kernel Audit for Containers

## 核心内容

**Authors:** Soo Yee Lim (UBC), Bogdan Stelea (Bristol), Xueyuan Han (Harvard), Thomas Pasquier (UBC) | SoCC 2021

### Problem
- Container auditing for security analysis relies on host audit systems
- Built-in audit: lacks high-fidelity container logs, system-wide architecture too costly for per-container
- Reference monitors require extensive kernel modifications → hard to deploy

### saBPF Solution
**secure audit BPF** — eBPF framework extension for container-granular system-level audit

#### Architecture
1. **Namespace-aware eBPF** — programs understand container boundaries (cgroup namespaces)
2. **LSM integration** — attaches to security_* hooks at container granularity
3. **Provenance tracking** — records lineage of processes/files/sockets per container
4. **No kernel modification** — CO-RE, loads via bpf() syscall

#### Three Demonstrated Systems
1. **Audit framework** — high-fidelity container logs (replaces host auditd)
2. **Intrusion detection system (IDS)** — anomaly detection on container syscalls
3. **Lightweight access control** — seccomp + eBPF filter per container

### Evaluation
- Performance comparable to kernel-implemented audit systems
- Security guarantees: verified by formal methods (provenance graph)
- Deployment: Kubernetes-native via CNI + eBPF

### Key Technical Points
- **Container ID extraction**: walks cgroup hierarchy to identify container ID
- **Policy engine**: userspace reads eBPF maps, makes decisions, pushes filter rules
- **Log fidelity**: syscall arguments + return values + file descriptors + socket addresses

---

## 关键引用

> "saBPF extends the eBPF framework to support per-container audit without modifying the Linux kernel."

> "Provenance tracking at container granularity enables forensic analysis and attack attribution."

---

## 相关页面
- [[entities/linux/ebpf/ebpf-container-audit]]
- [[entities/linux/security/linux-security-observability-ebpf]]
- [[kernel-subsystems-index]]
- [[sources/pdf-ebpf-papers]]
- [[ebpf-index]]
