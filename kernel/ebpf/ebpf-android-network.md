---
title: "eBPF-Based Android Network Optimization"
description: "eBPF provides sandboxed programs that run in a kernel virtual machine. C-like code compiles to bytecode, attaches to kernel hooks via JIT compilation."
---
# eBPF-Based Android Network Optimization

## Architecture
eBPF provides sandboxed programs that run in a kernel virtual machine. C-like code compiles to bytecode, attaches to kernel hooks via JIT compilation.

## Key eBPF Concepts
- **Hooks**: syscalls, tracepoints, network events, kprobes/uprobes
- **Maps**: Key-value storage (hash tables, arrays, ring buffers) for kernel-user communication
- **JIT**: Converts bytecode to native assembly
- **Verifier**: Checks program size and complexity for safety
- **Privileges**: Control access levels

## Android bpfloader
- Loads `.o` files from `/system/etc/bpf/` and `/vendor/etc/bpf/`
- 3-step: read code sections → create maps → load programs
- Programs pinned to `/sys/fs/bpf/` for persistence
- SELinux `neverallow` policies enforce restrictions

## Network Control Example (Doze Mode)
- Hooks `tcp_v4_do_rcv` via `bpf_skops_parse_hdr`
- `BPF_CGROUP_RUN_PROG_SOCK_OPS` triggers eBPF programs
- `bpf_owner_match` determines DROP or ALLOW per UID
- Controls both TCP and UDP traffic based on map rules

## Key Insight
eBPF enables fine-grained kernel extensibility **without kernel source modifications**. Android uses this for Doze mode network restrictions.
