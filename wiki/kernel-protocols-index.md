---
type: index
tags: [linux-kernel, networking, protocols, tcp, udp, ipv4, ipv6, osi, phy, mac]
created: 2026-05-22
---

# Linux Kernel — Network Protocols & Physical Layer

> TCP/UDP/IP implementation details, OSI physical/data-link layers, and full-stack network path analysis

## Entities

| Entity | Description | Tags |
|--------|-------------|------|
| [[entities/linux/network/linux-network-protocols]] | TCP/IP, IPv4/IPv6, BPF/XDP, bridging, routing, QoS | linux-kernel, networking, tcp |
| [[entities/linux/network/net-stack-deep-dive]] | Full-stack path: Socket → TCP/UDP → IP → Netfilter → Device | linux-kernel, networking, tcp, udp, ip, skbuff, netfilter, routing |
| [[entities/linux/network/osi-physical-layer]] | PHY/MAC architecture: MII/SMI, PCS/PMA/PMD, firmware vs driver | networking, osi, phy, mac, ethernet |

## Cross-References

- [[kernel-net-index]] — Main networking index (Socket/Netfilter/SKB architecture)
- [[os-index]] — Socket programming is a core OS concept; os-io-model covers select/poll/epoll
- [[kernel-subsystems-index]] — Crypto subsystem used for TLS/IPsec in network protocols
