---
type: index
created: 2026-05-22
---

# LLM Wiki

> **~95 pages. 15 module indexes.**
> Each module index acts as a sub-hub in the Obsidian graph view.

## Module Indexes

### Linux Kernel
| Index | Domain |
|-------|--------|
| [[wiki/kernel-virt-index]] | KVM, Virtio virtualization |
| [[wiki/kernel-io-index]] | io_uring, VFS |
| [[wiki/kernel-net-index]] | Socket/sk_buff, Netfilter, TCP/IP protocols |
| [[wiki/kernel-protocols-index]] | Protocol details, full-stack path, PHY/MAC layer |
| [[wiki/kernel-mm-index]] | SLUB, page fault, swap, page reclaim, mmap |
| [[wiki/kernel-sched-index]] | CFS, context switch, load balancing |
| [[wiki/kernel-block-index]] | bio/request, blk-mq, IO schedulers |
| [[wiki/kernel-subsystems-index]] | Crypto, locking, IPC, RCU, time, sound |
| [[wiki/kernel-books-index]] | Linux/Kernel书籍索引：内核/TLPI/APUE/CSAPP/网络/并发 (9 books) |
| [[wiki/ebpf-index]] | XDP, TC, Cilium, Falco, CO-RE, eBPF ecosystem |

### Emulation
| Index | Domain |
|-------|--------|
| [[wiki/qemu-index]] | QOM, memory, CPU, migration, block layer |

### Operating System
| Index | Domain |
|-------|--------|
| [[wiki/os-index]] | Process/thread, virtual memory, I/O models, Linux subsystems |

### Programming & Algorithms
| Index | Domain |
|-------|--------|
| [[wiki/datastructure-index]] | DSA: arrays, sorting, DP, trees, graphs |
| [[wiki/design-patterns-index]] | SOLID, creational, structural, behavioral |
| [[wiki/interview-index]] | Coding patterns, system design basics |
| [[wiki/cpp-index]] | Modern C++ (C++11-20), STL containers/algorithms |
| [[wiki/sys-prog-index]] | C/C++, Linux, middleware, security |

### C++ Frameworks & Libraries
| Index | Domain |
|-------|--------|
| [[wiki/workflow-index]] | Sogou Workflow async engine: HTTP/Redis/MySQL/Kafka/DNS |
| [[wiki/cpp-index]] | Modern C++ (C++11-20), STL containers/algorithms |

### Tools & BMC
| Index | Domain |
|-------|--------|
| [[wiki/tools-index]] | tcpdump, netcat, masscan, nmap |
| [[wiki/openbmc-index]] | IPMI, Redfish, boot/firmware update, hardware control |

### Snort3 IDS/IPS
| Index | Domain |
|-------|--------|
| [[wiki/entities/linux/snort3/snort3-framework]] | Plugin system, lifecycle, pig, shell |
| [[wiki/entities/linux/snort3/snort3-actions]] | Rule actions |
| [[wiki/entities/linux/snort3/snort3-connectors]] | Service connectors (TCP/UDP/file/popen) |
| [[wiki/entities/linux/snort3/snort3-events-filters]] | Event generation, 3-layer filter architecture |
| [[wiki/entities/linux/snort3/snort3-flow]] | Flow tracking |
| [[wiki/entities/linux/snort3/snort3-ips-options]] | IPS options |
| [[wiki/entities/linux/snort3/snort3-infrastructure]] | Hash tables, file_api, decompress, js_norm, helpers |
| [[wiki/entities/linux/snort3/snort3-control-startup]] | Control and startup |

