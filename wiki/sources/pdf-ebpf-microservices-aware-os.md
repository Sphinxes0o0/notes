---
type: source
tags: []
created: 2026-05-26source-type: pdf
title: "eBPF: Turning Linux into a Microservices-Aware Operating System"
author: "Brendan Gregg (Netflix)"
date: 2018
size: medium
path: raw/PDFs/papers/bpf-turninglinuxintoamicroservices-awareoperatingsystem-181105194737.pdf
summary: "Gregg's earlier essay framing eBPF as the technology that finally gives the Linux kernel awareness of microservice-level entities — services, connections, and latency — without application code changes."
created: 2026-05-27
---

# eBPF: Turning Linux into a Microservices-Aware Operating System

## Core Content

An earlier Brendan Gregg (Netflix) essay — a companion piece to "Rethinking the Linux Kernel" — focusing specifically on how eBPF solves the problem of kernel-level microservices awareness.

### The Problem

The Linux kernel traditionally thinks in terms of: processes, network connections, files. It has no native concept of a "microservice" — a logical unit of business functionality that may span multiple processes, containers, or network connections. This makes it hard to:
- Understand latency from the perspective of a service
- Attribute CPU/memory costs to a specific service
- Enforce policies at the service level
- Debug cross-service communication

### eBPF as the Solution

eBPF provides the mechanism to bridge the gap between kernel-level primitives and microservice-level semantics:

- **Process-to-Service Mapping**: eBPF programs can read container labels, cgroup membership, and environment variables to understand which service a process belongs to. This metadata can be attached to all subsequent observations.
- **Network Service Identity**: eBPF + XDP can tag packets with service-level metadata (e.g., source/destination service name) that persists through the networking stack. This enables per-service traffic accounting, rate limiting, and policy.
- **Distributed Tracing Context**: eBPF programs can inject/extract trace context (trace IDs, span IDs) from network packets, enabling zero-code-change distributed tracing.
- **Latency Attribution**: eBPF's ability to instrument kernel scheduler, block I/O, and networking paths simultaneously enables end-to-end latency breakdown per service.
- **Service Map Generation**: eBPF can continuously observe all TCP connections and build a real-time service dependency graph — which services talk to which.

### Specific Netflix Use Cases

- **Per-service CPU profiling**: Using eBPF to attribute CPU time to specific services running in containers — not just PIDs.
- **TCP flow analysis**: Understanding per-service TCP performance (retransmits, connection setup time) without modifying application code.
- **Container-level resource accounting**: Charging resource usage to services based on eBPF observations of syscalls and network activity.
- **Security per-service policies**: Enforcing network policies (which services can talk to which) at the kernel level via eBPF + XDP.

### Key Findings

- eBPF is the missing link between the kernel's process/connection view and the application developer's service view.
- Zero-code-change observability becomes possible: eBPF can extract microservice context from container metadata, DNS queries, or HTTP headers without application involvement.
- The combination of kernel-level visibility + microservice semantics is what makes eBPF uniquely powerful for cloud-native platforms.

## Source Details

- **Author**: Brendan Gregg, Netflix
- **Path**: raw/PDFs/papers/bpf-turninglinuxintoamicroservices-awareoperatingsystem-181105194737.pdf
- **Size**: 878.6 KB
- **Domain**: Linux kernel, eBPF, microservices, observability, networking