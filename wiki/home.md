---
type: index
tags: [navigation]
created: 2026-05-22
---

# LLM Wiki — Home

> 本文件由 LLM 维护，每次 ingest 后自动更新。
>
> Last updated: 2026-05-22 | Total pages: 157 | Module indexes: 26

---

## Module Indexes

> 每个 module index 是一个知识子域的入口，聚合相关 entity，便于 Obsidian 图谱导航。

### Linux Kernel
| Index | Domain | Entities |
|-------|--------|----------|
| [[kernel-virt-index]] | KVM, Virtio virtualization | 2 |
| [[kernel-io-index]] | io_uring, VFS | 2 |
| [[kernel-net-index]] | Socket/sk_buff, Netfilter, TCP/IP protocols | 4 |
| [[kernel-protocols-index]] | Protocol details, full-stack path, PHY/MAC layer | 3 |
| [[kernel-mm-index]] | SLUB, page fault, swap, reclaim, mmap | 5 |
| [[kernel-sched-index]] | CFS, context switch, load balancing | 4 |
| [[kernel-block-index]] | bio/request, blk-mq, IO schedulers | 3 |
| [[kernel-subsystems-index]] | Crypto, locking, IPC, RCU, time, sound | 6 |
| [[ebpf-index]] | XDP, TC, Cilium, Falco, CO-RE, eBPF ecosystem | 5 |

### Emulation
| Index | Domain | Entities |
|-------|--------|----------|
| [[qemu-index]] | QOM, memory, CPU, migration, block layer | 5 |

### Operating System
| Index | Domain | Entities |
|-------|--------|----------|
| [[os-index]] | Process/thread, virtual memory, I/O models, Linux subsystems | 7 |

### Exercise Science
| Index | Domain | Entities |
|-------|--------|----------|
| [[supplements-index]] | Curcumin (7 sub-entities), CoQ10 (5 sub-entities) | 12 |
| [[physiology-index]] | Muscle hypertrophy, mTOR, MPS, VO2max, lactate threshold, BFR... | 10 |
| [[nutrition-index]] | Protein, carbs, omega-3, ketogenic diet | 4 |
| [[running-index]] | Running economy, trail running, ultra-endurance | 3 |
| [[training-index]] | Periodization, tapering, training methods | 3 |
| [[biomechanics-index]] | Gait analysis, running shoes | 2 |
| [[exercise-health-index]] | Exercise as medicine, chronic disease | 1 |
| [[obesity-index]] | Obesity & visceral fat: 5-system impact, 23 papers | 6 |
| [[technology-index]] | Wearable devices, HRV monitoring, running power meters, AI/ML | 3 |
| [[kinesiology-tape-index]] | Kinesiology tape: mechanism, clinical evidence, pain management | 1 |
| [[population-index]] | Youth, master, female, elite runners; population-specific training | 4 |

### Programming & Algorithms
| Index | Domain | Entities |
|-------|--------|----------|
| [[datastructure-index]] | DSA: complexity, linear, sorting, DP, recursion, hash, trees | 7 |
| [[design-patterns-index]] | SOLID, creational, structural, behavioral | 5 |
| [[interview-index]] | Coding patterns, system design basics | 3 |
| [[cpp-index]] | Modern C++ (C++11-20), STL containers/algorithms/iterators, serialization | 18 |
| [[sys-prog-index]] | C/C++, Linux, middleware, security | 4 |

### Tools & BMC
| Index | Domain | Entities |
|-------|--------|----------|
| [[tools-index]] | tcpdump, netcat, masscan, nmap | 2 |
| [[openbmc-index]] | IPMI, Redfish, boot/firmware update, hardware control | 4 |

---

## Sources

