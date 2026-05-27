---
type: index
tags: [navigation]
created: 2026-05-22
---

# LLM Wiki — Home

> 本文件由 LLM 维护，每次 ingest 后自动更新。
>
> Last updated: 2026-05-27 | Total pages: ~403 | Module indexes: 25

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
| [[kernel-books-index]] | Linux/Kernel书籍索引：内核/TLPI/APUE/CSAPP/网络/并发 (9 books) | 3 |
| [[ebpf-index]] | XDP, TC, Cilium, Falco, CO-RE, eBPF ecosystem, saBPF, Security Observability, 10 papers | 7 |

### Embedded Network
| Index | Domain | Entities |
|-------|--------|----------|
| [[lwip-index]] | lwIP embedded TCP/IP stack: netif, pbuf, memory, IPv4, TCP, UDP, IGMP, DHCP, VLAN dispatch | 27 |
| [[lwip-source-index]] | lwIP core source reference: ip4.c, tcp.c, udp.c, pbuf.c, netif.c — 函数索引、数据结构、调用链 | 5 |
| [[lwfw-index]] | SafeOS LWFW firewall: 5-tuple, LWCT, dual filter engines, seL4 IPC, VLAN isolation | 26 |
| [[safeos-index]] | SafeOS NSv architecture: NSv Network Server, CMA/elem-ring, AF-PACKET/TPACKET, ABI boundary, analysis plan | 6 |

### SafeOS LWFW
| Index | Domain | Entities |
|-------|--------|----------|
| [[lwfw-index]] | LWFW module index: architecture, classification, filtering, LWCT, parsing, IPC, agent, VLAN, optimization | 26 |

### Emulation
| Index | Domain | Entities |
|-------|--------|----------|
| [[qemu-index]] | QOM, memory, CPU, migration, block layer | 5 |

### Operating System
| Index | Domain | Entities |
|-------|--------|----------|
| [[os-index]] | Process/thread, virtual memory, I/O models, Linux subsystems | 7 |
| [[arm-index]] | ARMv8-A, Cortex-A9, TrustZone/OP-TEE, computer architecture | 4 |

### Programming & Algorithms
| Index | Domain | Entities |
|-------|--------|----------|
| [[datastructure-index]] | DSA: complexity, linear, sorting, DP, recursion, hash, trees | 7 |
| [[design-patterns-index]] | SOLID, creational, structural, behavioral | 5 |
| [[interview-index]] | Coding patterns, system design basics | 3 |
| [[cpp-index]] | Modern C++ (C++11-20), STL containers/algorithms/iterators, serialization | 22 |
| [[cpp-modern-index]] | Modern C++ Skills (C++17+Master): 13 C++17 skills + 15 Master mental models | 28 |
| [[cpp-books-index]] | C++ Books: Modern/Templates/Concurrency/Performance/Memory/Design (16 PDFs) | 14 |
| [[cpp-modern-index]] | C++ Conference Talks (Batch N, 21 talks): Bjarne/安全/AI推理/编译器/RISC-V/嵌入式/AI Coding/异构计算 | 37 |
| [[rust-index]] | Rust language: ownership, borrowing, lifetimes, traits, concurrency | 1 |
| [[sys-prog-index]] | C/C++, Linux, middleware, security | 4 |
| [[math-index]] | 非线性动力学与混沌 | 1 |
| [[se-index]] | 人月神话、项目管理、软件架构 | 1 |

### Security
| Index | Domain | Entities |
|-------|--------|----------|
| [[security-index]] | 商用密码(SM2/3/4)、mbedtls、TLS/DTLS、PKI | 2 |

### C++ Frameworks & Libraries
| Index | Domain | Entities |
|-------|--------|----------|
| [[workflow-index]] | Sogou Workflow async engine: HTTP/Redis/MySQL/Kafka/DNS | 28 |
| [[cpp-index]] | Modern C++ (C++11-20), STL containers/algorithms/iterators, serialization | 22 |
| [[cpp-modern-index]] | Modern C++ Skills (C++17+Master): 13 C++17 skills + 15 Master mental models | 28 |

### Tools & BMC
| Index | Domain | Entities |
|-------|--------|----------|
| [[tools-index]] | tcpdump, netcat, masscan, nmap | 2 |
| [[openbmc-index]] | IPMI, Redfish, boot/firmware update, hardware control | 4 |

