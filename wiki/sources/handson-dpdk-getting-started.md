---
type: source
source-type: web
title: "DPDK Linux Getting Started Guide"
author: "DPDK Project"
date: 2024
size: medium
path: https://doc.dpdk.org/guides/linux_gsg/sys_reqs.html
summary: "Data Plane Development Kit — kernel-bypass packet processing framework for high-speed networking. Getting started with system requirements, hugepages, and EAL."
tags: [dpdk, kernel-bypass, packet-processing, high-performance, userspace-networking, zero-copy, hugepages, numa, poll-mode]
created: 2026-05-29
---

# DPDK Linux Getting Started Guide

## 核心内容

### What is DPDK?
- **Kernel bypass**: user-space poll-mode drivers (no kernel involvement)
- **Zero-copy**: mbuf-to-mbuf, no kernel copies
- **Multi-core**: per-core RX/TX queues, lockless ring buffers
- **Hugepages**: 2MB or 1GB pages for large memory pools

### System Requirements
```
Kernel: >= 5.4
glibc:  >= 2.7
Python: >= 3.6
Build:  Meson + ninja
```

### Hugepages Setup (关键！)
```bash
# 2MB hugepages
echo 1024 > /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages

# 1GB hugepages (less fragmentation)
echo 4 > /sys/kernel/mm/hugepages/hugepages-1048576kB/nr_hugepages

# Verify
cat /proc/meminfo | grep Huge
```

### EAL (Environment Abstraction Layer)
```c
#include <rte_eal.h>

int main(int argc, char **argv) {
    // EAL init — hugepages, logical cores, PCI probe
    if (rte_eal_init(argc, argv) < 0)
        rte_panic("EAL init failed");

    // Now can use DPDK libraries
    return 0;
}
```

### Key Libraries
| Library | Purpose |
|---------|---------|
| `librte_eal` | Environment abstraction (hugepages, cores, timers) |
| `librte_ethdev` | Ethernet poll-mode drivers |
| `librte_mbuf` | Packet buffer management |
| `librte_mempool` | Lockless mbuf pool (per-core) |
| `librte_ring` | Multi-producer/consumer ring |
| `librte_lcore` | Thread/core affinity |

### Poll Mode Driver (PMD)
```c
// No interrupts — busy polling
struct rte_mbuf *rx_pkt = rte_pktmbuf_alloc(mempool);
uint16_t nb_rx = rte_eth_rx_burst(port_id, queue_id, &rx_pkt, 32);

if (nb_rx > 0) {
    // Process packets in user space
    process_packets(rx_pkt, nb_rx);
    rte_pktmbuf_free(rx_pkt);
}
```

### Memory Pool (Per-Core)
```c
// 每核心独立 mempool，避免锁竞争
struct rte_mempool *mbuf_pool = rte_pktmbuf_pool_create(
    "packet_pool", 8192,  // 8192 mbufs
    256,                   // cache per lcore
    0,                     // private data size
    RTE_MBUF_DEFAULT_BUF_SIZE,  // 2176 bytes
    rte_socket_id()        // local NUMA node
);
```

### NUMA Awareness
```c
// Always allocate on local node
unsigned socket_id = rte_socket_id();
struct rte_mempool *pool = rte_pktmbuf_pool_create(
    name, n, cache_size, priv_size, mbuf_size, socket_id
);
```

## NIDS 关联

- **内核旁路** → 直接用户态数据包捕获（绕过内核网络栈）
- **零拷贝** → mbuf 直接传递，无内核复制
- **多核并行** → 多核 IDS 引擎并行包处理
- **Hugepages** → 大内存池避免 TLB miss，提升吞吐量
- **Suricata/DPDK**: Suricata 可使用 DPDK 抓包引擎
- **VPP + IDS**: Cisco VPP 使用 DPDK 进行高速包处理

## 来源详情

- **官方文档**: doc.dpdk.org
- **相关**: [[entities/linux/kernel/net/linux-kernel-net-subsystem]] — Linux 网络栈
- **相关**: [[entities/linux/kernel/net/linux-kernel-io-uring-core]] — io_uring（异步 I/O）
- **相关**: [[entities/linux/kernel/mm/linux-kernel-mm]] — 内存/hugepages
