---
type: index
tags: [linux-kernel, networking]
created: 2026-05-22
---

# Linux Kernel — Networking

> Socket layer, sk_buff management, netfilter framework, and network protocol implementations

## Entities

| Entity | Description | Tags |
|--------|-------------|------|
| [[entities/linux/kernel/net/linux-kernel-net-subsystem]] | Socket Layer, sk_buff, Netdevice, Routing, TCP/UDP implementation | linux-kernel, networking, socket |
| [[entities/linux/kernel/net/skbuff-deep-dive]] | SKB memory management: head/data/tail/end layout, clone/copy, scatter-gather, dataref | linux-kernel, networking, skbuff |
| [[entities/linux/kernel/netfilter/linux-kernel-netfilter-framework]] | Netfilter: iptables, nftables, conntrack, NAT, hook points | linux-kernel, networking, netfilter |
| [[entities/linux/network/linux-network-protocols]] | TCP/IP, IPv4/IPv6, BPF/XDP, bridging, routing, QoS | linux-kernel, networking, tcp |

## Cross-References

- [[kernel-protocols-index]] — Network protocols, full-stack analysis, and physical layer
- [[kernel-io-index]] — Network I/O passes through VFS for filesystem sockets
- [[kernel-virt-index]] — Virtio-net paravirtual NIC is the main network device for KVM guests
- [[os-index]] — Socket programming is a core OS concept; os-io-model covers select/poll/epoll