## Sources
| Source | Description |
|--------|-------------|
| [[wiki/sources/notes-net-deep]] | 网络深度笔记：skbuff/NAT/路由 Trie/PHY-MAC/Conntrack/全栈 |
| [[wiki/sources/notes-network-fundamentals]] | Linux 网络协议实现笔记 |
| [[wiki/sources/notes-netfilter]] | Linux Netfilter/iptables/nftables/conntrack |
| [[wiki/sources/notes-os]] | Linux 内核深度分析：VFS、调度器、SLUB、cgroups |
| [[wiki/sources/notes-os-fundamentals]] | 操作系统基础：进程/线程、内存管理、文件系统、IO模型 |
| [[wiki/sources/notes-qemu]] | QEMU 模拟器架构：TCG、QOM、KVM 集成、块设备 |
| [[wiki/sources/notes-overview]] | Sphinx 技术笔记索引页 |
| [[wiki/sources/notes-kernel]] | Linux 内核各子系统深度分析 |
| [[wiki/sources/notes-kernel-crypto]] | Linux 内核密码学子系统 |
| [[wiki/sources/notes-kernel-ipc]] | Linux 内核 IPC 子系统 |
| [[wiki/sources/notes-kernel-locking]] | Linux 内核锁子系统 |
| [[wiki/sources/notes-kernel-rcu]] | Linux 内核 RCU |
| [[wiki/sources/notes-kernel-sound]] | Linux 内核声音子系统 |
| [[wiki/sources/notes-kernel-time]] | Linux 内核时间子系统 |
| [[wiki/sources/notes-tools]] | 工具使用笔记：tcpdump、netcat、masscan/nmap |
| [[wiki/sources/notes-openbmc]] | OpenBMC 深度技术分析 |
| [[wiki/sources/pdf-cpp-modern-tutorial]] | Modern C++ Tutorial (C++11/14/17/20) |
| [[wiki/sources/pdf-cpp-effective-stl]] | Effective STL (Scott Meyers) |
| [[wiki/sources/pdf-ebpf-books]] | eBPF书籍3册: 龙蜥白皮书+技术实践+Liz Rice入门 |
| [[wiki/sources/pdf-ebpf-papers]] | eBPF论文10篇: Thomas Graf微内核愿景+微服务感知OS+Apple Falco+Google KRSI+Black Hat Rootkit+UFMG XDP+生态库+saBPF容器审计+Isovalent安全可观测性+PTPsec |
| [[wiki/sources/workflow-engine]] | Sogou Workflow C++ 异步引擎：架构核心17篇+教程18篇，13种协议支持 |
| [[wiki/sources/notes-ccpp]] | C/C++ 技术笔记：序列化、智能指针、堆栈对象创建、移动语义 |
| [[wiki/sources/github-modern-cpp-features]] | Modern C++ Features Reference (C++11/14/17/20/23)：AnthonyCalandra 100+ features with examples |
| [[wiki/sources/notes-datastructure]] | 数据结构与算法：复杂度、线性结构、排序、DP、递归、哈希表、树与图 |
| [[wiki/sources/notes-design-patterns]] | 设计模式：SOLID、创建型5种、结构型7种、行为型11种共23种 |
| [[wiki/sources/notes-interview]] | 面试准备：方法论、问题解决模式、系统设计基础、NP完全性、位操作 |
| [[wiki/sources/notes-midware]] | 中间件：DoIP协议（ISO 13400）、SOME/IP服务通信、vSOME/IP开源实现 |
| [[wiki/sources/notes-security]] | 安全工具：Masscan高速端口扫描、Falco K8s安全监控、Snort 3 NIDS |
| [[wiki/sources/github-snort3-infrastructure]] | Snort3 infrastructure: hash/XHash/ZHash, file_api, decompress, js_norm |
| [[wiki/sources/notes-sys]] | 系统编程：TTY/Shell/Console体系、ELF文件格式、Linux IPC |
| [[wiki/sources/pdf-the-linux-programming-interface]] | TLPI (Kerrisk, 1556页)：Linux/UNIX系统编程百科，500+系统调用 |
| [[wiki/sources/pdf-unix-environment-advanced-programming]] | APUE 第三版 (Stevens & Rago, 822页)：UNIX环境高级编程（扫描版）|
| [[wiki/sources/pdf-computer-systems-programmers-perspective]] | CS:APP (Bryant & O'Hallaron, 1078页)：计算机系统程序员视角，CMU 15-213 |
| [[wiki/sources/pdf-onedrive-batch1]] | OneDrive Batch P: OS concepts + C++ concurrency/high-performance/templates-v2 |
| [[wiki/sources/pdf-slides]] | C++ & Compiler Slides: 58 conference talks in 6 categories |
| [[wiki/sources/pdf-slides-cpp-standard]] | C++ Slides: 语言演进/标准化/反射/对象生命周期/嵌入式 (8 talks) |
| [[wiki/sources/pdf-slides-ai-coding]] | C++ Slides: AI Coding Agent/Coding/安全防御 (6 talks) |
| [[wiki/sources/pdf-slides-ai-compiler]] | C++ Slides: AI Compiler/MLIR/RISC-V生态 (5 talks) |
| [[wiki/sources/pdf-slides-llm-inference]] | C++ Slides: LLM推理/Mooncake/xLLM/DeepSeek/FlagScale/异构计算 (11 talks) |
| [[wiki/sources/pdf-slides-kernel]] | C++ Slides: Linux Kernel/调试/Btree/Kernel-bypass (4 talks) |
| [[wiki/sources/pdf-slides-tools]] | C++ Slides: EPI面试/Python刷题/Qoder CLI (2 talks) |
| [[wiki/sources/pdf-cpp-bjarne-40years]] | Bjarne Stroustrup C++ 40年演讲：成功因素、AI时代定位、C++26方向 |
| [[wiki/sources/pdf-mlir-fuzzing]] | MLIR编译器模糊测试：覆盖率引导fuzzing发现pass间bug |
| [[wiki/sources/pdf-ai-compiler-stack]] | AI编译器软件栈：SigInfer推理引擎/国产卡CUDA兼容/AI编译器自动生成 |
| [[wiki/sources/pdf-xllm-inference]] | xLLM大模型推理引擎：PD分离/EPD解耦/C++全栈/DAG调度 |
| [[wiki/sources/pdf-riscv-ai-compiler]] | RISC-V大模型推理AI编译器：软硬件协同设计/V扩展/代价模型 |
| [[wiki/sources/pdf-rtp-llm]] | RTP-LLM阿里大模型推理引擎：MoE专家模型/投机采样/分布式架构 |
| [[wiki/sources/pdf-mooncake]] | Mooncake解耦式大模型推理：KVCache Pool分层存储/以存换算 |
| [[wiki/sources/pdf-flagscale]] | FlagScale大模型训练推理框架：FlagCX统一通信库/FlagOS生态 |
| [[wiki/sources/pdf-llm-edge-storage]] | 端侧大模型部署：AIOS架构/存储系统挑战/KVCache分层 |
| [[wiki/sources/pdf-book-modern-cpp]] | The Book of Modern C++ 第二版：1053页多人合著C++20/23高级主题 |
| [[wiki/sources/pdf-trustzone-optee]] | TrustZone与OP-TEE技术详解：786页ARM硬件安全扩展权威著作 |
| [[wiki/sources/pdf-commercial-crypto-assessment]] | 商用密码应用安全性评估考核题：622页SM算法/密评/等级保护2.0 |
| [[wiki/sources/pdf-openssl-cookbook]] | OpenSSL Cookbook中文版：72页密钥生成/证书管理/SSL测试实用手册 |
| [[wiki/sources/pdf-ebpf-technical-practice]] | eBPF技术实践v2（龙蜥社区）：100页XDP/TC/CO-RE工具链 |
| [[wiki/sources/arthurchiao-linux-cpu-power-management]] | Linux CPU power management: P-states, C-states, TDP, hyperthreading |
| [[wiki/sources/arthurchiao-linux-net-stack]] | Linux network stack overview: IRQ/softirq, RX/TX, BPF/XDP, monitoring |
| [[wiki/sources/arthurchiao-linux-net-stack-implementation-rx]] | Linux network RX implementation: NAPI, DMA ring buffer, 9-stage pipeline |
| [[wiki/sources/arthurchiao-linux-net-stack-tuning-rx]] | Linux network RX tuning: ethtool, RSS, RPS, GRO, softirq budget |
| [[wiki/sources/arthurchiao-linux-irq-softirq]] | Linux IRQ/softirq: hard IRQ, softirq subsystem, tasklets, workqueues |
| [[wiki/sources/arthurchiao-bbr-paper]] | BBR congestion control: BtlBw/RTprop measurement, zero queue operation |
| [[wiki/sources/arthurchiao-facebook-xdp-to-socket]] | Facebook XDP/eBPF: Katran L4 LB, Maglev hashing, bpf_sk_reuseport |
| [[wiki/sources/arthurchiao-pki]] | PKI and certificates: CA hierarchy, trust stores, mTLS, certificate chain |
| [[wiki/sources/arthurchiao-modern-lb-proxy]] | Modern load balancing: L4 vs L7, topology, ECMP, service mesh |
| [[wiki/sources/arthurchiao-tc-da-mode]] | TC eBPF direct-action mode: clsact, action verdicts, cls_bpf filter |
| [[wiki/sources/arthurchiao-conntrack-design]] | Conntrack design: netfilter hooks, two-phase creation, NAT dependency |
| [[wiki/sources/arthurchiao-sockmap-ebpf]] | eBPF sockmap: socket redirection bypassing TCP/IP stack, sockops/sk_msg |
| [[wiki/sources/pdf-ebpf-basics]] | eBPF基础：80页入门/11个64位寄存器/CO-RE/BTF/Pinning机制 |
| [[wiki/sources/pdf-computer-architecture-hp]] | Hennessy & Patterson计算机体系结构量化研究方法（第五版）612页 |

## Synthesis
| Topic | Description |
|-------|-------------|
| [[wiki/synthesis/topic-os-fundamentals]] | OS fundamentals synthesis |
| [[wiki/synthesis/topic-network-fundamentals]] | Network fundamentals synthesis |