| 来源 | 描述 | 日期 | 类型 |
|------|------|------|------|
| [[sources/relay-neuron-supplements]] | 姜黄素与辅酶Q10补剂深度研究（~30篇文献）| 2026-04 | github |
| [[sources/relay-neuron-physiology]] | 运动生理学：肌肥大、mTOR、BFR、VO2max等（~25主题）| 2026-05 | github |
| [[sources/relay-neuron-obesity-literature]] | 中国肥胖文献分析：23篇，覆盖心血管/肝脏/神经/代谢/肾脏五大系统 | 2026-04 | github |
| [[sources/relay-neuron-technology]] | 可穿戴设备、HRV监控、跑步功率计、AI/ML预测、实时生理监控（10主题）| 2026-04 | github |
| [[sources/relay-neuron-kinesiology-tape]] | 运动肌贴原理、肌肉力量、关节稳定性、临床应用（5主题，2024-2026）| 2026-04 | github |
| [[sources/relay-neuron-population-specific]] | 青少年、中老年、女性、精英、休闲跑者专项研究（6主题）| 2026-04 | github |
| [[sources/relay-neuron-training-methods]] | 间歇、节奏跑、LSD、阈值、坡度训练综合（5主题）| 2026-04 | github |
| [[sources/notes-net-deep]] | 网络深度笔记合并：skbuff/NAT/路由 Trie/PHY-MAC/Conntrack/全栈路径 | 2026-05 | github |
| [[sources/notes-network-fundamentals]] | Linux 网络协议实现笔记（~78 .md 文件）| 2026-05 | github |
| [[sources/notes-netfilter]] | Linux Netfilter/iptables/nftables/conntrack 深度分析 | 2026-05 | github |
| [[sources/notes-os]] | Linux 内核深度分析：VFS、调度器、SLUB 分配器、cgroups 架构详解 | 2026-05 | github |
| [[sources/notes-os-fundamentals]] | 操作系统基础：进程/线程、内存管理、文件系统、IO模型 | 2026-05 | github |
| [[sources/notes-qemu]] | QEMU 模拟器架构：TCG、QOM、KVM 集成、块设备、迁移 | 2026-05 | github |
| [[sources/notes-overview]] | Sphinx 技术笔记索引页 | 2026-05 | github |
| [[sources/notes-kernel]] | Linux 内核各子系统深度分析：mm、sched、block、VFS、网络、虚拟化 | 2026-05 | github |
| [[sources/notes-kernel-crypto]] | Linux 内核密码学子系统：crypto_alg注册、skcipher、aead、ahash | 2026-05 | github |
| [[sources/notes-kernel-ipc]] | Linux 内核 IPC 子系统：msg、sem、shm、mqueue | 2026-05 | github |
| [[sources/notes-kernel-locking]] | Linux 内核锁子系统：spinlock、mutex、rwsem、percpu、lockdep | 2026-05 | github |
| [[sources/notes-kernel-rcu]] | Linux 内核 RCU：Read-Copy-Update、无锁同步、grace period | 2026-05 | github |
| [[sources/notes-kernel-sound]] | Linux 内核声音子系统：ALSA、PCM、ASoC、DAPM | 2026-05 | github |
| [[sources/notes-kernel-time]] | Linux 内核时间子系统：tick、hrtimer、timekeeping、posix-timers | 2026-05 | github |
| [[sources/notes-tools]] | 工具使用笔记：tcpdump、netcat、masscan/nmap、移除 Snap | 2026-05 | github |
| [[sources/notes-openbmc]] | OpenBMC 深度技术分析：硬件控制、安全、Redfish、IPMI、启动更新 | 2026-05 | github |
| [[sources/pdf-cpp-modern-tutorial]] | Modern C++ Tutorial (C++11/14/17/20)：Lambda、智能指针、RAII、并发、Move语义 | 2026-05 | pdf |
| [[sources/pdf-cpp-effective-stl]] | Effective STL (Scott Meyers)：50条STL最佳实践，容器/迭代器/算法/仿函数 | 2026-05 | pdf |
| [[sources/pdf-ebpf-books]] | eBPF书籍3册：龙蜥白皮书(XDP/TC/CO-RE)、技术实践、Cilium创始人Liz Rice入门 | 2026-05 | pdf |
| [[sources/pdf-ebpf-papers]] | eBPF论文7篇：Thomas Graf微内核愿景、Apple Falco、Google审计(Atomics/Ringbuf)、Black Hat Rootkit攻防 | 2026-05 | pdf |
| [[sources/notes-ccpp]] | C/C++ 技术笔记：序列化、智能指针深度分析、堆栈对象创建策略、移动语义 | 2026-05 | github |
| [[sources/notes-datastructure]] | 数据结构与算法：复杂度分析、线性结构、排序、DP、递归、哈希表、树与图（21章节+真题训练） | 2026-05 | github |
| [[sources/notes-design-patterns]] | 设计模式：SOLID原则、创建型5种、结构型7种、行为型11种共23种设计模式 | 2026-05 | github |
| [[sources/notes-interview]] | 面试准备：方法论、问题解决模式、系统设计基础、NP完全性、位操作、进阶数据结构 | 2026-05 | github |
| [[sources/notes-midware]] | 中间件：DoIP协议（ISO 13400）、SOME/IP服务通信、vSOME/IP开源实现 | 2026-05 | github |
| [[sources/notes-security]] | 安全工具：Masscan高速端口扫描、Falco K8s运行时安全、Snort 3 NIDS架构分析 | 2026-05 | github |
| [[sources/notes-sys]] | 系统编程：TTY/Shell/Console体系、ELF文件格式、Linux IPC、单例模式 | 2026-05 | github |

---

## Synthesis

| 主题 | 描述 | 日期 |
|------|------|------|
| [[synthesis/topic-os-fundamentals]] | 操作系统基础综合：进程/线程、内存管理、文件系统、网络、并发 | 2026-05 |
| [[synthesis/topic-network-fundamentals]] | 计算机网络基础综合：TCP/IP 五层模型、Socket 编程、HTTP 缓存、安全 | 2026-05 |

---

## Journal

> 待补充
