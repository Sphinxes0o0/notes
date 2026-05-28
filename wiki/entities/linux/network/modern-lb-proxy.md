---
type: entity
tags: [linux, networking, load-balancing, proxy, envoy, service-mesh, lb, l4, l7]
created: 2026-05-28
sources: [arthurchiao-modern-lb-proxy]
---

# Modern Load Balancing and Proxying

## Core Concepts

Modern load balancing is foundational to reliable distributed systems. Key aspects:

- **L4 vs L7 Load Balancing**: L4 operates at connection/session layer (bytes only); L7 operates at application protocol layer (HTTP, gRPC, Redis, etc.)
- **Topology Patterns**: Middle proxy, embedded library, sidecar
- **Scalability**: ECMP and Maglev consistent hashing

## Related Concepts

- [[entities/linux/network/load-balancing]] — 负载均衡相关概念
- [[entities/linux/network/net-stack-overview]] — Linux 网络栈
- [[entities/security/network-traffic-analysis]] — 网络流量分析
