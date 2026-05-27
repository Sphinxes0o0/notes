---
type: source
tags: []
created: 2026-05-26source-type: pdf
title: "Security Observability with eBPF — Isovalent"
author: "Isovalent"
date: 2023
size: large
path: raw/PDFs/papers/isovalent_security_observability.pdf
summary: "Isovalent's technical deep-dive into using eBPF for cloud-native security observability — covering network policy enforcement, workload identity, and runtime security monitoring."
created: 2026-05-27
---

# Security Observability with eBPF — Isovalent

## Core Content

This whitepaper from Isovalent (acquired by Cisco, now behind Cilium) provides an architectural overview of using eBPF for security observability in cloud-native Kubernetes environments.

### Key Contributions

- **Network Policy Enforcement at Scale**: eBPF-based Cilium datapath enforces Kubernetes NetworkPolicies at the L7 layer. Unlike iptables-based solutions (kube-proxy), eBPF avoids the O(n) rule traversal problem — policy lookups are O(1).
- **Workload Identity**: Uses X.509 certificates (via SPIFFE/SPIRE) embedded in eBPF connection metadata. Each pod gets a cryptographically verifiable identity used for mTLS and policy decisions — all enforced in the eBPF datapath.
- **Layer 7 Visibility**: eBPF programs at the socket/bpf_iter operation intercept HTTP/gRPC requests at the application layer without terminating TLS. Enables dark launches, rate limiting, and anomaly detection.
- **Encryption Enforcement**: WireGuard tunnels between nodes with keys managed by the control plane. eBPF enforces that traffic between namespaces must go through encrypted channels.
- **Runtime Security**: Detects syscall anomalies (exec of unexpected binaries, unusual file access patterns) by attaching to tracepoints — without kernel modules or agents.

### Technical Architecture

- **Cilium Agent**: Runs in user space, compiles and loads eBPF programs via ELF loading.
- **eBPF Maps**: Shared state between datapath and agent for policy lookups, metrics, and tracing.
- **Cluster Mesh**: Multi-cluster connectivity with consistent security policy across clusters using eBPF-based peer discovery.

### Key Findings

- eBPF enables a "always-on" security posture — policies are enforced inline, not as a sidecar proxy.
- Replacing iptables with eBPF reduces latency and CPU overhead for network policy enforcement by 10x in some benchmarks.
- The combination of eBPF + SPIFFE provides the foundation for zero-trust networking in Kubernetes.

## Source Details

- **Organization**: Isovalent (Cisco)
- **Path**: raw/PDFs/papers/isovalent_security_observability.pdf
- **Size**: 2.9 MB
- **Domain**: Cloud-native security, Kubernetes networking, Cilium, zero-trust