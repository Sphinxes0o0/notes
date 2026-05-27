---
type: source
source-type: pdf
title: "eBPF: Rethinking the Linux Kernel"
author: "Brendan Gregg (Netflix)"
date: 2020
size: medium
path: raw/PDFs/papers/bpf-rethinkingthelinuxkernel-200303183208.pdf
summary: "Brendan Gregg's influential essay on how eBPF transforms Linux from a general-purpose OS into a customizable, observability-first platform — covering tracing, networking, and security applications."
created: 2026-05-27
---

# eBPF: Rethinking the Linux Kernel

## Core Content

Brendan Gregg, a senior performance engineer at Netflix and author of "Systems Performance," presents eBPF as a fundamental paradigm shift in how Linux operates — from a kernel designed by Linus Torvalds's team to a kernel that can be dynamically reprogrammed by anyone.

### The Core Argument

Traditional kernel observability required either: (a) adding printk statements and recompiling, (b) using perf/ftrace with fixed tracepoints, or (c) writing kernel modules (dangerous, kernel version–dependent, require kernel header matching). eBPF replaces all of these with a single, safe, programmable interface.

### eBPF as the Kernel's SDK

- **Programmability**: eBPF makes the kernel programmable at runtime without reboots or kernel modules. Custom programs can be written in C (compiled with clang) or even at runtime with bpftrace.
- **Safety**: The in-kernel verifier ensures eBPF programs are safe (no infinite loops, bounded memory access, no pointer arithmetic that escapes bounds). This is what separates eBPF from kernel modules.
- **Dynamic Loading**: Programs are compiled into eBPF bytecode, validated by the verifier, JIT-compiled to native code, and loaded — all at runtime, without rebooting.
- **Persistence**: Programs can be loaded into the kernel and persist until explicitly unloaded. With bpffs mounted, programs can survive reboots.

### Key Domains of Application

1. **Performance Tracing**: `execsnoop`, `opensnoop`, `biolatency`, `funclatency` — bpftrace one-liners and full programs for deep system introspection.
2. **Networking**: XDP for fast path processing, tc for shaping, socket redirection for service mesh sidecars.
3. **Security**: Falco for runtime security, seccomp enforcement, capability bounding.
4. **Observability**: Continuous profiling (BPF-based profilers), distributed tracing with eBPF context propagation.

### The Observability Revolution

- **DTrace vs eBPF**: Gregg draws explicit parallels to DTrace (Solaris) — eBPF provides DTrace-like capabilities inside Linux. The difference: eBPF is now a first-class Linux feature, not a third-party kernel modification.
- **Perf + ftrace**: eBPF subsumes both — it can use perf counters and ftrace tracepoints as attachment points.
- **bpftrace**: A high-level language for eBPF, inspired by awk/DTrace. One-liners for common debugging tasks.

### Key Findings

- eBPF represents the third era of Linux observability: (1) ad-hoc tools, (2) static tracing (ftrace/perf), (3) programmable eBPF.
- The verifier is the key innovation — it enables safe in-kernel execution of untrusted code, which was previously impossible.
- eBPF blurs the line between "kernel developer" and "application developer" — anyone can extend the kernel's behavior.

## Source Details

- **Author**: Brendan Gregg, Netflix
- **Path**: raw/PDFs/papers/bpf-rethinkingthelinuxkernel-200303183208.pdf
- **Size**: 2.7 MB
- **Domain**: Linux kernel, eBPF, observability, performance engineering