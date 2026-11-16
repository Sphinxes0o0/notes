---
type: entity
tags: [linux, networking, load-balancing, proxy, service-mesh, lb, l4, l7]
created: 2026-05-28
sources: [arthurchiao-modern-lb-proxy]
---

# Load Balancing and Proxy

## Definition

Modern network load balancing distributes traffic across backend servers using various topologies and approaches. Key distinction between L4 (connection/session layer) and L7 (application protocol layer) load balancing.

## L4 vs L7 Load Balancing

| Aspect | L4 | L7 |
|--------|----|----|
| Layer | Connection/session | Application protocol |
| Visibility | Bytes only | HTTP, gRPC, Redis, etc. |
| Performance | Higher | Lower |
| Use case | Raw throughput | Content-based routing |

> "L7 load balancing is critical for modern protocols due to multiplexing and kept-alive connections creating 3000x load imbalances."

## Topology Patterns

| Pattern | Examples | Trade-off |
|---------|----------|-----------|
| Middle/Edge Proxy | HAProxy, NGINX, Envoy | Simple but single points of failure |
| Embedded Client Library | Finagle, gRPC | Best performance/isolation; multi-language burden |
| Sidecar Proxy | Envoy-based service mesh | Language-agnostic; achieves client library benefits |

## L4 Design Patterns

| Pattern | Description | Use Case |
|---------|-------------|----------|
| Termination | LB terminates client connection | Simpler, lower client latency |
| Passthrough | NAT without terminating | Higher throughput, backend congestion control |
| DSR | Response directly to client | Reduces LB bandwidth |

## L4 Scalability
- **HA Pair**: Traditional; 50% idle capacity, limited fault tolerance
- **Clustering + ECMP**: Google Maglev, AWS NLB; horizontal scaling with commodity hardware

## Related Pages

- [[entities/linux/ebpf/ebpf-networking]] — eBPF-based load balancing (Katran)
- [[entities/linux/network/modern-lb-proxy]] — Envoy, service mesh
- [[entities/linux/network/congestion-control]] — Backend congestion control
- [[entities/linux/ebpf/ebpf-xdp]] — XDP for high-performance LB
