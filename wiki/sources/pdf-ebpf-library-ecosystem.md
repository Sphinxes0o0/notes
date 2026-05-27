---
---
type: source
source-type: pdf
title: "eBPF Library Ecosystem Overview in Go, Rust, Python, C and More"
author: "Cilium / Isovalent Community"
date: 2023
size: small
path: raw/PDFs/papers/eBPF_Library_Ecosystem_Overview_in_Go_Rust_Python_C_and_More.pdf
summary: "A survey of the eBPF library ecosystem across 6 programming languages — comparing APIs, feature coverage, CO-RE support, and developer ergonomics."
created: 2026-05-27
---

# eBPF Library Ecosystem Overview in Go, Rust, Python, C and More

## Core Content

This document provides a comprehensive survey of eBPF library support across major programming languages as of 2023, produced by the Cilium/Isovalent community.

### Libraries Covered

| Language | Library | CO-RE | Key Features |
|----------|---------|-------|--------------|
| C | libbpf | Full | Reference implementation; used by kernel itself; requires kernel headers |
| Go | `cilium/ebpf` | Full | Most complete Go eBPF library; CO-RE via CO-RE relocation; used in production at scale |
| Rust | `aya` | Full | Memory-safe eBPF development; async support; actively maintained by Oxirus |
| Python | `BPFCC` (BCC) | Partial | Legacy; Python bindings for the BCC framework; no CO-RE |
| Python | `bpfprog` | Full | Newer; cleaner API; CO-RE support |
| Go | `dropshots` | N/A | XDP testing only |
| Go | `florianl/go-bpf` | Limited | Older, less maintained |

### Key Observations

- **CO-RE (Compile Once — Run Everywhere)**: The biggest differentiator. Libraries with CO-RE support (libbpf-based) avoid recompiling against kernel headers for each target kernel version. All modern libraries (cilium/ebpf, aya, bpfprog) support CO-RE; BCC-based approaches do not.
- **libbpf as the Foundation**: Nearly all modern eBPF libraries are thin wrappers around libbpf. libbpf provides the core: program loading, map management, BTF parsing, CO-RE relocation, ring buffer.
- **Go's cilium/ebpf**: The most mature non-C library. Used in Cilium, Falco, Katran, and many production systems. Supports all program types, all map types, ring buffers, and struct_ops.
- **Rust's aya**: The Rust ecosystem's answer to memory-safe eBPF. Compile eBPF programs in Rust using the `aya` crate, and the user-space component separately. Growing fast.
- **Python's State**: BCC-based Python (BPFCC) is easy to use but requires matching kernel headers. The newer `bpfprog` addresses this but is less mature.
- **Go vs Rust**: Go libraries focus on user-space program control (loading maps, reading data); Rust's aya additionally supports writing the eBPF programs themselves in memory-safe Rust.

### Ecosystem Trends

- **Consolidation**: The ecosystem is converging on libbpf as the shared foundation.
- **CO-RE adoption**: All new libraries implement CO-RE. Legacy BCC users are migrating.
- **Rust growth**: The aya project is rapidly gaining features and production users.
- **WASM?**: No major WASM-eBPF integration yet (as of 2023), though some experimental work exists.

## Source Details

- **Organization**: Cilium / Isovalent Community
- **Path**: raw/PDFs/papers/eBPF_Library_Ecosystem_Overview_in_Go_Rust_Python_C_and_More.pdf
- **Size**: 275.1 KB
- **Domain**: eBPF programming, library ecosystem, developer tools
