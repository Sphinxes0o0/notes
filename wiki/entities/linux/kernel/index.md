---
type: index
tags: [linux-kernel, navigation]
created: 2026-05-29
---

# Linux Kernel — Master Index

> 各子系统索引合并页 | Last updated: 2026-05-29

---

## Subsystems

| Subsystem | Description | Index |
|-----------|-------------|-------|
| [[entities/linux/kernel/mm/linux-kernel-mm]] | Memory Management: SLUB, page fault, swap, mmap | [[entities/linux/kernel/index#memory-management]] |
| [[entities/linux/kernel/sched/linux-kernel-sched-core]] | Scheduler: CFS, context switch, load balance | [[entities/linux/kernel/index#scheduler]] |
| [[entities/linux/kernel/block/linux-kernel-block-core]] | Block Layer: bio, blk-mq, I/O schedulers | [[entities/linux/kernel/index#block-layer]] |
| [[entities/linux/kernel/net.md]] | Networking: Socket, sk_buff, Netfilter | [[entities/linux/kernel/index#networking]] |
| [[entities/linux/kernel/virt-kvm]] | Virtualization: KVM, Virtio | [[entities/linux/kernel/index#virtualization]] |
| [[entities/linux/kernel/linux-kernel-io-uring-core]] | Async I/O: io_uring | [[entities/linux/kernel/index#io-uring--vfs]] |
| [[entities/linux/kernel/linux-kernel-vfs-core]] | VFS: inode, dentry, super_block | [[entities/linux/kernel/index#io-uring--vfs]] |

---

## Core Subsystems (Crypto / Locking / IPC / RCU / Time / Sound)

| Entity | Description | Tags |
|--------|-------------|------|
| [[entities/linux/kernel/linux-kernel-crypto-core]] | Crypto subsystem: crypto_alg registration, skcipher, aead, template mechanism | linux-kernel, crypto |
| [[entities/linux/kernel/linux-kernel-locking-core]] | Locking: spinlock, mutex, rwsem, percpu, lockdep | linux-kernel, locking |
| [[entities/linux/kernel/linux-kernel-ipc-core]] | IPC: msg, sem, shm, mqueue, pipelined send | linux-kernel, ipc |
| [[entities/linux/kernel/linux-kernel-rcu-core]] | RCU: Read-Copy-Update, lock-free reads, grace period, srcu | linux-kernel, rcu |
| [[entities/linux/kernel/linux-kernel-time-core]] | Time: tick, hrtimer, timekeeping, NTP, posix-timers | linux-kernel, time |
| [[entities/linux/kernel/linux-kernel-sound-core]] | Sound: ALSA, PCM, ASoC, DAPM widget, DAI | linux-kernel, sound |

---

## Memory Management

| Entity | Description | Tags |
|--------|-------------|------|
| [[entities/linux/kernel/mm/linux-kernel-mm-slab-allocator]] | SLUB: sheaf/cmpxchg16b, freelist, per-CPU cache | linux-kernel, mm, slab |
| [[entities/linux/kernel/mm/linux-kernel-mm-page-fault]] | Page fault: do_page_fault, handle_mm_fault, anon/file VMA | linux-kernel, mm, paging |
| [[entities/linux/kernel/mm/linux-kernel-mm-swap]] | Swap: swap_cache XA tree, kswapd, Multi-Gen LRU | linux-kernel, mm, swap |
| [[entities/linux/kernel/mm/linux-kernel-mm-page-reclaim]] | Page reclaim: LRU, refault distance, working set | linux-kernel, mm, reclaim |
| [[entities/linux/kernel/mm/linux-kernel-mm-mmap]] | mmap: VMA, Maple Tree, vm_area_struct | linux-kernel, mm, mmap |

---

## Scheduler

| Entity | Description | Tags |
|--------|-------------|------|
| [[entities/linux/kernel/sched/linux-kernel-sched-core]] | Scheduler core: __schedule, pick_next_task, sched_class | linux-kernel, sched |
| [[entities/linux/kernel/sched/linux-kernel-sched-cfs]] | CFS: vruntime red-black tree, EEVDF, latency target | linux-kernel, sched, cfs |
| [[entities/linux/kernel/sched/linux-kernel-sched-context-switch]] | Context switch: switch_to, register save/restore, lazy TLB | linux-kernel, sched, context-switch |
| [[entities/linux/kernel/sched/linux-kernel-sched-load-balance]] | Load balancing: sched_domain, load_balance, idle balance | linux-kernel, sched, load-balance |

---

## Block Layer

| Entity | Description | Tags |
|--------|-------------|------|
| [[entities/linux/kernel/block/linux-kernel-block-core]] | Block layer: bio/request/gendisk, block_device | linux-kernel, block |
| [[entities/linux/kernel/block/linux-kernel-block-mq]] | blk-mq: hctx/tags, software queue, hardware queue | linux-kernel, block, mq |
| [[entities/linux/kernel/block/linux-kernel-block-scheduler]] | IO schedulers: mq-deadline, BFQ, elevator | linux-kernel, block, scheduler |

---

## Networking

| Entity | Description | Tags |
|--------|-------------|------|
| [[entities/linux/kernel/net.md]] | Socket Layer, sk_buff, Netdevice, Routing, TCP/UDP implementation | linux-kernel, networking, socket |
| [[entities/linux/kernel/skbuff-deep-dive]] | SKB memory management: head/data/tail/end layout, clone/copy, scatter-gather, dataref | linux-kernel, networking, skbuff |
| [[entities/linux/kernel/netfilter.md]] | Netfilter: iptables, nftables, conntrack, NAT, hook points | linux-kernel, networking, netfilter |

---

## Network Protocols & Physical Layer

| Entity | Description | Tags |
|--------|-------------|------|
| [[entities/linux/network/linux-network-protocols]] | TCP/IP, IPv4/IPv6, BPF/XDP, bridging, routing, QoS | linux-kernel, networking, tcp |
| [[entities/linux/network/net-stack-deep-dive]] | Full-stack path: Socket → TCP/UDP → IP → Netfilter → Device | linux-kernel, networking, tcp, udp, ip, skbuff, netfilter, routing |
| [[entities/linux/network/osi-physical-layer]] | PHY/MAC architecture: MII/SMI, PCS/PMA/PMD, firmware vs driver | networking, osi, phy, mac, ethernet |

---

## Virtualization

| Entity | Description | Tags |
|--------|-------------|------|
| [[entities/linux/kernel/virt-kvm]] | KVM: hardware virtualization, struct kvm/vCPU, VM-Exit/Entry, EPT paging, Dirty Ring, guest_memfd | linux-kernel, virtualization, kvm |
| [[entities/linux/kernel/virt-virtio]] | Virtio: paravirtual I/O framework, virtqueue ring, device state machine, PCI/MMIO transport | linux-kernel, virtualization, virtio |

---

## I/O (io_uring + VFS)

| Entity | Description | Tags |
|--------|-------------|------|
| [[entities/linux/kernel/linux-kernel-io-uring-core]] | io_uring: high-performance async I/O, SQ/CQ rings, 65 opcodes, mmap shared memory, io-wq | linux-kernel, async-io |
| [[entities/linux/kernel/linux-kernel-vfs-core]] | VFS: inode/dentry/super_block/file, namei path lookup, dcache, 6 operation interfaces | linux-kernel, vfs, filesystem |

---

## Other Subsystems

| Entity | Description | Tags |
|--------|-------------|------|
| [[entities/linux/kernel/linux-kernel-smp]] | SMP: per-CPU data, CPU bringup, IPI | linux-kernel, smp |
| [[entities/linux/kernel/irq-softirq]] | IRQ/Softirq: interrupt handling, tasklets, softirqs | linux-kernel, irq |
| [[entities/linux/kernel/cpu-power-management]] | CPU Power Management: P-state, C-state, idle, cpufreq | linux-kernel, power |

---

## Cross-References

- [[os-index]] — OS-level concepts: virtual memory, processes, threads, I/O models
- [[entities/linux/kernel/index]] — Books and references for further study
- [[ebpf-index]] — eBPF for kernel instrumentation

---

← [[home|Back to Home]]
