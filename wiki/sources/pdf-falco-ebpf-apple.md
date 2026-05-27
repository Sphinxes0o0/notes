---
type: source
source-type: pdf
title: "Think eBPF for Kernel Security Monitoring — Falco at Apple"
author: "Leonardo Di Donato, Mark Stemm, Leonardo Grasso (Apple / Sysdig)"
date: 2023
size: large
path: raw/PDFs/papers/Think_eBPF_for_Kernel_Security_Monitoring_-_Falco_at_Apple.pdf
summary: "Falco's journey replacing its kernel module driver with an eBPF probe — enabling safer, more portable, kernel-level security monitoring without CAP_SYS_ADMIN."
created: 2026-05-27
---

# Think eBPF for Kernel Security Monitoring — Falco at Apple

## Core Content

A deep technical presentation from the Falco team (now part of Sysdig) detailing how they rewrote Falco's kernel driver from a kernel module to eBPF, enabling production-safe runtime security monitoring at Apple scale.

### Background: Falco's Original Architecture

Falco originally used a kernel module (`falco.ko`) to hook into the kernel's syscall path. This required `CAP_SYS_MODULE` — effectively root-equivalent — and was considered too risky for production use at Apple.

### The eBPF Migration

- **Driver**: Replaced `falco.ko` with an eBPF probe (`falco-bpf`) that attaches to syscall tracepoints (`sys_enter`, `sys_exit`). The probe is compiled with clang and loaded at runtime.
- **No CAP_SYS_ADMIN**: Uses CO-RE (Compile Once — Run Everywhere) with BTF type information. Relies only on `CAP_BPF` (or recent kernel's `CAP_PERFMON`) instead of full kernel module privileges.
- **Ring Buffer**: Replaced the old userspace `fanotify`-based event delivery with eBPF ring buffer (`bpf_ringbuf_reserve`), providing lower latency and zero-copy event delivery from kernel to userspace.
- **Dropping In-Kernel Events**: eBPF programs can filter events in-kernel before copying to userspace — dramatically reducing the performance overhead of security monitoring.
- **Program Types**: Uses `BPF_PROG_TYPE_TRACEPOINT`, `BPF_PROG_TYPE_KPROBE`, and `BPF_PROG_TYPE_RAW_TRACEPOINT`.

### Technical Deep Dives

- **Syscall Extraction**: Extracts syscall arguments, file paths, process metadata (UID, container ID) via per-syscall tracepoint probes.
- **Security Rules**: Falco's rule engine runs in userspace, consuming events from the ring buffer. Rules define suspicious patterns (e.g., "shell spawned in a container", "sensitive file opened").
- **CO-RE / BTF**: Explained in detail — the approach that makes eBPF portable across kernel versions without recompiling the probe against kernel headers.
- **Scap (userspace library)**: The userspace component handles event buffering, rule processing, and output to SIEM/SOAR platforms.

### Key Findings

- eBPF transforms security monitoring from a "must be privileged" operation to a "can be production-safe" operation.
- CO-RE + ring buffer + in-kernel filtering together reduce monitoring overhead by ~60% vs the kernel module approach.
- The Falco eBPF probe has been deployed at Apple to monitor tens of thousands of production nodes.

## Source Details

- **Authors**: Leonardo Di Donato, Mark Stemm, Leonardo Grasso (Apple / Sysdig)
- **Event**: Presented at an Apple engineering conference
- **Path**: raw/PDFs/papers/Think_eBPF_for_Kernel_Security_Monitoring_-_Falco_at_Apple.pdf
- **Size**: 8.6 MB
- **Domain**: Runtime security, kernel monitoring, Falco, containers, eBPF