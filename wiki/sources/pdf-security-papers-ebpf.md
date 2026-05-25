---
type: source
source-type: pdf
created: 2026-05-25
title: "eBPF Security Papers: Rootkit Defense, Falco at Apple, Google BPF Audit"
author: "Pat Hogan, Eric Sage, Melissa Kilby, Brendan Jackman"
date: 2021-2024
size: medium
path: raw/PDFs/papers/
summary: "eBPF内核安全：Rootkit攻防(2024)、Apple Falco运行时检测(2021)、Google KRSI安全审计"
tags: [security, ebpf, rootkit, falco, google, krsi, linux-kernel]
---

# eBPF Security Papers: Rootkit Defense, Falco at Apple, Google BPF Audit

## 核心内容

### 1. Creating and countering the next generation of Linux rootkits using eBPF (Pat Hogan, 2024)

**Key Topics:**
- Linux kernel rootkits: advantages (visibility/control over network, files, processes) vs risks (kernel crashes, updates break modules, EKS blocks arbitrary modules)
- eBPF as rootkit weapon: hooks syscall table, network stack, file system transparently
- eBPF verification: safety guarantees vs kernel modules
- Detecting/preventing malicious eBPF usage

### 2. Think eBPF for Kernel Security Monitoring - Falco at Apple (Eric Sage & Melissa Kilby, eBPF Summit 2021)

**Key Topics:**
- Why Apple loves BPF: easy to audit, limits bug impact vs kernel modules, no dependencies
- BPF VM vs Kernel Module comparison: BPF has limited access, kernel modules have full hardware access
- BPF kernel bypass: falco.ko vs XDPSocket Filter vs Probe Tracepoint
- libbpf/bpftool for inspecting program instructions, map contents, usage statistics

### 3. Stories from BPF security auditing at Google (Brendan Jackman, Google)

**Key Topics:**
- KRSI (Kernel Runtime Security Instrumentation): BPF LSM for security telemetry
- BPF Atomics: atomic operations in BPF programs
- Ringbuffers: efficient event delivery from kernel to user space
- Google's journey: audit was too slow, kernel modules hard to maintain → BPF LSM
- LSM provides semantic internal API for security information (designed for enforcement, used for audit)

---

## 关键引用

- eBPF verifier provides safety guarantees for programs before loading
- BPF LSM hooks: security_bprm_check, security_file_open, security_socket_bind, etc.
- Falco rule engine: syscalls + container context → notify via ringbuffer to userspace

---

## 相关页面
- [[entities/linux/ebpf/ebpf-security-observability]]
- [[entities/linux/security/linux-security-observability-ebpf]]
- [[kernel-subsystems-index]]
- [[sources/pdf-ebpf-papers]]