---

## Sources

| 来源 | 描述 | 日期 | 类型 |
|------|------|------|------|
| [[sources/notes-net-deep]] | 网络深度笔记合并：skbuff/NAT/路由 Trie/PHY-MAC/Conntrack/全栈路径 | 2026-05 | github |
| [[sources/safeos-lwip-core]] | SafeOS lwIP 核心网络协议分析 (~28篇)：netif/pbuf/TCP/UDP/IGMP/DHCP/VLAN | 2026-05 | github |
| [[sources/safeos-lwfw]] | SafeOS LWFW 防火墙分析 (27篇)：架构/过滤/LWCT/解析/事件/IPC/Agent/VLAN/优化 | 2026-05 | github |
| [[sources/safeos-lwip-extensions]] | SafeOS lwIP 扩展/集成分析 (19篇)：LWFW/CMA/elem_ring/AF-PACKET/seL4 IPC/VIRT_BRG | 2026-05 | github |
| [[sources/safeos-architecture]] | SafeOS NSv 架构设计文档 (7篇)：9阶段分析计划/NSv深度分析/AF-PACKET设计/VDF nids关系 | 2026-05 | github |
| [[sources/notes-network-fundamentals]] | Linux 网络协议实现笔记（~78 .md 文件）| 2026-05 | github |
| [[sources/notes-net]] | Linux 内核网络子系统深度分析：Socket/sk_buff/Netdevice/Routing/Netfilter/TCP/UDP | 2026-05 | github |
| [[sources/notes-network]] | Linux 网络协议笔记：TCP/IP、IPv4/IPv6、BPF/XDP、桥接、路由、性能优化 | 2026-05 | github |
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
| [[sources/pdf-cpp-slides]] | C++ Conference Talks Batch N (21 talks)：Bjarne/安全/AI推理(RTP-LLM/Mooncake/xLLM)/编译器(RISC-V/MLIR)/嵌入式/AI Coding/异构计算 | 2026-05 | pdf |
| [[sources/pdf-cpp-ai-inference]] | AI推理与MLIR编译优化：RTP-LLM(阿里)、xLLM、DeepSeek SGLang优化、MLIR Actor编译器 | 2026-05 | pdf |
| [[sources/pdf-cpp-compiler-toolchain]] | 编译器与工具链：MLIR fuzzing、RISC-V AI编译器、多元AI算子库、编译技术在AI软件栈的实践 | 2026-05 | pdf |
| [[sources/pdf-cpp-perf-engineering]] | 高性能C++工程：缓存/分布式计算加速、内核Btree块缓存、异构传输库优化 | 2026-05 | pdf |
| [[sources/pdf-cpp-safety-standards]] | C++安全标准与安全优先演进：安全开发路线图、AI原生研发成熟度 | 2026-05 | pdf |
| [[sources/pdf-cpp-engineering-practices]] | C++工程实践：C++在Xiaomi Vela(嵌入式)、统一算力FlagScale/FlagOS、CodeBuddy终端、具身机器人多仓构建、AI重塑测试 | 2026-05 | pdf |
| [[sources/pdf-ebpf-books]] | eBPF书籍3册：龙蜥白皮书(XDP/TC/CO-RE)、技术实践、Cilium创始人Liz Rice入门 | 2026-05 | pdf |
| [[sources/pdf-ebpf-papers]] | eBPF论文10篇：Thomas Graf微内核、微服务感知OS、Apple Falco、Google KRSI、Rootkit攻防、UFMG XDP、生态库、saBPF容器审计、Isovalent安全可观测性、PTPsec | 2026-05 | pdf |
| [[sources/pdf-bpf-rethinking-kernel]] | Rethinking Linux Kernel (Thomas Graf 2020)：eBPF微内核+可组合服务层愿景 | 2020 | pdf |
| [[sources/pdf-bpf-microservices-os]] | BPF Microservices-aware OS (Thomas Graf 2018)：Cilium/Hubble功能矩阵/Service Mesh加速 | 2018 | pdf |
| [[sources/pdf-google-bpf-audit]] | BPF Security Auditing at Google (Brendan Jackman)：KRSI BPF LSM/Atomics原子/Ringbuf promise/CO-RE | 2021 | pdf |
| [[sources/pdf-falco-apple]] | Falco at Apple (eBPF Summit 2021)：BPF vs内核模块优势/LSM hook/高价值Syscall监控列表 | 2021 | pdf |
| [[sources/pdf-ebpf-library-ecosystem]] | eBPF Library Ecosystem (Kyle Quest)：Go/Rust/Python/C生态库：BCC/libbpf/cilium-ebpf/aya全面评测 | 2021 | pdf |
| [[sources/pdf-xdp-fast-packet]] | XDP Fast Packet Processing (UFMG)：BPF指令格式详解/~20Mpps性能/XDP Actions部署 | 2021 | pdf |
| [[sources/pdf-infocom-ptpsec]] | PTPsec (INFOCOM 2024)：IEEE 1588时间同步循环路径不对称分析/静态增量延迟攻击缓解 | 2024 | pdf |
| [[sources/pdf-ptp-security]] | PTPsec：IEEE 1588时间同步延迟攻击检测与缓解 (INFOCOM 2024) | 2024 | pdf |
| [[sources/pdf-cpp-templates]] | C++ Templates 2nd Edition：模板权威指南（范德沃尔德/约祖蒂斯/格雷戈）| 2017 | pdf |
| [[sources/pdf-cpp-nginx-module]] | Nginx模块开发指南：C++11 + Boost 扩展Nginx | 2015 | pdf |
| [[sources/pdf-crypto-books]] | [DEPRECATED → pdf-security-crypto-books] OpenSSL Cookbook + 图解密码技术 | 2024 | pdf |
| [[sources/pdf-cpp-modern-books]] | Modern C++ 合集 6册：C++20/23、Professional C++、21st Century C++、Modern C、C++17、Large-Scale C++ | 2024 | pdf |
| [[sources/pdf-cpp-templates-books]] | C++ Templates 合集 3册：完整指南 + 模板元编程实战 | 2023 | pdf |
| [[sources/pdf-cpp-perf-memory]] | C++ 性能与内存管理 4册：内存管理高级指南、性能优化指南、Cache 内存 | 2025 | pdf |
| [[sources/pdf-cpp-concurrency]] | C++ 并发编程 2册：Concurrency with Modern C++ + C++ Concurrency in Action | 2023 | pdf |
| [[sources/pdf-cpp-perf-books]] | C++性能优化与架构2册：Optimized C++ (string/algorithm/memory优化) + Large-Scale C++ Software Design (物理设计/组件/层级) | 2016-2019 | pdf |
| [[sources/pdf-c-language]] | C 语言编程 2册：K&R C 第2版 + C in a Nutshell 第2版 | 2015 | pdf |
| [[sources/pdf-the-linux-programming-interface]] | TLPI (Michael Kerrisk, 1556页)：Linux/UNIX系统编程百科，500+系统调用，64章节覆盖进程/线程/内存/IPC/网络 | 2026-05 | pdf |
| [[sources/pdf-unix-environment-advanced-programming]] | APUE 第三版 (Stevens & Rago, 822页)：UNIX环境高级编程，POSIX标准系统编程经典（扫描版） | 2026-05 | pdf |
| [[sources/pdf-computer-systems-programmers-perspective]] | CS:APP (Bryant & O'Hallaron, 1078页)：计算机系统程序员视角，机器码/缓存/虚拟内存/链接/并发，CMU 15-213 教材 | 2026-05 | pdf |
| [[sources/pdf-linux-sysprog]] | Linux系统编程4册：TLPI+APUE+Unix工具+CSAPP深入理解计算机系统 | 2026-05 | pdf |
| [[sources/pdf-linux-kernel-books]] | Linux内核2册：深入理解Linux内核(架构)+Linux内核0.12完全注释 | 2026-05 | pdf |
| [[sources/pdf-linux-net-server]] | Linux网络/服务端3册：高性能服务器+muduo多线程编程+LwIP协议栈源码 | 2026-05 | pdf |
| [[sources/pdf-concurrency-perf]] | 并发与并行编程2册：OSTEP线程锁+perfbook(Paul McKenney RCU/无锁同步) | 2026-05 | pdf |
| [[sources/pdf-design-patterns-cpp]] | GoF 23种设计模式精解附C++实现源码 | 2026-05 | pdf |
| [[sources/pdf-ds-cpp]] | 数据结构C++语言版(第3版·清华大学邓俊辉)：向量/树/图/排序/串匹配 | 2026-05 | pdf |
| [[sources/pdf-rust-intro]] | Rust 合集 3册：入门指北 + Programming Rust 2nd Ed + Rust 编程语言（官方中文版）| 2024 | pdf |
| [[sources/pdf-af-xdp-quic]] | B站 AF_XDP with QUIC 实践：QUIC网关性能优化 | 2024 | pdf |
| [[sources/pdf-someip-docs]] | SOME/IP & vSOME/IP 技术文档6篇：CommonAPI/Franca/SD/Endpoints | 2024 | pdf |
| [[sources/notes-ccpp]] | C/C++ 技术笔记：序列化、智能指针深度分析、堆栈对象创建策略、移动语义 | 2026-05 | github |
| [[sources/cpp-modern-skills]] | Modern C++ Skills (C++17+Master): 26 skills covering ownership, templates, type-driven design, error handling, concurrency, DDD, performance, ecosystem, lifecycle | 2026-05 | github |
| [[sources/notes-datastructure]] | 数据结构与算法：复杂度分析、线性结构、排序、DP、递归、哈希表、树与图（21章节+真题训练） | 2026-05 | github |
| [[sources/notes-design-patterns]] | 设计模式：SOLID原则、创建型5种、结构型7种、行为型11种共23种设计模式 | 2026-05 | github |
| [[sources/notes-interview]] | 面试准备：方法论、问题解决模式、系统设计基础、NP完全性、位操作、进阶数据结构 | 2026-05 | github |
| [[sources/notes-midware]] | 中间件：DoIP协议（ISO 13400）、SOME/IP服务通信、vSOME/IP开源实现 | 2026-05 | github |
| [[sources/notes-security]] | 安全工具：Masscan高速端口扫描、Falco K8s运行时安全、Snort 3 NIDS架构分析 | 2026-05 | github |
| [[sources/workflow-engine]] | Sogou Workflow C++ 异步引擎：架构核心17篇+教程18篇，13种协议支持 | 2026-05 | github |
| [[sources/notes-sys]] | 系统编程：TTY/Shell/Console体系、ELF文件格式、Linux IPC、单例模式 | 2026-05 | github |
| [[sources/pdf-algo-ds-books]] | 算法与数据结构7册：Sedgewick图算法、TAOCP Vol.1、邓俊辉数据结构、基础集合论 | 2026-05 | pdf |
| [[sources/pdf-interview-books]] | 编程面试2册：Cracking the Coding Interview 6th + EPI | 2026-05 | pdf |
| [[sources/pdf-algorithms-books]] | 算法与面试书籍合集8册：Sedgewick算法+图算法卷、Goodrich DS&A 2nd+3rd、Knuth TAOCP、石田算法书、CTCI 6th、EPI | 2026-05 | pdf |
| [[sources/pdf-epi-python]] | Python编程面试书：DS&A (数组/链表/树/图/哈希)、设计问题、OOD、Python 3实现 | 2017 | pdf |
| [[sources/pdf-security-crypto-books]] | 安全与密码学6册：Bulletproof TLS/PKI、mbedtls、TrustZone/OP-TEE、商用密码考核 | 2026-05 | pdf |
| [[sources/pdf-security-crypto-books-updated]] | 安全与密码学更新3册：mbedtls开发实战、OpenSSL攻略、Bulletproof TLS/PKI | 2026-05 | pdf |
| [[sources/pdf-security-papers-ebpf]] | eBPF安全论文3篇：Rootkit攻防(2024)、Apple Falco运行时检测(2021)、Google KRSI审计 | 2021-2024 | pdf |
| [[sources/pdf-isovalent-security-observability]] | Isovalent O'Reilly报告：eBPF Four Golden Signals云原生安全可观测性(Cilium/Hubble) | 2022 | pdf |
| [[sources/pdf-sabpf-container-audit]] | saBPF SoCC 2021论文：eBPF容器级LSM审计，零内核修改，provenance追踪 | 2021 | pdf |
| [[sources/pdf-arm-architecture]] | ARM体系结构4册：Armv8/Armv9参考手册、Cortex-A9 TRM、量化研究方法 | 2026-05 | pdf |
| [[sources/pdf-misc-books]] | 杂项3册：人月神话、非线性动力学与混沌、偏微分方程 | 2026-05 | pdf |
| [[sources/pdf-remaining-books]] | 剩余书籍汇总 Batch O（38册）：C基础/嵌入式/ARM/Rust/数学/软件工程/其他 | 2026-05 | pdf |
| [[sources/pdf-security-crypto-books-updated]] | 安全与密码学更新3册：mbedtls开发实战、OpenSSL攻略、Bulletproof TLS/PKI | 2026-05 | pdf |
| [[sources/pdf-cpp-bjarne-40years]] | Bjarne Stroustrup C++ 40年演讲：成功因素/AI时代定位/C++26方向 | 2026-05 | pdf |
| [[sources/pdf-mlir-fuzzing]] | MLIR编译器模糊测试：覆盖率引导fuzzing发现pass间/跨dialect bug | 2026-05 | pdf |
| [[sources/pdf-ai-compiler-stack]] | AI编译器软件栈：SigInfer推理引擎/国产卡CUDA兼容/AI编译器自动生成 | 2026-05 | pdf |
| [[sources/pdf-xllm-inference]] | xLLM大模型推理引擎C++实现：PD/EPD分离/电商场景/DAG调度/KVCache优化 | 2026-05 | pdf |
| [[sources/pdf-riscv-ai-compiler]] | RISC-V大模型推理AI编译器：软硬件协同/V扩展/代价模型/自动调优 | 2026-05 | pdf |
| [[sources/pdf-rtp-llm]] | RTP-LLM阿里推理引擎：MoE专家模型/投机采样/分布式架构/未来展望 | 2026-05 | pdf |
| [[sources/pdf-mooncake]] | Mooncake解耦式LLM推理：KVCache Pool分层/以存换算/vLLM兼容 | 2026-05 | pdf |
| [[sources/pdf-flagscale]] | FlagScale训练推理框架：FlagCX统一通信/FlagOS跨AI芯片生态 | 2026-05 | pdf |
| [[sources/pdf-llm-edge-storage]] | 端侧大模型部署：AIOS架构/存储挑战/分层KVCache/计算存储融合 | 2026-05 | pdf |
| [[sources/pdf-book-modern-cpp]] | The Book of Modern C++ 第二版：1053页多人合著C++20/23高级主题 | 2024 | pdf |
| [[sources/pdf-trustzone-optee]] | TrustZone与OP-TEE技术详解：786页ARM硬件安全扩展权威著作 | 2018 | pdf |
| [[sources/pdf-commercial-crypto-assessment]] | 商用密码评估考核题：622页SM算法/密评流程/等级保护2.0 | 2023 | pdf |
| [[sources/pdf-openssl-cookbook]] | OpenSSL Cookbook中文版：72页密钥生成/证书管理/SSL测试/漏洞检测 | 2015 | pdf |
| [[sources/pdf-ebpf-technical-practice]] | eBPF技术实践v2（龙蜥社区）：100页开发流程/工具链/应用场景 | 2023 | pdf |
| [[sources/pdf-ebpf-basics]] | eBPF基础：80页入门/CO-RE/BTF/Maps/Pinning机制/11个64位寄存器 | 2023 | pdf |
| [[sources/pdf-computer-architecture-hp]] | H&P计算机体系结构量化研究方法（第五版）：612页体系结构圣经 | 2017 | pdf |
| [[sources/pdf-onedrive-batch1]] | OneDrive Batch P (5 PDFs): OS concepts + C++ concurrency/high-performance/templates-v2 | 2026-05 | pdf |

---

## Synthesis

| 主题 | 描述 | 日期 |
|------|------|------|
| [[synthesis/topic-os-fundamentals]] | 操作系统基础综合：进程/线程、内存管理、文件系统、网络、并发 | 2026-05 |
| [[synthesis/topic-network-fundamentals]] | 计算机网络基础综合：TCP/IP 五层模型、Socket 编程、HTTP 缓存、安全 | 2026-05 |

---

## Journal

> 待补充
